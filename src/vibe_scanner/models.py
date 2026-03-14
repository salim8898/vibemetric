"""
Core data models for vibe-scanner.

This module contains all data model classes with validation rules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# Enums

class OutputFormat(Enum):
    """Output format options for reports."""
    TERMINAL = "terminal"
    JSON = "json"
    MARKDOWN = "markdown"


class RiskLevel(Enum):
    """Risk level classification based on vibe score."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SignalType(Enum):
    """Types of detection signals."""
    PATTERN = "PATTERN"
    STATISTICAL = "STATISTICAL"
    STYLE = "STYLE"
    GIT = "GIT"
    CUSTOM = "CUSTOM"


# Supporting Models

@dataclass
class PatternMatch:
    """Represents a detected AI code pattern."""
    pattern_name: str
    line_number: int
    confidence: float
    description: str
    matched_text: str
    
    def __post_init__(self):
        """Validate pattern match data."""
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        if self.line_number < 0:
            raise ValueError(f"Line number must be non-negative, got {self.line_number}")


@dataclass
class StatisticalMetrics:
    """Statistical analysis metrics for code."""
    perplexity_score: float
    predictability_score: float
    token_distribution_score: float
    anomaly_score: float
    
    def __post_init__(self):
        """Validate statistical metrics are normalized."""
        for field_name in ['perplexity_score', 'predictability_score', 
                          'token_distribution_score', 'anomaly_score']:
            value = getattr(self, field_name)
            if not 0 <= value <= 100:
                raise ValueError(f"{field_name} must be between 0 and 100, got {value}")


@dataclass
class StyleMetrics:
    """Coding style analysis metrics."""
    indentation_consistency: float
    naming_convention_score: float
    line_length_variance: float
    comment_density: float
    whitespace_consistency: float
    
    def __post_init__(self):
        """Validate style metrics are normalized."""
        for field_name in ['indentation_consistency', 'naming_convention_score',
                          'line_length_variance', 'comment_density', 'whitespace_consistency']:
            value = getattr(self, field_name)
            if not 0 <= value <= 100:
                raise ValueError(f"{field_name} must be between 0 and 100, got {value}")


@dataclass
class GitMetrics:
    """Git metadata analysis metrics."""
    authoring_speed_lpm: float  # lines per minute
    commit_size_avg: float
    commit_interval_avg: float  # seconds
    unusual_speed_detected: bool
    unusual_timing_detected: bool
    total_commits: int
    
    def __post_init__(self):
        """Validate git metrics."""
        if self.authoring_speed_lpm < 0:
            raise ValueError(f"Authoring speed must be non-negative, got {self.authoring_speed_lpm}")
        if self.commit_size_avg < 0:
            raise ValueError(f"Commit size average must be non-negative, got {self.commit_size_avg}")
        if self.commit_interval_avg < 0:
            raise ValueError(f"Commit interval average must be non-negative, got {self.commit_interval_avg}")
        if self.total_commits < 0:
            raise ValueError(f"Total commits must be non-negative, got {self.total_commits}")


@dataclass
class Evidence:
    """Evidence supporting a detection signal."""
    evidence_type: str
    score: float
    details: Any = None
    
    def __post_init__(self):
        """Validate evidence data."""
        if not 0 <= self.score <= 100:
            raise ValueError(f"Evidence score must be between 0 and 100, got {self.score}")


@dataclass
class LineScore:
    """Vibe score for a specific line of code."""
    line_number: int
    score: float
    confidence: float
    
    def __post_init__(self):
        """Validate line score bounds."""
        if self.line_number < 0:
            raise ValueError(f"Line number must be non-negative, got {self.line_number}")
        if not 0 <= self.score <= 100:
            raise ValueError(f"Line score must be between 0 and 100, got {self.score}")
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")


# Main Models

@dataclass
class ScanConfig:
    """Configuration for repository scanning."""
    repo_path: str
    include_patterns: List[str] = field(default_factory=lambda: ["**/*"])
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/venv/**",
        "**/.git/**"
    ])
    file_extensions: List[str] = field(default_factory=lambda: [
        ".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c", ".rb", ".php"
    ])
    max_file_size: int = 1024  # KB
    parallel_workers: int = 1
    enable_git_analysis: bool = True
    output_format: OutputFormat = OutputFormat.TERMINAL
    verbosity: int = 0
    
    def __post_init__(self):
        """Validate scan configuration."""
        import os
        import multiprocessing
        
        # Validate repo_path exists and is readable
        if not os.path.exists(self.repo_path):
            raise ValueError(f"Repository path does not exist: {self.repo_path}")
        if not os.access(self.repo_path, os.R_OK):
            raise ValueError(f"Repository path is not readable: {self.repo_path}")
        
        # Validate max_file_size is positive
        if self.max_file_size <= 0:
            raise ValueError(f"max_file_size must be positive, got {self.max_file_size}")
        
        # Validate parallel_workers is within valid range
        cpu_count = multiprocessing.cpu_count()
        if not 1 <= self.parallel_workers <= cpu_count:
            raise ValueError(
                f"parallel_workers must be between 1 and {cpu_count}, got {self.parallel_workers}"
            )
        
        # Validate output_format is valid enum
        if not isinstance(self.output_format, OutputFormat):
            raise ValueError(f"output_format must be OutputFormat enum, got {type(self.output_format)}")


@dataclass
class DetectionSignal:
    """A detection signal from an analyzer."""
    signal_type: SignalType
    signal_name: str
    score: float  # 0-100
    confidence: float  # 0-1
    weight: float  # 0-1
    evidence: List[Evidence]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate detection signal."""
        # Validate score bounds
        if not 0 <= self.score <= 100:
            raise ValueError(f"Score must be between 0 and 100, got {self.score}")
        
        # Validate confidence bounds
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        
        # Validate weight bounds
        if not 0 <= self.weight <= 1:
            raise ValueError(f"Weight must be between 0 and 1, got {self.weight}")
        
        # Validate signal_type is valid enum
        if not isinstance(self.signal_type, SignalType):
            raise ValueError(f"signal_type must be SignalType enum, got {type(self.signal_type)}")
        
        # Validate evidence list is not empty
        if not self.evidence:
            raise ValueError("Evidence list must not be empty")


@dataclass
class VibeScore:
    """Vibe score indicating AI-generation likelihood."""
    overall_score: float  # 0-100
    confidence: float  # 0-1
    contributing_signals: Dict[str, float]
    risk_level: RiskLevel
    explanation: str
    line_scores: Optional[List[LineScore]] = None
    
    def __post_init__(self):
        """Validate vibe score and ensure risk level consistency."""
        # Validate overall_score bounds
        if not 0 <= self.overall_score <= 100:
            raise ValueError(f"overall_score must be between 0 and 100, got {self.overall_score}")
        
        # Validate confidence bounds
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        
        # Validate risk_level is valid enum
        if not isinstance(self.risk_level, RiskLevel):
            raise ValueError(f"risk_level must be RiskLevel enum, got {type(self.risk_level)}")
        
        # Validate risk level consistency with score
        if self.overall_score < 30 and self.risk_level != RiskLevel.LOW:
            raise ValueError(
                f"Risk level must be LOW for score < 30, got {self.risk_level} with score {self.overall_score}"
            )
        if 30 <= self.overall_score < 70 and self.risk_level != RiskLevel.MEDIUM:
            raise ValueError(
                f"Risk level must be MEDIUM for score 30-70, got {self.risk_level} with score {self.overall_score}"
            )
        if self.overall_score >= 70 and self.risk_level != RiskLevel.HIGH:
            raise ValueError(
                f"Risk level must be HIGH for score >= 70, got {self.risk_level} with score {self.overall_score}"
            )
        
        # Validate line_scores if present
        if self.line_scores is not None:
            for line_score in self.line_scores:
                if not isinstance(line_score, LineScore):
                    raise ValueError(f"All line_scores must be LineScore instances")


@dataclass
class FileAnalysisResult:
    """Analysis result for a single file."""
    file_path: str
    language: str
    total_lines: int
    code_lines: int
    vibe_score: VibeScore
    pattern_matches: List[PatternMatch]
    statistical_metrics: StatisticalMetrics
    style_metrics: StyleMetrics
    git_metrics: Optional[GitMetrics]
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate file analysis result."""
        # Validate file_path is not empty
        if not self.file_path:
            raise ValueError("file_path must not be empty")
        
        # Validate total_lines >= code_lines
        if self.total_lines < self.code_lines:
            raise ValueError(
                f"total_lines ({self.total_lines}) must be >= code_lines ({self.code_lines})"
            )
        
        # Validate code_lines is non-negative
        if self.code_lines < 0:
            raise ValueError(f"code_lines must be non-negative, got {self.code_lines}")
        
        # Validate language is not empty
        if not self.language:
            raise ValueError("language must not be empty")
        
        # Validate vibe_score is VibeScore instance
        if not isinstance(self.vibe_score, VibeScore):
            raise ValueError(f"vibe_score must be VibeScore instance, got {type(self.vibe_score)}")


@dataclass
class RiskSummary:
    """Summary of risk levels across analyzed files."""
    high_risk_files: int
    medium_risk_files: int
    low_risk_files: int
    critical_files_affected: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate risk summary."""
        if self.high_risk_files < 0:
            raise ValueError(f"high_risk_files must be non-negative, got {self.high_risk_files}")
        if self.medium_risk_files < 0:
            raise ValueError(f"medium_risk_files must be non-negative, got {self.medium_risk_files}")
        if self.low_risk_files < 0:
            raise ValueError(f"low_risk_files must be non-negative, got {self.low_risk_files}")


@dataclass
class ScanResult:
    """Complete scan result for a repository."""
    repo_path: str
    scan_timestamp: datetime
    total_files_scanned: int
    total_lines_analyzed: int
    overall_vibe_score: VibeScore
    file_results: List[FileAnalysisResult]
    ai_generated_lines: int
    human_written_lines: int
    risk_summary: RiskSummary
    scan_duration: float
    
    def __post_init__(self):
        """Validate scan result consistency."""
        # Validate total_files_scanned matches file_results length
        if self.total_files_scanned != len(self.file_results):
            raise ValueError(
                f"total_files_scanned ({self.total_files_scanned}) must equal "
                f"length of file_results ({len(self.file_results)})"
            )
        
        # Validate total_lines_analyzed matches sum of file code_lines
        expected_total_lines = sum(f.code_lines for f in self.file_results)
        if self.total_lines_analyzed != expected_total_lines:
            raise ValueError(
                f"total_lines_analyzed ({self.total_lines_analyzed}) must equal "
                f"sum of file code_lines ({expected_total_lines})"
            )
        
        # Validate line classification completeness
        if self.ai_generated_lines + self.human_written_lines != self.total_lines_analyzed:
            raise ValueError(
                f"ai_generated_lines ({self.ai_generated_lines}) + "
                f"human_written_lines ({self.human_written_lines}) must equal "
                f"total_lines_analyzed ({self.total_lines_analyzed})"
            )
        
        # Validate scan_duration is positive
        if self.scan_duration <= 0:
            raise ValueError(f"scan_duration must be positive, got {self.scan_duration}")
        
        # Validate overall_vibe_score is VibeScore instance
        if not isinstance(self.overall_vibe_score, VibeScore):
            raise ValueError(
                f"overall_vibe_score must be VibeScore instance, got {type(self.overall_vibe_score)}"
            )
        
        # Validate risk_summary is RiskSummary instance
        if not isinstance(self.risk_summary, RiskSummary):
            raise ValueError(
                f"risk_summary must be RiskSummary instance, got {type(self.risk_summary)}"
            )
