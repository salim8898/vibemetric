"""
Developer Profile Generator

Analyzes individual developer AI usage patterns, tool adoption,
and productivity metrics.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import json

from ..detectors.artifact_detector import ArtifactDetector
from ..detectors.velocity_analyzer import VelocityAnalyzer
from ..detectors.pattern_detector import PatternDetector
from ..models import Artifact


@dataclass
class DeveloperProfile:
    """
    Developer AI usage profile.
    
    Attributes:
        author: Developer name
        email: Developer email
        ai_tools: List of AI tools used
        adoption_date: Date when AI tools were first adopted
        days_using_ai: Number of days using AI tools
        velocity_before_ai: Lines per day before AI adoption
        velocity_after_ai: Lines per day after AI adoption
        velocity_improvement: Percentage improvement in velocity
        total_commits: Total number of commits
        ai_assisted_commits: Number of commits with AI patterns
        ai_commit_percentage: Percentage of AI-assisted commits
        average_ai_score: Average AI likelihood score across commits
    """
    author: str
    email: Optional[str]
    ai_tools: List[str]
    adoption_date: Optional[datetime]
    days_using_ai: int
    velocity_before_ai: float
    velocity_after_ai: float
    velocity_improvement: float
    total_commits: int
    ai_assisted_commits: int
    ai_commit_percentage: float
    average_ai_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "author": self.author,
            "email": self.email,
            "ai_tools": self.ai_tools,
            "adoption_date": self.adoption_date.isoformat() if self.adoption_date else None,
            "days_using_ai": self.days_using_ai,
            "velocity_before_ai": round(self.velocity_before_ai, 1),
            "velocity_after_ai": round(self.velocity_after_ai, 1),
            "velocity_improvement": round(self.velocity_improvement, 1),
            "total_commits": self.total_commits,
            "ai_assisted_commits": self.ai_assisted_commits,
            "ai_commit_percentage": round(self.ai_commit_percentage, 1),
            "average_ai_score": round(self.average_ai_score, 1)
        }
    
    def to_json(self) -> str:
        """Convert profile to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def format_terminal(self) -> str:
        """Format profile for terminal display."""
        lines = []
        
        # Header
        header = f"Developer Profile: {self.author}"
        if self.email:
            header += f" ({self.email})"
        lines.append(header)
        lines.append("")
        
        # AI Tool Usage
        lines.append("AI Tool Usage:")
        if self.ai_tools:
            lines.append(f"  Tools: {', '.join(self.ai_tools)}")
            if self.adoption_date:
                lines.append(f"  Adoption Date: {self.adoption_date.strftime('%Y-%m-%d')}")
            lines.append(f"  Days Using AI: {self.days_using_ai}")
        else:
            lines.append("  No AI tools detected")
        lines.append("")
        
        # Productivity Metrics
        lines.append("Productivity Metrics:")
        if self.velocity_before_ai > 0 and self.velocity_after_ai > 0:
            lines.append(f"  Velocity Before AI: {self.velocity_before_ai:.1f} lines/day")
            lines.append(f"  Velocity After AI: {self.velocity_after_ai:.1f} lines/day")
            
            if self.velocity_improvement > 0:
                lines.append(f"  Improvement: +{self.velocity_improvement:.1f}%")
            elif self.velocity_improvement < 0:
                lines.append(f"  Change: {self.velocity_improvement:.1f}%")
            else:
                lines.append(f"  Change: No significant change")
        else:
            lines.append("  Insufficient data for velocity analysis")
        lines.append("")
        
        # Code Analysis
        lines.append("Code Analysis:")
        lines.append(f"  Total Commits: {self.total_commits}")
        if self.total_commits > 0:
            lines.append(f"  AI-Assisted Commits: {self.ai_assisted_commits} ({self.ai_commit_percentage:.1f}%)")
            lines.append(f"  Average AI Score: {self.average_ai_score:.1f}/100")
        lines.append("")
        
        return "\n".join(lines)


class DeveloperProfiler:
    """
    Generates developer AI usage profiles.
    
    Analyzes individual developer contributions to identify AI tool
    adoption, productivity changes, and AI-assisted code patterns.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize developer profiler.
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path)
        self.artifact_detector = ArtifactDetector(repo_path)
        self.velocity_analyzer = VelocityAnalyzer(repo_path)
        self.pattern_detector = PatternDetector()
    
    def generate_profile(self, author: Optional[str] = None, email: Optional[str] = None) -> Optional[DeveloperProfile]:
        """
        Generate profile for a specific developer.
        
        Args:
            author: Developer name (optional)
            email: Developer email (optional)
            
        Returns:
            Developer profile or None if developer not found
        """
        # Get developer identifier
        if not author and not email:
            return None
        
        # Detect AI tools in repository
        artifacts = self.artifact_detector.detect()
        
        # Find which tools THIS developer actually uses (based on artifact commits)
        developer_tools = []
        for artifact in artifacts:
            if author and author in artifact.authors:
                if artifact.tool_name not in developer_tools:
                    developer_tools.append(artifact.tool_name)
        
        # Find adoption date for this developer
        adoption_date = self._find_adoption_date(artifacts, author, email)
        
        # Calculate days using AI
        days_using_ai = 0
        if adoption_date:
            days_using_ai = (datetime.now() - adoption_date).days
        
        # Analyze velocity
        velocity_metrics = self.velocity_analyzer.analyze(author=author)
        
        # Analyze commits
        commits = self.velocity_analyzer._get_commits(author=author)
        
        # Filter commits by email if provided
        if email:
            commits = [c for c in commits if c.email == email]
        
        total_commits = len(commits)
        
        # Analyze commit messages for AI patterns
        ai_assisted_commits = 0
        ai_scores = []
        
        for commit in commits:
            signal = self.pattern_detector.analyze_commit_message(commit.message)
            if signal.score > 40.0:  # Threshold for AI-assisted
                ai_assisted_commits += 1
            ai_scores.append(signal.score)
        
        # Calculate statistics
        ai_commit_percentage = (ai_assisted_commits / total_commits * 100) if total_commits > 0 else 0.0
        average_ai_score = sum(ai_scores) / len(ai_scores) if ai_scores else 0.0
        
        # Calculate velocity improvement
        velocity_improvement = 0.0
        if velocity_metrics["baseline_velocity"] > 0:
            velocity_improvement = (
                (velocity_metrics["current_velocity"] / velocity_metrics["baseline_velocity"] - 1.0) * 100
            )
        
        # Determine author name
        if not author and commits:
            author = commits[0].author
        
        # Determine email
        if not email and commits:
            email = commits[0].email
        
        return DeveloperProfile(
            author=author or "Unknown",
            email=email,
            ai_tools=developer_tools,  # Only tools they committed
            adoption_date=adoption_date,
            days_using_ai=days_using_ai,
            velocity_before_ai=velocity_metrics["baseline_velocity"],
            velocity_after_ai=velocity_metrics["current_velocity"],
            velocity_improvement=velocity_improvement,
            total_commits=total_commits,
            ai_assisted_commits=ai_assisted_commits,
            ai_commit_percentage=ai_commit_percentage,
            average_ai_score=average_ai_score
        )
    
    def generate_all_profiles(self) -> List[DeveloperProfile]:
        """
        Generate profiles for all developers in repository.
        
        Returns:
            List of developer profiles (deduplicated by author name)
        """
        # Get all commits to find unique developers
        commits = self.velocity_analyzer._get_commits()
        
        # Find unique developers by email
        developers = {}
        for commit in commits:
            if commit.email not in developers:
                developers[commit.email] = commit.author
        
        # Generate profile for each developer
        profiles = []
        for email, author in developers.items():
            profile = self.generate_profile(author=author, email=email)
            if profile and profile.total_commits > 0:
                profiles.append(profile)
        
        # Deduplicate by author name (merge profiles with same name but different emails)
        deduplicated = self._deduplicate_profiles(profiles)
        
        # Sort by total commits (most active first)
        deduplicated.sort(key=lambda p: p.total_commits, reverse=True)
        
        return deduplicated
    
    def _deduplicate_profiles(self, profiles: List[DeveloperProfile]) -> List[DeveloperProfile]:
        """
        Merge profiles for the same author with different emails.
        
        Args:
            profiles: List of profiles to deduplicate
            
        Returns:
            Deduplicated list of profiles
        """
        # Group profiles by author name
        by_author = {}
        for profile in profiles:
            author_key = profile.author.lower().strip()
            if author_key not in by_author:
                by_author[author_key] = []
            by_author[author_key].append(profile)
        
        # Merge profiles for same author
        merged = []
        for author_key, author_profiles in by_author.items():
            if len(author_profiles) == 1:
                # Single profile, no merging needed
                merged.append(author_profiles[0])
            else:
                # Multiple profiles for same author - merge them
                merged_profile = self._merge_profiles(author_profiles)
                merged.append(merged_profile)
        
        return merged
    
    def _merge_profiles(self, profiles: List[DeveloperProfile]) -> DeveloperProfile:
        """
        Merge multiple profiles for the same author.
        
        Args:
            profiles: List of profiles to merge
            
        Returns:
            Merged profile
        """
        # Use the profile with most commits as base
        profiles.sort(key=lambda p: p.total_commits, reverse=True)
        base = profiles[0]
        
        # Collect all emails
        all_emails = [p.email for p in profiles if p.email]
        email_str = ", ".join(all_emails) if all_emails else None
        
        # Merge AI tools (unique)
        all_tools = []
        for p in profiles:
            all_tools.extend(p.ai_tools)
        unique_tools = list(dict.fromkeys(all_tools))  # Preserve order, remove duplicates
        
        # Use earliest adoption date
        adoption_dates = [p.adoption_date for p in profiles if p.adoption_date]
        earliest_adoption = min(adoption_dates) if adoption_dates else None
        
        # Calculate days using AI from earliest adoption
        days_using_ai = 0
        if earliest_adoption:
            days_using_ai = (datetime.now() - earliest_adoption).days
        
        # Sum commits
        total_commits = sum(p.total_commits for p in profiles)
        ai_assisted_commits = sum(p.ai_assisted_commits for p in profiles)
        
        # Calculate weighted average AI score
        total_score_weight = sum(p.average_ai_score * p.total_commits for p in profiles)
        average_ai_score = total_score_weight / total_commits if total_commits > 0 else 0.0
        
        # Calculate AI commit percentage
        ai_commit_percentage = (ai_assisted_commits / total_commits * 100) if total_commits > 0 else 0.0
        
        # Use velocity from profile with most commits
        return DeveloperProfile(
            author=base.author,
            email=email_str,
            ai_tools=unique_tools,
            adoption_date=earliest_adoption,
            days_using_ai=days_using_ai,
            velocity_before_ai=base.velocity_before_ai,
            velocity_after_ai=base.velocity_after_ai,
            velocity_improvement=base.velocity_improvement,
            total_commits=total_commits,
            ai_assisted_commits=ai_assisted_commits,
            ai_commit_percentage=ai_commit_percentage,
            average_ai_score=average_ai_score
        )
    
    def _find_adoption_date(
        self,
        artifacts: List[Artifact],
        author: Optional[str],
        email: Optional[str]
    ) -> Optional[datetime]:
        """
        Find when developer adopted AI tools.
        
        This looks at git history to find when the developer FIRST
        committed or modified an AI tool config file.
        
        Args:
            artifacts: List of detected artifacts
            author: Developer name
            email: Developer email
            
        Returns:
            Adoption date or None if developer didn't commit artifacts
        """
        if not artifacts or not self.artifact_detector.repo:
            return None
        
        # Find earliest commit by this developer for any artifact
        earliest_dates = []
        
        for artifact in artifacts:
            # Check if developer is in artifact authors
            if author and author in artifact.authors:
                # Get the actual date when THIS developer first touched the file
                artifact_path = self.repo_path / artifact.file_path
                try:
                    rel_path = artifact_path.relative_to(self.repo_path)
                    
                    # Get commits by this author for this file (oldest first)
                    commits = list(self.artifact_detector.repo.iter_commits(
                        paths=str(rel_path),
                        reverse=True
                    ))
                    
                    # Find first commit by this author
                    for commit in commits:
                        if commit.author.name == author:
                            earliest_dates.append(datetime.fromtimestamp(commit.committed_date))
                            break
                            
                except (ValueError, Exception):
                    pass
        
        if earliest_dates:
            return min(earliest_dates)
        
        # Don't use repository-wide artifact date as fallback
        return None
