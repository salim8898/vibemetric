"""
Vibemetric CLI - AI Code Detection Tool

Command-line interface for scanning repositories and detecting AI-generated code.
"""

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .detectors.artifact_detector import ArtifactDetector
from .detectors.ml_detector import MLDetector
from .detectors.pattern_detector import PatternDetector
from .detectors.velocity_analyzer import VelocityAnalyzer
from .formatters import SARIFFormatter
from .integrations import PRAnalyzer
from .integrations.github_client import GITHUB_AVAILABLE, GitHubClient
from .models import DetectionLayerType, DetectionSignal
from .profiles import DeveloperProfiler
from .reports import TeamReporter
from .scorer import Scorer

console = Console()


def scan_repository(repo_path: str, sample_size: int = 10, verbose: bool = False) -> dict:
    """
    Scan repository with all 4 detection layers.

    Args:
        repo_path: Path to repository
        sample_size: Number of files to sample for pattern/ML detection
        verbose: Show detailed progress

    Returns:
        Dictionary with scan results
    """
    repo_path_obj = Path(repo_path)

    if not repo_path_obj.exists():
        console.print(f"[red]Error: Repository path does not exist: {repo_path}[/red]")
        sys.exit(1)

    results = {
        "repository": str(repo_path_obj.absolute()),
        "signals": [],
        "vibe_score": None,
        "artifacts": [],
        "velocity_metrics": {},
        "pattern_results": [],
        "ml_results": [],
    }

    # 1. Artifact Detection
    if verbose:
        console.print("\n[cyan]Running Artifact Detector...[/cyan]")

    artifact_detector = ArtifactDetector(repo_path)
    artifacts = artifact_detector.detect()
    artifact_signal = artifact_detector.get_detection_signal(artifacts)

    results["artifacts"] = [
        {
            "tool": a.tool_name,
            "file": a.file_path,
            "adoption_date": a.adoption_date.isoformat() if a.adoption_date else None,
            "authors": a.authors,
        }
        for a in artifacts
    ]
    results["signals"].append(artifact_signal)

    # 2. Velocity Analysis
    if verbose:
        console.print("[cyan]Running Velocity Analyzer...[/cyan]")

    velocity_analyzer = VelocityAnalyzer(repo_path)
    velocity_metrics = velocity_analyzer.analyze()
    velocity_signal = velocity_analyzer.get_detection_signal(velocity_metrics)

    results["velocity_metrics"] = {
        "spike_detected": velocity_metrics["spike_detected"],
        "baseline_velocity": velocity_metrics["baseline_velocity"],
        "current_velocity": velocity_metrics["current_velocity"],
        "velocity_increase": velocity_metrics["velocity_increase"],
        "spike_date": velocity_metrics["spike_date"].isoformat()
        if velocity_metrics["spike_date"]
        else None,
    }
    results["signals"].append(velocity_signal)

    # 3. Pattern Detection
    if verbose:
        console.print("[cyan]Running Pattern Detector...[/cyan]")

    pattern_detector = PatternDetector()
    python_files = _find_python_files(repo_path_obj)

    pattern_results = []
    for file_path in python_files[:sample_size]:
        try:
            signal = pattern_detector.analyze_file(str(file_path))
            pattern_results.append((file_path.name, signal))
        except Exception:
            pass

    if pattern_results:
        avg_pattern_score = sum(s.score for _, s in pattern_results) / len(pattern_results)
        avg_pattern_confidence = sum(s.confidence for _, s in pattern_results) / len(
            pattern_results
        )

        pattern_signal = DetectionSignal(
            layer_type=DetectionLayerType.PATTERN,
            score=avg_pattern_score,
            confidence=avg_pattern_confidence,
            evidence=[f"Analyzed {len(pattern_results)} files"],
            metadata={"file_count": len(pattern_results)},
        )
        results["signals"].append(pattern_signal)

        results["pattern_results"] = [
            {
                "file": filename,
                "score": signal.score,
                "confidence": signal.confidence,
                "patterns": signal.metadata.get("pattern_count", 0),
            }
            for filename, signal in pattern_results
        ]

    # 4. ML Detection
    if verbose:
        console.print("[cyan]Running ML Detector...[/cyan]")

    ml_detector = MLDetector()

    if ml_detector.model_available:
        ml_results = []
        for file_path in python_files[:sample_size]:
            try:
                signal = ml_detector.analyze_file(str(file_path))
                ml_results.append((file_path.name, signal))
            except Exception:
                pass

        if ml_results:
            avg_ml_score = sum(s.score for _, s in ml_results) / len(ml_results)
            avg_ml_confidence = sum(s.confidence for _, s in ml_results) / len(ml_results)

            ml_signal = DetectionSignal(
                layer_type=DetectionLayerType.ML,
                score=avg_ml_score,
                confidence=avg_ml_confidence,
                evidence=[f"ML analyzed {len(ml_results)} files"],
                metadata={"file_count": len(ml_results)},
            )
            results["signals"].append(ml_signal)

            results["ml_results"] = [
                {
                    "file": filename,
                    "score": signal.score,
                    "confidence": signal.confidence,
                    "prediction": "AI" if signal.score > 50 else "Human",
                }
                for filename, signal in ml_results
            ]

    # Calculate combined score
    scorer = Scorer()
    vibe_score = scorer.calculate_vibe_score(results["signals"])

    results["vibe_score"] = {
        "overall_score": vibe_score.overall_score,
        "confidence": vibe_score.confidence,
        "ai_assistance_level": vibe_score.ai_assistance_level.value,
        "interpretation": scorer.get_interpretation(vibe_score),
        "recommendations": scorer.get_recommendations(vibe_score),
    }

    return results


def _find_python_files(repo_path: Path) -> list[Path]:
    """Find Python files excluding tool-generated ones."""
    EXCLUDE_DIRS = {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        ".nox",
        "node_modules",
        "venv",
        "env",
        ".venv",
        ".env",
        "build",
        "dist",
        ".egg-info",
        ".eggs",
        "htmlcov",
        ".coverage",
        ".git",
        ".svn",
        ".hg",
        "migrations",
        "alembic",
    }

    EXCLUDE_PATTERNS = {
        "*_pb2.py",
        "*_pb2_grpc.py",
        "setup.py",
        "version.py",
        "__init__.py",
        "conftest.py",
    }

    python_files = []
    for py_file in repo_path.rglob("*.py"):
        if any(excluded in py_file.parts for excluded in EXCLUDE_DIRS):
            continue
        if any(py_file.match(pattern) for pattern in EXCLUDE_PATTERNS):
            continue
        python_files.append(py_file)

    return python_files


def display_results(results: dict, format: str = "terminal"):
    """Display scan results in specified format."""

    if format == "sarif":
        # SARIF output
        formatter = SARIFFormatter(version="0.1.0")
        sarif_output = formatter.format(results)
        print(sarif_output)
        return

    if format == "json":
        # JSON output
        output = {
            "repository": results["repository"],
            "overall_score": results["vibe_score"]["overall_score"],
            "ai_assistance_level": results["vibe_score"]["ai_assistance_level"],
            "confidence": results["vibe_score"]["confidence"],
            "layers": {
                "artifact": {
                    "score": next(
                        (
                            s.score
                            for s in results["signals"]
                            if s.layer_type == DetectionLayerType.ARTIFACT
                        ),
                        0,
                    ),
                    "tools_found": len(results["artifacts"]),
                },
                "velocity": {
                    "score": next(
                        (
                            s.score
                            for s in results["signals"]
                            if s.layer_type == DetectionLayerType.VELOCITY
                        ),
                        0,
                    ),
                    "spike_detected": results["velocity_metrics"]["spike_detected"],
                },
                "pattern": {
                    "score": next(
                        (
                            s.score
                            for s in results["signals"]
                            if s.layer_type == DetectionLayerType.PATTERN
                        ),
                        0,
                    ),
                    "files_analyzed": len(results["pattern_results"]),
                },
                "ml": {
                    "score": next(
                        (
                            s.score
                            for s in results["signals"]
                            if s.layer_type == DetectionLayerType.ML
                        ),
                        0,
                    ),
                    "files_analyzed": len(results["ml_results"]),
                },
            },
            "interpretation": results["vibe_score"]["interpretation"],
            "recommendations": results["vibe_score"]["recommendations"],
        }
        print(json.dumps(output, indent=2))
        return

    # Terminal output
    console.print(
        "\n[bold magenta]╔═══════════════════════════════════════════════════════════╗[/bold magenta]"
    )
    console.print(
        "[bold magenta]║              VIBEMETRIC SCAN RESULTS                      ║[/bold magenta]"
    )
    console.print(
        "[bold magenta]╚═══════════════════════════════════════════════════════════╝[/bold magenta]"
    )

    console.print(f"\n[bold]Repository:[/bold] {results['repository']}")

    # Summary table
    table = Table(title="Detection Summary", show_header=True, header_style="bold magenta")
    table.add_column("Layer", style="cyan")
    table.add_column("Score", style="yellow")
    table.add_column("Status", style="green")

    for signal in results["signals"]:
        layer_name = signal.layer_type.value.title()
        score = f"{signal.score:.1f}/100"

        if signal.layer_type == DetectionLayerType.ARTIFACT:
            status = f"✓ {len(results['artifacts'])} tools" if results["artifacts"] else "✗ None"
        elif signal.layer_type == DetectionLayerType.VELOCITY:
            status = "✓ Spike" if results["velocity_metrics"]["spike_detected"] else "✗ No spike"
        elif signal.layer_type == DetectionLayerType.PATTERN:
            high_ai = sum(1 for r in results["pattern_results"] if r["score"] > 60)
            status = f"✓ {high_ai} high-AI files"
        elif signal.layer_type == DetectionLayerType.ML:
            ai_files = sum(1 for r in results["ml_results"] if r["prediction"] == "AI")
            status = f"✓ {ai_files} AI files"
        else:
            status = "✓"

        table.add_row(f"{layer_name} Detection", score, status)

    console.print("\n")
    console.print(table)

    # Overall score
    vibe = results["vibe_score"]
    level = vibe["ai_assistance_level"]
    level_colors = {"MINIMAL": "green", "PARTIAL": "yellow", "SUBSTANTIAL": "red"}
    color = level_colors.get(level, "white")

    console.print(
        f"\n[bold]Combined AI Likelihood:[/bold] [{color}]{vibe['overall_score']:.1f}/100[/{color}]"
    )
    console.print(f"[bold]AI Assistance Level:[/bold] [{color}]{level}[/{color}]")
    console.print(f"[bold]Confidence:[/bold] {vibe['confidence']:.2f}")

    # Interpretation
    console.print("\n[bold]Interpretation:[/bold]")
    console.print(f"  {vibe['interpretation']}")

    # Recommendations
    if vibe["recommendations"]:
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in vibe["recommendations"]:
            console.print(f"  • {rec}")

    console.print("\n[bold green]✓ Scan complete![/bold green]\n")


def cmd_scan(args):
    """Handle scan command."""
    # Suppress progress for non-terminal formats
    show_progress = args.format == "terminal"

    if show_progress:
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Scanning repository...", total=None)
            results = scan_repository(args.path, sample_size=args.sample_size, verbose=args.verbose)
            progress.update(task, completed=True)
    else:
        # No progress indicator for JSON/SARIF output
        results = scan_repository(args.path, sample_size=args.sample_size, verbose=args.verbose)

    display_results(results, format=args.format)


def cmd_developer_profile(args):
    """Handle developer-profile command."""
    repo_path = args.path

    # Validate repository path
    repo_path_obj = Path(repo_path)
    if not repo_path_obj.exists():
        console.print(f"[red]Error: Repository path does not exist: {repo_path}[/red]")
        sys.exit(1)

    # Create profiler
    profiler = DeveloperProfiler(repo_path)

    # Generate profiles
    if args.all:
        # Generate profiles for all developers
        profiles = profiler.generate_all_profiles()

        if not profiles:
            console.print("[yellow]No developers found in repository[/yellow]")
            sys.exit(0)

        if args.format == "json":
            # JSON output for all profiles
            output = {
                "repository": str(repo_path_obj.absolute()),
                "developer_count": len(profiles),
                "profiles": [p.to_dict() for p in profiles],
            }
            print(json.dumps(output, indent=2))
        else:
            # Terminal output for all profiles
            console.print(f"\n[bold magenta]Developer Profiles: {repo_path}[/bold magenta]\n")
            console.print(f"Found {len(profiles)} developers\n")

            for i, profile in enumerate(profiles, 1):
                console.print(f"[bold cyan]{'=' * 60}[/bold cyan]")
                console.print(f"[bold cyan]Developer {i}/{len(profiles)}[/bold cyan]")
                console.print(f"[bold cyan]{'=' * 60}[/bold cyan]")
                console.print(profile.format_terminal())
    else:
        # Generate profile for specific developer
        profile = profiler.generate_profile(author=args.author, email=args.email)

        if not profile:
            console.print("[yellow]Developer not found in repository[/yellow]")
            sys.exit(0)

        if profile.total_commits == 0:
            console.print(
                f"[yellow]No commits found for developer: {args.author or args.email}[/yellow]"
            )
            sys.exit(0)

        if args.format == "json":
            # JSON output
            print(profile.to_json())
        else:
            # Terminal output
            console.print("\n")
            console.print(profile.format_terminal())


def cmd_team_report(args):
    """Handle team-report command."""
    repo_path = args.path

    # Validate repository path
    repo_path_obj = Path(repo_path)
    if not repo_path_obj.exists():
        console.print(f"[red]Error: Repository path does not exist: {repo_path}[/red]")
        sys.exit(1)

    # Create reporter
    reporter = TeamReporter(repo_path)

    # Generate report
    report = reporter.generate_report(min_commits=args.min_commits)

    if report.total_developers == 0:
        console.print("[yellow]No developers found in repository[/yellow]")
        sys.exit(0)

    if args.format == "json":
        # JSON output
        print(report.to_json())
    else:
        # Terminal output
        console.print("\n")
        console.print(report.format_terminal())


def cmd_scan_pr(args):
    """Handle scan-pr command."""
    repo_path = args.path

    # Validate repository path
    repo_path_obj = Path(repo_path)
    if not repo_path_obj.exists():
        console.print(f"[red]Error: Repository path does not exist: {repo_path}[/red]")
        sys.exit(1)

    # Initialize analyzer
    pr_analyzer = PRAnalyzer(repo_path)

    # Determine PR analysis mode
    use_local = args.local or not GITHUB_AVAILABLE

    if use_local:
        # Mode 2: Local git analysis (no API)
        console.print("[cyan]Using local git analysis (no API calls)[/cyan]")

        if not args.pr_number:
            console.print("[red]Error: PR number required for local analysis[/red]")
            sys.exit(1)

        try:
            from .integrations.local_pr_analyzer import LocalPRAnalyzer

            local_analyzer = LocalPRAnalyzer(repo_path)

            console.print(f"[cyan]Fetching PR #{args.pr_number} from local git...[/cyan]")
            pr_data = local_analyzer.fetch_pr_locally(args.pr_number)

        except Exception as e:
            console.print(f"[red]Error fetching PR locally: {e}[/red]")
            console.print("[yellow]Tip: Ensure the PR branch is accessible via git fetch[/yellow]")
            sys.exit(1)
    else:
        # Mode 1: GitHub API
        if not GITHUB_AVAILABLE:
            console.print("[red]Error: PyGithub is not installed[/red]")
            console.print("Install with: pip install PyGithub")
            console.print("Or use --local flag for local git analysis")
            sys.exit(1)

        github_client = GitHubClient()

        # Fetch PR data
        try:
            if args.url:
                # Fetch by URL
                console.print(f"[cyan]Fetching PR from URL: {args.url}[/cyan]")
                pr_data = github_client.fetch_pr_by_url(args.url)
            else:
                # Fetch by PR number from local repo
                console.print(f"[cyan]Fetching PR #{args.pr_number} from GitHub API...[/cyan]")
                pr_data = github_client.fetch_pr_from_repo(repo_path, args.pr_number)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("[yellow]Tip: Use --local flag to analyze without GitHub API[/yellow]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            console.print("[yellow]Tip: Use --local flag to analyze without GitHub API[/yellow]")
            sys.exit(1)

    # Calculate baseline if requested
    baseline_score = None
    if args.baseline:
        console.print("[cyan]Calculating repository baseline...[/cyan]")
        baseline_results = scan_repository(repo_path, sample_size=20, verbose=False)
        baseline_score = baseline_results["vibe_score"]["overall_score"]

    # Analyze PR
    console.print("[cyan]Analyzing pull request...[/cyan]")
    result = pr_analyzer.analyze_pr_from_data(
        pr_number=pr_data["pr_number"],
        title=pr_data["title"],
        author=pr_data["author"],
        description=pr_data["description"],
        created_at=pr_data["created_at"],
        merged_at=pr_data["merged_at"],
        state=pr_data["state"],
        files_data=pr_data["files"],
        commits_data=pr_data["commits"],
        baseline_score=baseline_score,
    )

    # Display results
    if args.format == "json":
        # JSON output
        print(json.dumps(result.to_dict(), indent=2))
    else:
        # Terminal output
        console.print(result.format_terminal())


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Vibemetric - AI Code Detection Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vibemetric scan .                              # Scan current directory
  vibemetric scan /path/to/repo                  # Scan specific repository
  vibemetric scan . --format json                # Output as JSON
  vibemetric scan . --sample-size 20             # Analyze 20 files

  vibemetric developer-profile . --email john@example.com
  vibemetric developer-profile . --author "John Doe"
  vibemetric developer-profile . --all           # All developers
  vibemetric developer-profile . --all --format json

  vibemetric team-report .                       # Team-wide analytics
  vibemetric team-report . --min-commits 5       # Filter low-activity devs
  vibemetric team-report . --format json         # JSON output

  vibemetric scan-pr . 123                       # Analyze PR #123
  vibemetric scan-pr . --url https://github.com/user/repo/pull/123
  vibemetric scan-pr . 123 --baseline            # Compare with repo baseline
  vibemetric scan-pr . 123 --format json         # JSON output
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan repository for AI-generated code")
    scan_parser.add_argument("path", help="Path to repository")
    scan_parser.add_argument(
        "--format",
        choices=["terminal", "json", "sarif"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    scan_parser.add_argument(
        "--sample-size",
        type=int,
        default=10,
        help="Number of files to sample for analysis (default: 10)",
    )
    scan_parser.add_argument("--verbose", action="store_true", help="Show detailed progress")
    scan_parser.set_defaults(func=cmd_scan)

    # Developer profile command
    profile_parser = subparsers.add_parser(
        "developer-profile", help="Generate developer AI usage profile"
    )
    profile_parser.add_argument("path", help="Path to repository")
    profile_parser.add_argument("--author", help="Developer name to analyze")
    profile_parser.add_argument("--email", help="Developer email to analyze")
    profile_parser.add_argument(
        "--all", action="store_true", help="Generate profiles for all developers"
    )
    profile_parser.add_argument(
        "--format",
        choices=["terminal", "json"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    profile_parser.set_defaults(func=cmd_developer_profile)

    # Team report command
    team_parser = subparsers.add_parser("team-report", help="Generate team-wide AI usage report")
    team_parser.add_argument("path", help="Path to repository")
    team_parser.add_argument(
        "--min-commits",
        type=int,
        default=1,
        help="Minimum commits required to include developer (default: 1)",
    )
    team_parser.add_argument(
        "--format",
        choices=["terminal", "json"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    team_parser.set_defaults(func=cmd_team_report)

    # Scan PR command
    pr_parser = subparsers.add_parser(
        "scan-pr", help="Analyze specific pull request for AI-generated code"
    )
    pr_parser.add_argument("path", help="Path to repository")
    pr_parser.add_argument("pr_number", type=int, nargs="?", help="Pull request number")
    pr_parser.add_argument("--url", help="Full PR URL (alternative to pr_number)")
    pr_parser.add_argument(
        "--local",
        action="store_true",
        help="Use local git analysis (no GitHub API, no rate limits)",
    )
    pr_parser.add_argument(
        "--baseline", action="store_true", help="Compare with repository baseline"
    )
    pr_parser.add_argument(
        "--format",
        choices=["terminal", "json"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    pr_parser.set_defaults(func=cmd_scan_pr)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
