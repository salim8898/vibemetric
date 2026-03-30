"""
Pull Request Analyzer

Analyzes pull requests for AI-generated code patterns.
This is a unique differentiator for Vibemetric.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from ..detectors.pattern_detector import PatternDetector
from ..detectors.ml_detector import MLDetector
from ..scorer import Scorer
from ..models import DetectionSignal, DetectionLayerType, AIAssistanceLevel


@dataclass
class PRFile:
    """Represents a file changed in a PR"""
    filename: str
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None
    content: Optional[str] = None
    ai_score: float = 0.0
    confidence: float = 0.0


@dataclass
class PRCommit:
    """Represents a commit in a PR"""
    sha: str
    message: str
    author: str
    timestamp: datetime
    ai_score: float = 0.0
    confidence: float = 0.0


@dataclass
class PRAnalysisResult:
    """Complete PR analysis result"""
    pr_number: int
    title: str
    author: str
    created_at: datetime
    merged_at: Optional[datetime]
    state: str
    
    # PR description analysis
    description: str
    description_ai_score: float = 0.0
    description_confidence: float = 0.0
    description_patterns: List[str] = field(default_factory=list)
    
    # Files analysis
    files: List[PRFile] = field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0
    high_ai_files: List[PRFile] = field(default_factory=list)
    
    # Commits analysis
    commits: List[PRCommit] = field(default_factory=list)
    ai_style_commits: int = 0
    avg_commit_ai_score: float = 0.0
    
    # Overall scores
    overall_ai_score: float = 0.0
    overall_confidence: float = 0.0
    ai_assistance_level: AIAssistanceLevel = AIAssistanceLevel.MINIMAL
    
    # Baseline comparison
    repo_baseline_score: Optional[float] = None
    baseline_difference: Optional[float] = None
    baseline_percentage: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output"""
        return {
            "pr_number": self.pr_number,
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "merged_at": self.merged_at.isoformat() if self.merged_at else None,
            "state": self.state,
            "description_analysis": {
                "ai_score": self.description_ai_score,
                "confidence": self.description_confidence,
                "patterns": self.description_patterns
            },
            "files_analysis": {
                "total_files": len(self.files),
                "total_additions": self.total_additions,
                "total_deletions": self.total_deletions,
                "high_ai_files": [
                    {
                        "filename": f.filename,
                        "ai_score": f.ai_score,
                        "additions": f.additions
                    }
                    for f in self.high_ai_files
                ]
            },
            "commits_analysis": {
                "total_commits": len(self.commits),
                "ai_style_commits": self.ai_style_commits,
                "avg_ai_score": self.avg_commit_ai_score
            },
            "overall": {
                "ai_score": self.overall_ai_score,
                "confidence": self.overall_confidence,
                "ai_assistance_level": self.ai_assistance_level.value
            },
            "baseline_comparison": {
                "repo_baseline": self.repo_baseline_score,
                "difference": self.baseline_difference,
                "percentage_higher": self.baseline_percentage
            } if self.repo_baseline_score else None
        }
    
    def format_terminal(self) -> str:
        """Format PR analysis result for terminal output"""
        lines = []
        
        lines.append(f"\n{'=' * 70}")
        lines.append(f"Pull Request Analysis: #{self.pr_number}")
        lines.append(f"{'=' * 70}\n")
        
        # PR Information
        lines.append("PR Information:")
        lines.append(f"  Title: {self.title}")
        lines.append(f"  Author: {self.author}")
        lines.append(f"  Created: {self.created_at.strftime('%Y-%m-%d')}")
        if self.merged_at:
            lines.append(f"  Merged: {self.merged_at.strftime('%Y-%m-%d')}")
        lines.append(f"  Status: {self.state}")
        
        # PR Description Analysis
        lines.append(f"\nPR Description Analysis:")
        level_color = self._get_level_indicator(self.description_ai_score)
        lines.append(f"  AI Likelihood: {self.description_ai_score:.1f}/100 {level_color}")
        lines.append(f"  Confidence: {self.description_confidence:.2f}")
        
        if self.description_patterns:
            lines.append(f"  Patterns Detected:")
            for pattern in self.description_patterns[:5]:  # Top 5
                lines.append(f"    • {pattern}")
        else:
            lines.append(f"  Patterns Detected: None (human-style description)")
        
        # Changed Files Analysis
        lines.append(f"\nChanged Files Analysis:")
        lines.append(f"  Total Files: {len(self.files)}")
        lines.append(f"  Lines Added: {self.total_additions}")
        lines.append(f"  Lines Deleted: {self.total_deletions}")
        
        # Show ALL analyzed files with scores
        analyzed_files = [f for f in self.files if f.ai_score > 0]
        if analyzed_files:
            lines.append(f"\n  File AI Likelihood Scores:")
            # Sort by score descending
            analyzed_files.sort(key=lambda f: f.ai_score, reverse=True)
            for file in analyzed_files[:10]:  # Top 10
                level_color = self._get_level_indicator(file.ai_score)
                lines.append(f"    • {file.filename}: {file.ai_score:.1f}/100 {level_color} (+{file.additions}/-{file.deletions})")
        else:
            lines.append(f"  File Analysis: No code files analyzed (binary/excluded files)")
        
        if self.high_ai_files:
            lines.append(f"\n  ⚠️  High AI Likelihood Files (>60): {len(self.high_ai_files)}")
        
        # Commit Messages Analysis
        lines.append(f"\nCommit Messages Analysis:")
        lines.append(f"  Total Commits: {len(self.commits)}")
        
        if self.commits:
            ai_pct = (self.ai_style_commits / len(self.commits) * 100) if self.commits else 0
            lines.append(f"  AI-Style Commits: {self.ai_style_commits}/{len(self.commits)} ({ai_pct:.1f}%)")
            lines.append(f"  Average AI Score: {self.avg_commit_ai_score:.1f}/100")
            
            # Show commits with AI patterns
            ai_commits = [c for c in self.commits if c.ai_score > 40]
            if ai_commits:
                lines.append(f"\n  AI-Style Commit Messages:")
                for commit in ai_commits[:5]:  # Top 5
                    msg_preview = commit.message.split('\n')[0][:60]
                    lines.append(f"    • {commit.sha[:7]}: {msg_preview}... ({commit.ai_score:.1f}/100)")
            else:
                lines.append(f"  AI-Style Commits: None detected (human-style messages)")
        else:
            lines.append(f"  No commits to analyze")
        
        # Overall Assessment
        lines.append(f"\n{'─' * 70}")
        lines.append(f"Overall Assessment:")
        lines.append(f"{'─' * 70}")
        
        level_color = self._get_level_indicator(self.overall_ai_score)
        lines.append(f"  AI Likelihood: {self.overall_ai_score:.1f}/100 {level_color}")
        lines.append(f"  AI Assistance Level: {self.ai_assistance_level.value}")
        lines.append(f"  Confidence: {self.overall_confidence:.2f}")
        
        # Score breakdown - show what contributed to the score
        lines.append(f"\n  Score Breakdown:")
        lines.append(f"    • PR Description: {self.description_ai_score:.1f}/100 (weight: 30%)")
        
        # Calculate average file score
        if analyzed_files:
            avg_file_score = sum(f.ai_score for f in analyzed_files) / len(analyzed_files)
            lines.append(f"    • Changed Files: {avg_file_score:.1f}/100 (weight: 40%, {len(analyzed_files)} files)")
        else:
            lines.append(f"    • Changed Files: N/A (no analyzable files)")
        
        lines.append(f"    • Commit Messages: {self.avg_commit_ai_score:.1f}/100 (weight: 30%, {len(self.commits)} commits)")
        
        # Interpretation
        lines.append(f"\n  Interpretation:")
        if self.overall_ai_score >= 70:
            lines.append(f"    This PR shows SUBSTANTIAL AI assistance. Multiple indicators suggest")
            lines.append(f"    significant AI tool usage in code generation, documentation, or commits.")
        elif self.overall_ai_score >= 40:
            lines.append(f"    This PR shows PARTIAL AI assistance. Some patterns suggest AI tool")
            lines.append(f"    usage, but mixed with human contributions.")
        else:
            lines.append(f"    This PR shows MINIMAL AI assistance. Patterns are consistent with")
            lines.append(f"    human-authored code and commits.")
        
        # Baseline Comparison
        if self.repo_baseline_score is not None:
            lines.append(f"\nComparison with Repository Baseline:")
            lines.append(f"  Repository Average: {self.repo_baseline_score:.1f}/100")
            lines.append(f"  This PR: {self.overall_ai_score:.1f}/100")
            
            if self.baseline_difference > 0:
                lines.append(f"  Difference: +{self.baseline_difference:.1f} points ({self.baseline_percentage:+.1f}% higher)")
                lines.append(f"  ⚠️  This PR has HIGHER AI usage than repository average")
            elif self.baseline_difference < 0:
                lines.append(f"  Difference: {self.baseline_difference:.1f} points ({self.baseline_percentage:.1f}% lower)")
                lines.append(f"  ✓ This PR has LOWER AI usage than repository average")
            else:
                lines.append(f"  Difference: No significant difference")
        
        lines.append(f"\n{'=' * 70}\n")
        
        return "\n".join(lines)
    
    def _get_level_indicator(self, score: float) -> str:
        """Get visual indicator for AI likelihood level"""
        if score >= 70:
            return "🔴 SUBSTANTIAL"
        elif score >= 40:
            return "🟡 PARTIAL"
        else:
            return "🟢 MINIMAL"


class PRAnalyzer:
    """
    Analyzes pull requests for AI-generated code.
    
    This is the unique differentiator for Vibemetric - analyzing PRs
    instead of just entire repositories.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize PR analyzer.
        
        Args:
            repo_path: Path to local git repository
        """
        self.repo_path = Path(repo_path)
        self.pattern_detector = PatternDetector()
        self.ml_detector = MLDetector()
        self.scorer = Scorer()
    
    def analyze_pr_from_data(
        self,
        pr_number: int,
        title: str,
        author: str,
        description: str,
        created_at: datetime,
        merged_at: Optional[datetime],
        state: str,
        files_data: List[Dict[str, Any]],
        commits_data: List[Dict[str, Any]],
        baseline_score: Optional[float] = None
    ) -> PRAnalysisResult:
        """
        Analyze PR from provided data (from GitHub/GitLab API).
        
        Args:
            pr_number: PR number
            title: PR title
            author: PR author
            description: PR description text
            created_at: PR creation timestamp
            merged_at: PR merge timestamp (if merged)
            state: PR state (open/closed/merged)
            files_data: List of file changes
            commits_data: List of commits
            baseline_score: Repository baseline score for comparison
            
        Returns:
            Complete PR analysis result
        """
        result = PRAnalysisResult(
            pr_number=pr_number,
            title=title,
            author=author,
            description=description,
            created_at=created_at,
            merged_at=merged_at,
            state=state
        )
        
        # 1. Analyze PR description
        desc_signal = self.pattern_detector.analyze_pr_description(description)
        result.description_ai_score = desc_signal.score
        result.description_confidence = desc_signal.confidence
        result.description_patterns = desc_signal.evidence
        
        # 2. Analyze changed files
        for file_data in files_data:
            pr_file = PRFile(
                filename=file_data["filename"],
                additions=file_data.get("additions", 0),
                deletions=file_data.get("deletions", 0),
                changes=file_data.get("changes", 0),
                patch=file_data.get("patch"),
                content=file_data.get("content")
            )
            
            # Analyze file content if available
            if pr_file.content and self._should_analyze_file(pr_file.filename):
                file_signal = self.pattern_detector.analyze_code(
                    pr_file.content,
                    language=self._detect_language(pr_file.filename)
                )
                pr_file.ai_score = file_signal.score
                pr_file.confidence = file_signal.confidence
                
                # Track high AI files (>60 score)
                if pr_file.ai_score > 60:
                    result.high_ai_files.append(pr_file)
            
            result.files.append(pr_file)
            result.total_additions += pr_file.additions
            result.total_deletions += pr_file.deletions
        
        # Sort high AI files by score
        result.high_ai_files.sort(key=lambda f: f.ai_score, reverse=True)
        
        # 3. Analyze commit messages
        for commit_data in commits_data:
            pr_commit = PRCommit(
                sha=commit_data["sha"],
                message=commit_data["message"],
                author=commit_data["author"],
                timestamp=commit_data["timestamp"]
            )
            
            # Analyze commit message
            commit_signal = self.pattern_detector.analyze_commit_message(pr_commit.message)
            pr_commit.ai_score = commit_signal.score
            pr_commit.confidence = commit_signal.confidence
            
            # Track AI-style commits (>40 score)
            if pr_commit.ai_score > 40:
                result.ai_style_commits += 1
            
            result.commits.append(pr_commit)
        
        # Calculate average commit AI score
        if result.commits:
            result.avg_commit_ai_score = sum(c.ai_score for c in result.commits) / len(result.commits)
        
        # 4. Calculate overall PR AI score
        signals = []
        
        # PR description signal (weight: 30%)
        if result.description_ai_score > 0:
            signals.append(DetectionSignal(
                layer_type=DetectionLayerType.PATTERN,
                score=result.description_ai_score,
                confidence=result.description_confidence,
                evidence=result.description_patterns,
                metadata={"source": "pr_description", "weight": 0.30}
            ))
        
        # Files signal (weight: 40%)
        if result.files:
            avg_file_score = sum(f.ai_score for f in result.files) / len(result.files)
            avg_file_confidence = sum(f.confidence for f in result.files) / len(result.files)
            signals.append(DetectionSignal(
                layer_type=DetectionLayerType.PATTERN,
                score=avg_file_score,
                confidence=avg_file_confidence,
                evidence=[f"{len(result.high_ai_files)} high-AI files detected"],
                metadata={"source": "files", "weight": 0.40}
            ))
        
        # Commits signal (weight: 30%)
        if result.commits:
            signals.append(DetectionSignal(
                layer_type=DetectionLayerType.PATTERN,
                score=result.avg_commit_ai_score,
                confidence=0.70,  # Commit analysis is fairly reliable
                evidence=[f"{result.ai_style_commits}/{len(result.commits)} AI-style commits"],
                metadata={"source": "commits", "weight": 0.30}
            ))
        
        # Calculate weighted average
        if signals:
            total_weight = sum(s.metadata.get("weight", 1.0) for s in signals)
            weighted_sum = sum(s.score * s.metadata.get("weight", 1.0) for s in signals)
            result.overall_ai_score = weighted_sum / total_weight
            
            # Calculate overall confidence
            result.overall_confidence = sum(s.confidence for s in signals) / len(signals)
            
            # Determine AI assistance level
            if result.overall_ai_score >= 70:
                result.ai_assistance_level = AIAssistanceLevel.SUBSTANTIAL
            elif result.overall_ai_score >= 40:
                result.ai_assistance_level = AIAssistanceLevel.PARTIAL
            else:
                result.ai_assistance_level = AIAssistanceLevel.MINIMAL
        
        # 5. Baseline comparison
        if baseline_score is not None:
            result.repo_baseline_score = baseline_score
            result.baseline_difference = result.overall_ai_score - baseline_score
            if baseline_score > 0:
                result.baseline_percentage = (result.baseline_difference / baseline_score) * 100
        
        return result
    
    def _should_analyze_file(self, filename: str) -> bool:
        """Check if file should be analyzed (exclude binaries, generated files)"""
        # Exclude patterns
        exclude_patterns = [
            r'\.min\.js$',
            r'\.min\.css$',
            r'\.map$',
            r'\.lock$',
            r'package-lock\.json$',
            r'yarn\.lock$',
            r'Pipfile\.lock$',
            r'poetry\.lock$',
            r'\.svg$',
            r'\.png$',
            r'\.jpg$',
            r'\.gif$',
            r'\.ico$',
            r'\.woff',
            r'\.ttf$',
            r'\.eot$',
            r'_pb2\.py$',
            r'_pb2_grpc\.py$',
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return False
        
        return True
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
        }
        
        ext = Path(filename).suffix.lower()
        return ext_map.get(ext, 'unknown')
