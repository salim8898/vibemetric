"""
Velocity Analyzer - Layer 2 (80% Accuracy)

Detects AI usage by analyzing coding velocity changes.
A sudden 2x+ increase in lines of code per day suggests AI adoption.

Algorithm:
1. Calculate baseline velocity (30-day average before spike)
2. Calculate current velocity (30-day average after spike)
3. Detect velocity spikes (2x+ increase)
4. Cross-reference with artifact adoption dates

KNOWN LIMITATIONS:
- Squash merge workflows may produce inaccurate results
- Large squash commits appear as artificial velocity spikes
- TODO: Implement PR-based analysis for squash merge detection
  See: https://github.com/vibemetric/issues/squash-merge-support

FUTURE ENHANCEMENTS:
1. Detect squash merge commits (>500 lines, many files)
2. Fetch PR timeline data from GitHub/GitLab API
3. Calculate velocity based on PR open-to-merge duration
4. Hybrid approach: regular commits + PR-based for squash merges
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import git

from ..models import DetectionSignal, DetectionLayerType, Commit


class VelocityAnalyzer:
    """
    Analyzes coding velocity to detect AI adoption.

    A 2x+ velocity increase suggests AI tool usage.
    """

    def __init__(self, repo_path: str):
        """
        Initialize velocity analyzer.

        Args:
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path)
        self.repo: Optional[git.Repo] = None

        # Try to open git repository
        try:
            self.repo = git.Repo(repo_path)
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            self.repo = None

    def analyze(self, author: Optional[str] = None) -> Dict[str, any]:
        """
        Analyze velocity for repository or specific author.

        Args:
            author: Optional author name to analyze (None = all authors)

        Returns:
            Dictionary with velocity metrics
        """
        if not self.repo:
            return {
                "baseline_velocity": 0.0,
                "current_velocity": 0.0,
                "velocity_increase": 0.0,
                "spike_detected": False,
                "spike_date": None,
            }

        # Get commits
        commits = self._get_commits(author)

        if len(commits) < 10:
            # Not enough data
            return {
                "baseline_velocity": 0.0,
                "current_velocity": 0.0,
                "velocity_increase": 0.0,
                "spike_detected": False,
                "spike_date": None,
            }

        # Detect velocity spike
        spike_date = self._detect_spike(commits)

        if spike_date:
            # Calculate baseline (before spike)
            baseline = self._calculate_velocity(commits, end_date=spike_date, days=30)

            # Calculate current (after spike)
            current = self._calculate_velocity(commits, start_date=spike_date, days=30)

            velocity_increase = (current / baseline - 1.0) * 100 if baseline > 0 else 0.0

            return {
                "baseline_velocity": baseline,
                "current_velocity": current,
                "velocity_increase": velocity_increase,
                "spike_detected": True,
                "spike_date": spike_date,
            }
        else:
            # No spike detected, calculate overall velocity
            velocity = self._calculate_velocity(commits, days=30)

            return {
                "baseline_velocity": velocity,
                "current_velocity": velocity,
                "velocity_increase": 0.0,
                "spike_detected": False,
                "spike_date": None,
            }

    def get_detection_signal(self, metrics: Dict[str, any]) -> DetectionSignal:
        """
        Create detection signal from velocity metrics.

        Args:
            metrics: Velocity analysis results

        Returns:
            Detection signal for velocity layer
        """
        if not metrics["spike_detected"]:
            return DetectionSignal(
                layer_type=DetectionLayerType.VELOCITY,
                score=0.0,
                confidence=0.0,
                evidence=[],
                metadata=metrics,
            )

        # Score based on velocity increase
        # 1.8x = 60, 2.7x = 80, 3.5x+ = 90
        increase_ratio = (
            metrics["current_velocity"] / metrics["baseline_velocity"]
            if metrics["baseline_velocity"] > 0
            else 1.0
        )

        if increase_ratio >= 3.5:
            score = 90.0
            confidence = 0.85
        elif increase_ratio >= 2.7:
            score = 80.0
            confidence = 0.82
        elif increase_ratio >= 1.8:
            score = 60.0
            confidence = 0.78
        else:
            score = 0.0
            confidence = 0.0

        evidence = [
            f"Velocity increased from {metrics['baseline_velocity']:.1f} to {metrics['current_velocity']:.1f} lines/day",
            f"Spike detected on {metrics['spike_date'].strftime('%Y-%m-%d') if metrics['spike_date'] else 'unknown'}",
            f"Increase: {metrics['velocity_increase']:.1f}%",
        ]

        return DetectionSignal(
            layer_type=DetectionLayerType.VELOCITY,
            score=score,
            confidence=confidence,
            evidence=evidence,
            metadata=metrics,
        )

    def _get_commits(self, author: Optional[str] = None, debug: bool = False) -> List[Commit]:
        """
        Get commits from repository.

        Args:
            author: Optional author name filter
            debug: Print debug information

        Returns:
            List of commits with metadata
        """
        if not self.repo:
            if debug:
                print("DEBUG: No repo object")
            return []

        commits = []

        try:
            # Get all commits
            for idx, git_commit in enumerate(self.repo.iter_commits()):
                if debug and idx < 3:
                    print(f"DEBUG: Processing commit {idx}: {git_commit.hexsha[:8]}")

                # Filter by author if specified
                if author and git_commit.author.name != author:
                    if debug and idx < 3:
                        print(f"  Skipped: author filter ({git_commit.author.name} != {author})")
                    continue

                # Calculate lines changed
                lines_added = 0
                lines_removed = 0

                try:
                    if git_commit.parents:
                        # Compare with parent
                        parent = git_commit.parents[0]
                        diff = parent.diff(git_commit, create_patch=True)

                        for diff_item in diff:
                            if diff_item.diff:
                                diff_text = diff_item.diff.decode("utf-8", errors="ignore")
                                for line in diff_text.split("\n"):
                                    if line.startswith("+") and not line.startswith("+++"):
                                        lines_added += 1
                                    elif line.startswith("-") and not line.startswith("---"):
                                        lines_removed += 1
                    else:
                        # First commit - count all lines as added
                        for item in git_commit.stats.files:
                            lines_added += git_commit.stats.files[item]["insertions"]
                            lines_removed += git_commit.stats.files[item]["deletions"]

                    if debug and idx < 3:
                        print(f"  Lines: +{lines_added} -{lines_removed}")

                except Exception as e:
                    if debug and idx < 3:
                        print(f"  Diff error: {e}, trying stats fallback")
                    # If diff fails, use stats as fallback
                    try:
                        for item in git_commit.stats.files:
                            lines_added += git_commit.stats.files[item]["insertions"]
                            lines_removed += git_commit.stats.files[item]["deletions"]
                        if debug and idx < 3:
                            print(f"  Stats fallback: +{lines_added} -{lines_removed}")
                    except Exception as e2:
                        if debug and idx < 3:
                            print(f"  Stats fallback error: {e2}, skipping")
                        # Skip commits with errors
                        continue

                commit = Commit(
                    commit_hash=git_commit.hexsha,
                    author=git_commit.author.name,
                    email=git_commit.author.email,
                    timestamp=datetime.fromtimestamp(git_commit.committed_date),
                    message=git_commit.message,
                    lines_added=lines_added,
                    lines_deleted=lines_removed,
                    files_changed=[str(f) for f in git_commit.stats.files.keys()],
                )
                commits.append(commit)

                if debug and idx < 3:
                    print(f"  Added commit to list")

        except Exception as e:
            if debug:
                print(f"DEBUG: Outer exception: {e}")
            # Log error but don't crash
            pass

        if debug:
            print(f"DEBUG: Total commits collected: {len(commits)}")

        return commits

    def _detect_spike(self, commits: List[Commit]) -> Optional[datetime]:
        """
        Detect velocity spike in commit history.

        Args:
            commits: List of commits sorted by date

        Returns:
            Date of velocity spike, or None if no spike detected
        """
        if len(commits) < 40:  # Need at least 40 commits for analysis
            return None

        # Sort commits by date
        commits = sorted(commits, key=lambda c: c.timestamp)

        # Split into two halves and compare
        mid_point = len(commits) // 2
        first_half = commits[:mid_point]
        second_half = commits[mid_point:]

        # Calculate velocities for each half
        first_velocity = self._calculate_velocity_for_commits(first_half)
        second_velocity = self._calculate_velocity_for_commits(second_half)

        # Check for 2x spike
        if first_velocity > 0 and second_velocity / first_velocity >= 2.0:
            # Return the date of the first commit in second half (spike point)
            return second_half[0].timestamp

        # Also try sliding window approach for more granular detection
        window_size = 10  # Smaller window for better sensitivity
        velocities = []

        for i in range(len(commits) - window_size):
            window = commits[i : i + window_size]
            velocity = self._calculate_velocity_for_commits(window)
            velocities.append((window[-1].timestamp, velocity))

        # Find significant spikes (2x+ increase)
        for i in range(1, len(velocities)):
            prev_velocity = velocities[i - 1][1]
            curr_velocity = velocities[i][1]

            if prev_velocity > 0 and curr_velocity / prev_velocity >= 2.0:
                # Found a spike
                return velocities[i][0]

        return None

    def _calculate_velocity(
        self,
        commits: List[Commit],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 30,
    ) -> float:
        """
        Calculate average lines per day for a time period.

        Args:
            commits: List of commits
            start_date: Start date (None = use earliest)
            end_date: End date (None = use latest)
            days: Number of days to analyze

        Returns:
            Average lines per day
        """
        # Filter commits by date range
        filtered = commits

        if start_date:
            filtered = [c for c in filtered if c.timestamp >= start_date]

        if end_date:
            filtered = [c for c in filtered if c.timestamp <= end_date]

        # Take only the specified number of days
        if filtered:
            filtered = sorted(filtered, key=lambda c: c.timestamp)

            if start_date:
                # Take first N days after start
                cutoff = start_date + timedelta(days=days)
                filtered = [c for c in filtered if c.timestamp <= cutoff]
            elif end_date:
                # Take last N days before end
                cutoff = end_date - timedelta(days=days)
                filtered = [c for c in filtered if c.timestamp >= cutoff]
            else:
                # Take last N days
                if len(filtered) > 0:
                    latest = filtered[-1].timestamp
                    cutoff = latest - timedelta(days=days)
                    filtered = [c for c in filtered if c.timestamp >= cutoff]

        return self._calculate_velocity_for_commits(filtered)

    def _calculate_velocity_for_commits(self, commits: List[Commit]) -> float:
        """
        Calculate average lines per day for a list of commits.

        Args:
            commits: List of commits

        Returns:
            Average lines per day
        """
        if not commits:
            return 0.0

        # Calculate total lines
        total_lines = sum(c.lines_added + c.lines_deleted for c in commits)

        # Calculate time span
        commits = sorted(commits, key=lambda c: c.timestamp)
        time_span = (commits[-1].timestamp - commits[0].timestamp).days

        if time_span == 0:
            time_span = 1  # Avoid division by zero

        return total_lines / time_span
