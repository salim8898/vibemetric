"""
Team Report Generator

Generates team-wide AI usage analytics by aggregating
individual developer profiles.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from collections import Counter
import json

from ..profiles import DeveloperProfiler, DeveloperProfile


@dataclass
class TeamReport:
    """
    Team-wide AI usage report.
    
    Attributes:
        repository: Repository path
        total_developers: Total number of developers
        ai_tool_users: Number of developers with AI tool configs
        shadow_ai_users: Number of developers using AI without configs
        human_only_developers: Number of developers with no AI usage
        ai_adoption_rate: Percentage of developers using AI (any type)
        tool_distribution: Dictionary of tool name to user count
        top_ai_users: List of top developers by AI usage
        productivity_metrics: Team productivity statistics
        ai_adoption_timeline: Timeline of AI tool adoptions
    """
    repository: str
    total_developers: int
    ai_tool_users: int
    shadow_ai_users: int
    human_only_developers: int
    ai_adoption_rate: float
    tool_distribution: Dict[str, int]
    top_ai_users: List[Dict[str, Any]]
    productivity_metrics: Dict[str, Any]
    ai_adoption_timeline: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "repository": self.repository,
            "total_developers": self.total_developers,
            "ai_tool_users": self.ai_tool_users,
            "shadow_ai_users": self.shadow_ai_users,
            "human_only_developers": self.human_only_developers,
            "ai_adoption_rate": round(self.ai_adoption_rate, 1),
            "tool_distribution": self.tool_distribution,
            "top_ai_users": self.top_ai_users,
            "productivity_metrics": self.productivity_metrics,
            "ai_adoption_timeline": self.ai_adoption_timeline
        }
    
    def to_json(self) -> str:
        """Convert report to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def format_terminal(self) -> str:
        """Format report for terminal display."""
        lines = []
        
        # Header
        lines.append(f"Team AI Usage Report: {self.repository}")
        lines.append("")
        
        # Team Overview
        lines.append("Team Overview:")
        lines.append(f"  Total Developers: {self.total_developers}")
        
        ai_tool_pct = (self.ai_tool_users / self.total_developers * 100) if self.total_developers > 0 else 0
        lines.append(f"  AI Tool Users: {self.ai_tool_users} ({ai_tool_pct:.1f}%)")
        
        shadow_pct = (self.shadow_ai_users / self.total_developers * 100) if self.total_developers > 0 else 0
        lines.append(f"  Shadow AI Users: {self.shadow_ai_users} ({shadow_pct:.1f}%)")
        
        human_pct = (self.human_only_developers / self.total_developers * 100) if self.total_developers > 0 else 0
        lines.append(f"  Human-Only Developers: {self.human_only_developers} ({human_pct:.1f}%)")
        
        lines.append(f"  Overall AI Adoption Rate: {self.ai_adoption_rate:.1f}%")
        lines.append("")
        
        # AI Tool Distribution
        if self.tool_distribution:
            lines.append("AI Tool Distribution:")
            for tool, count in sorted(self.tool_distribution.items(), key=lambda x: x[1], reverse=True):
                plural = "developers" if count > 1 else "developer"
                lines.append(f"  {tool}: {count} {plural}")
            lines.append("")
        
        # Top AI Users
        if self.top_ai_users:
            lines.append(f"Top AI Users (by AI-assisted commits):")
            for i, user in enumerate(self.top_ai_users[:10], 1):
                lines.append(
                    f"  {i}. {user['author']} - {user['ai_commit_percentage']:.1f}% AI-assisted "
                    f"({user['ai_assisted_commits']}/{user['total_commits']} commits, "
                    f"score: {user['average_ai_score']:.1f}/100)"
                )
            lines.append("")
        
        # Productivity Metrics
        metrics = self.productivity_metrics
        lines.append("Productivity Metrics:")
        
        if metrics.get('developers_with_velocity_data', 0) > 0:
            avg_improvement = metrics['average_velocity_improvement']
            if avg_improvement > 0:
                lines.append(f"  Average Velocity Improvement: +{avg_improvement:.1f}%")
            elif avg_improvement < 0:
                lines.append(f"  Average Velocity Improvement: {avg_improvement:.1f}%")
            else:
                lines.append(f"  Average Velocity Improvement: No significant change (0.0%)")
            
            lines.append(f"  Developers with Velocity Data: {metrics['developers_with_velocity_data']}")
            
            if metrics['developers_with_positive_impact'] > 0:
                lines.append(f"  Developers with Positive Impact: {metrics['developers_with_positive_impact']}")
            if metrics['developers_with_negative_impact'] > 0:
                lines.append(f"  Developers with Negative Impact: {metrics['developers_with_negative_impact']}")
            if metrics['developers_with_positive_impact'] == 0 and metrics['developers_with_negative_impact'] == 0:
                lines.append(f"  Note: Velocity unchanged for all developers with data")
        else:
            lines.append("  Insufficient velocity data for analysis")
        
        lines.append(f"  Average AI Score: {metrics['average_ai_score']:.1f}/100")
        lines.append(f"    (Team-wide average of commit message AI likelihood)")
        lines.append(f"  Total Commits Analyzed: {metrics['total_commits']}")
        lines.append(f"  AI-Assisted Commits: {metrics['ai_assisted_commits']} ({metrics['ai_assisted_percentage']:.1f}%)")
        lines.append(f"    (Commits with AI patterns: structured format, lists, etc.)")
        lines.append("")
        
        # AI Adoption Timeline
        if self.ai_adoption_timeline:
            lines.append("AI Adoption Timeline:")
            for event in self.ai_adoption_timeline[:10]:
                lines.append(f"  {event['date']}: {event['developer']} adopted {event['tool']}")
            if len(self.ai_adoption_timeline) > 10:
                lines.append(f"  ... and {len(self.ai_adoption_timeline) - 10} more")
            lines.append("")
        
        # Explanation section
        lines.append("=" * 70)
        lines.append("METRIC EXPLANATIONS")
        lines.append("=" * 70)
        lines.append("")
        lines.append("AI Tool Users:")
        lines.append("  Developers who committed AI tool config files (.cursorrules, .kiro/, etc.)")
        lines.append("")
        lines.append("Shadow AI Users:")
        lines.append("  Developers with >50% AI-assisted commits but no config files")
        lines.append("  (Using AI tools without committing configuration)")
        lines.append("")
        lines.append("Average AI Score:")
        lines.append("  Team-wide average of commit message AI likelihood (0-100)")
        lines.append("  Based on patterns: structured format, bullet lists, conventional commits")
        lines.append("  - 0-40: Minimal AI usage")
        lines.append("  - 40-70: Partial AI usage")
        lines.append("  - 70-100: Substantial AI usage")
        lines.append("")
        lines.append("AI-Assisted Commits:")
        lines.append("  Commits with AI patterns (score >40): structured, list-style, verbose")
        lines.append("")
        
        return "\n".join(lines)


class TeamReporter:
    """
    Generates team-wide AI usage reports.
    
    Aggregates individual developer profiles to provide
    team-level insights and analytics.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize team reporter.
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path)
        self.profiler = DeveloperProfiler(repo_path)
    
    def generate_report(self, min_commits: int = 1) -> TeamReport:
        """
        Generate team-wide AI usage report.
        
        Args:
            min_commits: Minimum commits required to include developer
            
        Returns:
            Team report with aggregated analytics
        """
        # Get all developer profiles
        profiles = self.profiler.generate_all_profiles()
        
        # Filter by minimum commits
        profiles = [p for p in profiles if p.total_commits >= min_commits]
        
        total_developers = len(profiles)
        
        if total_developers == 0:
            return self._empty_report()
        
        # Calculate AI tool users (developers who committed AI config files)
        ai_tool_users = len([p for p in profiles if p.ai_tools])
        
        # Calculate shadow AI users (high AI usage but no config files)
        # Shadow AI = AI-assisted commits > 50% AND no AI tools
        shadow_ai_users = len([
            p for p in profiles 
            if not p.ai_tools and p.ai_commit_percentage > 50.0
        ])
        
        # Calculate human-only developers (low AI usage, no tools)
        human_only_developers = len([
            p for p in profiles
            if not p.ai_tools and p.ai_commit_percentage <= 50.0
        ])
        
        # Calculate overall AI adoption rate (tool users + shadow users)
        ai_adoption_rate = ((ai_tool_users + shadow_ai_users) / total_developers * 100) if total_developers > 0 else 0.0
        
        # Tool distribution
        tool_counter = Counter()
        for profile in profiles:
            for tool in profile.ai_tools:
                tool_counter[tool] += 1
        tool_distribution = dict(tool_counter)
        
        # Top AI users (by AI-assisted commit percentage, then by total commits)
        top_ai_users = sorted(
            profiles,
            key=lambda p: (p.ai_commit_percentage, p.total_commits),
            reverse=True
        )[:20]
        
        top_ai_users_data = [
            {
                "author": p.author,
                "email": p.email,
                "total_commits": p.total_commits,
                "ai_assisted_commits": p.ai_assisted_commits,
                "ai_commit_percentage": p.ai_commit_percentage,
                "average_ai_score": p.average_ai_score,
                "ai_tools": p.ai_tools
            }
            for p in top_ai_users
        ]
        
        # Productivity metrics
        productivity_metrics = self._calculate_productivity_metrics(profiles)
        
        # AI adoption timeline
        ai_adoption_timeline = self._build_adoption_timeline(profiles)
        
        return TeamReport(
            repository=str(self.repo_path.absolute()),
            total_developers=total_developers,
            ai_tool_users=ai_tool_users,
            shadow_ai_users=shadow_ai_users,
            human_only_developers=human_only_developers,
            ai_adoption_rate=ai_adoption_rate,
            tool_distribution=tool_distribution,
            top_ai_users=top_ai_users_data,
            productivity_metrics=productivity_metrics,
            ai_adoption_timeline=ai_adoption_timeline
        )
    
    def _calculate_productivity_metrics(self, profiles: List[DeveloperProfile]) -> Dict[str, Any]:
        """Calculate team productivity metrics."""
        # Velocity improvements
        velocity_improvements = [
            p.velocity_improvement
            for p in profiles
            if p.velocity_before_ai > 0 and p.velocity_after_ai > 0
        ]
        
        avg_velocity_improvement = (
            sum(velocity_improvements) / len(velocity_improvements)
            if velocity_improvements else 0.0
        )
        
        developers_with_positive_impact = len([v for v in velocity_improvements if v > 0])
        developers_with_negative_impact = len([v for v in velocity_improvements if v < 0])
        
        # AI scores
        ai_scores = [p.average_ai_score for p in profiles]
        average_ai_score = sum(ai_scores) / len(ai_scores) if ai_scores else 0.0
        
        # Commit statistics
        total_commits = sum(p.total_commits for p in profiles)
        ai_assisted_commits = sum(p.ai_assisted_commits for p in profiles)
        ai_assisted_percentage = (ai_assisted_commits / total_commits * 100) if total_commits > 0 else 0.0
        
        return {
            "average_velocity_improvement": avg_velocity_improvement,
            "developers_with_velocity_data": len(velocity_improvements),
            "developers_with_positive_impact": developers_with_positive_impact,
            "developers_with_negative_impact": developers_with_negative_impact,
            "average_ai_score": average_ai_score,
            "total_commits": total_commits,
            "ai_assisted_commits": ai_assisted_commits,
            "ai_assisted_percentage": ai_assisted_percentage
        }
    
    def _build_adoption_timeline(self, profiles: List[DeveloperProfile]) -> List[Dict[str, Any]]:
        """Build timeline of AI tool adoptions."""
        timeline = []
        
        for profile in profiles:
            if profile.adoption_date and profile.ai_tools:
                for tool in profile.ai_tools:
                    timeline.append({
                        "date": profile.adoption_date.strftime("%Y-%m-%d"),
                        "developer": profile.author,
                        "tool": tool
                    })
        
        # Sort by date
        timeline.sort(key=lambda x: x["date"])
        
        return timeline
    
    def _empty_report(self) -> TeamReport:
        """Create empty report for repositories with no developers."""
        return TeamReport(
            repository=str(self.repo_path.absolute()),
            total_developers=0,
            ai_tool_users=0,
            shadow_ai_users=0,
            human_only_developers=0,
            ai_adoption_rate=0.0,
            tool_distribution={},
            top_ai_users=[],
            productivity_metrics={
                "average_velocity_improvement": 0.0,
                "developers_with_velocity_data": 0,
                "developers_with_positive_impact": 0,
                "developers_with_negative_impact": 0,
                "average_ai_score": 0.0,
                "total_commits": 0,
                "ai_assisted_commits": 0,
                "ai_assisted_percentage": 0.0
            },
            ai_adoption_timeline=[]
        )
