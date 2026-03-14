"""
Command-line interface for vibe-scanner.

Provides CLI commands for scanning repositories and generating reports.
"""

import sys
import os
import click

from .models import ScanConfig, OutputFormat
from .scanner import RepositoryScanner
from .reporter import ReportGenerator


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Vibe Scanner - AI-Generated Code Detection Tool"""
    pass


@cli.command()
@click.argument('repo_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Choice(['terminal', 'json', 'markdown']), 
              default='terminal', help='Output format')
@click.option('--output-file', '-f', type=click.Path(), help='Write output to file')
@click.option('--include', multiple=True, help='Include file patterns (can be repeated)')
@click.option('--exclude', multiple=True, help='Exclude file patterns (can be repeated)')
@click.option('--workers', '-w', type=int, default=1, help='Number of parallel workers')
@click.option('--no-git', is_flag=True, help='Disable git metadata analysis')
@click.option('--threshold', '-t', type=float, help='Exit with error if score exceeds threshold')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Minimal output')
@click.option('--max-file-size', type=int, default=1024, help='Maximum file size in KB')
def scan(repo_path, output, output_file, include, exclude, workers, no_git, 
         threshold, verbose, quiet, max_file_size):
    """Scan a repository for AI-generated code."""
    
    # Set verbosity
    verbosity = 0
    if verbose:
        verbosity = 2
    elif quiet:
        verbosity = 0
    else:
        verbosity = 1
    
    # Default patterns if none provided
    if not include:
        include = ['**/*.py', '**/*.js', '**/*.ts', '**/*.tsx', '**/*.jsx', 
                   '**/*.java', '**/*.go', '**/*.rs', '**/*.cpp', '**/*.c']
    
    if not exclude:
        exclude = ['**/node_modules/**', '**/__pycache__/**', '**/venv/**', 
                   '**/.git/**', '**/dist/**', '**/build/**']
    
    # Map output string to OutputFormat enum
    format_map = {
        'terminal': OutputFormat.TERMINAL,
        'json': OutputFormat.JSON,
        'markdown': OutputFormat.MARKDOWN
    }
    
    # Create configuration
    config = ScanConfig(
        repo_path=repo_path,
        include_patterns=list(include),
        exclude_patterns=list(exclude),
        file_extensions=[],  # Will use patterns instead
        max_file_size=max_file_size,
        parallel_workers=workers,
        enable_git_analysis=not no_git,
        output_format=format_map[output],
        verbosity=verbosity
    )
    
    try:
        # Create scanner and run scan
        if verbosity > 0:
            click.echo(f"Scanning repository: {repo_path}")
            click.echo(f"Workers: {workers}")
            click.echo("")
        
        scanner = RepositoryScanner(config)
        result = scanner.scan(repo_path)
        
        # Generate report
        reporter = ReportGenerator()
        report = reporter.generate(result, format_map[output])
        
        # Output report
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            if verbosity > 0:
                click.echo(f"\nReport written to: {output_file}")
        else:
            click.echo(report)
        
        # Check threshold and exit accordingly
        if threshold is not None:
            if result.overall_vibe_score.overall_score > threshold:
                click.echo(f"\nWARNING: Vibe score ({result.overall_vibe_score.overall_score:.1f}%) exceeds threshold ({threshold}%)", err=True)
                sys.exit(1)
        
        sys.exit(0)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbosity > 1:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
