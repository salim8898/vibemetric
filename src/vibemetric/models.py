"""
Core Data Models for Vibemetric

This module defines all data structures used throughout the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class AIAssistanceLevel(Enum):
    """Level of AI assistance detected in code"""

    MINIMAL = "MINIMAL"  # 0-40% AI likelihood - Primarily human-authored
    PARTIAL = "PARTIAL"  # 40-70% AI likelihood - Mixed human-AI collaboration
    SUBSTANTIAL = "SUBSTANTIAL"  # 70-100% AI likelihood - Significant AI contribution


class DetectionLayerType(Enum):
    """Types of detection layers"""

    ARTIFACT = "artifact"
    VELOCITY = "velocity"
    PATTERN = "pattern"
    ML = "ml"


@dataclass
class DetectionSignal:
    """Signal from a single detection layer"""

    layer_type: DetectionLayerType
    score: float  # 0-100
    confidence: float  # 0-1
    evidence: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VibeScore:
    """Combined AI likelihood score"""

    overall_score: float  # 0-100
    confidence: float  # 0-1
    ai_assistance_level: AIAssistanceLevel
    contributing_signals: list[DetectionSignal] = field(default_factory=list)

    def __post_init__(self):
        """Validate score bounds"""
        assert 0 <= self.overall_score <= 100, "Score must be between 0 and 100"
        assert 0 <= self.confidence <= 1, "Confidence must be between 0 and 1"


@dataclass
class Artifact:
    """AI tool artifact detected in repository"""

    id: UUID = field(default_factory=uuid4)
    tool_name: str = ""
    file_path: str = ""
    adoption_date: Optional[datetime] = None
    authors: list[str] = field(default_factory=list)
    confidence: float = 0.9


@dataclass
class Commit:
    """Git commit information"""

    id: UUID = field(default_factory=uuid4)
    commit_hash: str = ""
    author: str = ""
    email: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    message: str = ""
    lines_added: int = 0
    lines_deleted: int = 0
    files_changed: list[str] = field(default_factory=list)
    ai_likelihood_score: Optional[float] = None
    confidence: Optional[float] = None
    velocity_ratio: Optional[float] = None


@dataclass
class PullRequest:
    """Pull request information"""

    id: UUID = field(default_factory=uuid4)
    pr_number: int = 0
    title: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    merged_at: Optional[datetime] = None
    lines_added: int = 0
    lines_deleted: int = 0
    files_changed: int = 0
    ai_likelihood_score: Optional[float] = None
    confidence: Optional[float] = None
    risk_level: Optional[AIAssistanceLevel] = None
    detection_signals: list[DetectionSignal] = field(default_factory=list)
    time_to_merge: Optional[int] = None  # seconds
    review_cycles: Optional[int] = None


@dataclass
class Developer:
    """Developer profile"""

    id: UUID = field(default_factory=uuid4)
    username: str = ""
    email: str = ""
    name: str = ""
    ai_tools: list[str] = field(default_factory=list)
    ai_adoption_date: Optional[datetime] = None
    total_commits: int = 0
    ai_assisted_commits: int = 0
    ai_adoption_rate: float = 0.0
    velocity_before_ai: Optional[float] = None
    velocity_after_ai: Optional[float] = None
    velocity_improvement: Optional[float] = None


@dataclass
class Repository:
    """Repository information"""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    url: str = ""
    platform: str = ""  # 'github', 'gitlab', 'local'
    owner: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_scanned_at: Optional[datetime] = None
    total_commits: int = 0
    total_prs: int = 0
    ai_adoption_rate: float = 0.0
    detected_tools: list[str] = field(default_factory=list)


@dataclass
class ScanResult:
    """Complete scan result for a repository"""

    repository: Repository
    scan_timestamp: datetime = field(default_factory=datetime.now)
    total_files_scanned: int = 0
    total_lines_analyzed: int = 0
    overall_vibe_score: Optional[VibeScore] = None
    artifacts: list[Artifact] = field(default_factory=list)
    pull_requests: list[PullRequest] = field(default_factory=list)
    commits: list[Commit] = field(default_factory=list)
    developers: list[Developer] = field(default_factory=list)
    ai_generated_lines: int = 0
    human_written_lines: int = 0
    scan_duration: float = 0.0  # seconds
