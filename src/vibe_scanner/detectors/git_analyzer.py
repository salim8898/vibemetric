"""
Git metadata analysis for AI-generated code detection.

This module implements git-based detection including:
- Git commit history extraction
- Authoring speed calculation (lines per minute)
- Commit pattern analysis (sizes, timing, intervals)
- Code churn metrics calculation
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models import DetectionSignal, SignalType, Evidence


class GitMetadataAnalyzer:
    """
    Analyzes git commit patterns and authoring metadata.
    
    Detects AI-generated code by analyzing git history for unusual patterns
    such as rapid authoring speed and suspicious commit patterns.
    """
    
    def __init__(self):
        """Initialize the git metadata analyzer."""
        self.weight = 0.30
        self.speed_threshold = 100  # lines per minute threshold
    
    def analyze(self, file_path: str, repo_path: str) -> DetectionSignal:
        """
        Analyze git metadata for a file.
        
        Args:
            file_path: Relative path to the file
            repo_path: Path to the repository root
            
        Returns:
            DetectionSignal with git analysis results
        """
        try:
            import git
        except ImportError:
            return self._create_null_signal("GitPython not available")
        
        try:
            repo = git.Repo(repo_path)
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            return self._create_null_signal("Not a git repository")
        
        # Get commit history for file
        commits = self._get_file_commits(repo, file_path)
        
        if not commits:
            return self._create_null_signal("No commit history")
        
        # Analyze commit patterns
        commit_sizes = self._extract_commit_sizes(commits)
        commit_intervals = self._extract_commit_intervals(commits)
        
        # Calculate authoring speed
        lines_per_minute = self._calculate_authoring_speed(commit_sizes, commit_intervals)
        
        # Detect unusual patterns
        unusual_speed = lines_per_minute > self.speed_threshold
        unusual_sizes = self._detect_size_outliers(commit_sizes)
        unusual_timing = self._detect_timing_anomalies(commit_intervals)
        
        # Calculate scores
        speed_score = self._score_authoring_speed(lines_per_minute)
        size_score = self._score_commit_sizes(commit_sizes, unusual_sizes)
        timing_score = self._score_commit_timing(commit_intervals, unusual_timing)
        
        # Combine git-based scores
        weights = [0.4, 0.3, 0.3]
        overall_score = sum(s * w for s, w in zip([speed_score, size_score, timing_score], weights))
        confidence = self._calculate_git_confidence(len(commits))
        
        evidence = [
            Evidence("AUTHORING_SPEED", speed_score, {"lines_per_minute": lines_per_minute}),
            Evidence("COMMIT_SIZES", size_score, {"unusual_count": len(unusual_sizes)}),
            Evidence("COMMIT_TIMING", timing_score, {"unusual_count": len(unusual_timing)})
        ]
        
        return DetectionSignal(
            signal_type=SignalType.GIT,
            signal_name="git_metadata",
            score=overall_score,
            confidence=confidence,
            weight=self.weight,
            evidence=evidence,
            metadata={
                "commit_count": len(commits),
                "lines_per_minute": lines_per_minute,
                "file_path": file_path
            }
        )
    
    def _get_file_commits(self, repo, file_path: str) -> List[Any]:
        """Get commit history for a specific file."""
        try:
            commits = list(repo.iter_commits(paths=file_path, max_count=50))
            return commits
        except Exception:
            return []
    
    def _extract_commit_sizes(self, commits: List[Any]) -> List[int]:
        """Extract lines added/deleted from commits."""
        sizes = []
        for commit in commits:
            try:
                stats = commit.stats.total
                lines_changed = stats.get('lines', 0) or (stats.get('insertions', 0) + stats.get('deletions', 0))
                sizes.append(lines_changed)
            except Exception:
                continue
        return sizes
    
    def _extract_commit_intervals(self, commits: List[Any]) -> List[float]:
        """Extract time intervals between commits (in minutes)."""
        intervals = []
        for i in range(len(commits) - 1):
            try:
                time_diff = commits[i].committed_date - commits[i + 1].committed_date
                intervals.append(time_diff / 60.0)  # Convert to minutes
            except Exception:
                continue
        return intervals
    
    def _calculate_authoring_speed(self, commit_sizes: List[int], commit_intervals: List[float]) -> float:
        """Calculate lines per minute authoring speed."""
        if not commit_sizes or not commit_intervals:
            return 0.0
        
        avg_commit_size = sum(commit_sizes) / len(commit_sizes)
        avg_interval = sum(commit_intervals) / len(commit_intervals) if commit_intervals else 1.0
        
        # Avoid division by zero
        if avg_interval == 0:
            avg_interval = 1.0
        
        lines_per_minute = avg_commit_size / avg_interval
        return lines_per_minute
    
    def _detect_size_outliers(self, commit_sizes: List[int]) -> List[int]:
        """Detect unusually large commits."""
        if not commit_sizes:
            return []
        
        avg_size = sum(commit_sizes) / len(commit_sizes)
        outliers = [size for size in commit_sizes if size > avg_size * 3]
        return outliers
    
    def _detect_timing_anomalies(self, commit_intervals: List[float]) -> List[float]:
        """Detect unusually short commit intervals."""
        if not commit_intervals:
            return []
        
        # Commits less than 5 minutes apart are suspicious
        anomalies = [interval for interval in commit_intervals if interval < 5.0]
        return anomalies
    
    def _score_authoring_speed(self, lines_per_minute: float) -> float:
        """Score authoring speed (higher speed = more AI-like)."""
        # Human typical: 5-20 lines/min
        # AI typical: 50-500+ lines/min
        if lines_per_minute < 20:
            return 0.0
        elif lines_per_minute < 50:
            return 30.0
        elif lines_per_minute < 100:
            return 60.0
        else:
            return min(80.0 + (lines_per_minute - 100) / 10, 100.0)
    
    def _score_commit_sizes(self, commit_sizes: List[int], unusual_sizes: List[int]) -> float:
        """Score commit size patterns."""
        if not commit_sizes:
            return 0.0
        
        outlier_ratio = len(unusual_sizes) / len(commit_sizes)
        return min(outlier_ratio * 100, 100.0)
    
    def _score_commit_timing(self, commit_intervals: List[float], unusual_timing: List[float]) -> float:
        """Score commit timing patterns."""
        if not commit_intervals:
            return 0.0
        
        anomaly_ratio = len(unusual_timing) / len(commit_intervals)
        return min(anomaly_ratio * 150, 100.0)
    
    def _calculate_git_confidence(self, commit_count: int) -> float:
        """Calculate confidence based on commit history depth."""
        # More commits = higher confidence
        if commit_count < 3:
            return 0.3
        elif commit_count < 10:
            return 0.6
        else:
            return min(0.6 + (commit_count - 10) * 0.02, 0.9)
    
    def _create_null_signal(self, reason: str = "") -> DetectionSignal:
        """Create a null signal when git analysis is unavailable."""
        return DetectionSignal(
            signal_type=SignalType.GIT,
            signal_name="git_metadata",
            score=0.0,
            confidence=0.0,
            weight=0.0,  # Zero weight when unavailable
            evidence=[Evidence("GIT_UNAVAILABLE", 0.0, {"reason": reason})],
            metadata={"reason": reason}
        )
