"""
Unit tests for vibe-scanner data models.

Tests validation rules and data model behavior.
"""

import pytest
from datetime import datetime
from src.vibe_scanner.models import (
    OutputFormat,
    RiskLevel,
    SignalType,
    PatternMatch,
    StatisticalMetrics,
    StyleMetrics,
    GitMetrics,
    Evidence,
    LineScore,
    ScanConfig,
    DetectionSignal,
    VibeScore,
    FileAnalysisResult,
    RiskSummary,
    ScanResult,
)


class TestPatternMatch:
    """Tests for PatternMatch model."""
    
    def test_valid_pattern_match(self):
        """Test creating a valid pattern match."""
        pm = PatternMatch(
            pattern_name="AI_COMMENT",
            line_number=10,
            confidence=0.85,
            description="AI-style comment detected",
            matched_text="# This is a comment"
        )
        assert pm.pattern_name == "AI_COMMENT"
        assert pm.confidence == 0.85
    
    def test_invalid_confidence_bounds(self):
        """Test that confidence must be between 0 and 1."""
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            PatternMatch(
                pattern_name="TEST",
                line_number=1,
                confidence=1.5,
                description="test",
                matched_text="test"
            )
    
    def test_negative_line_number(self):
        """Test that line number must be non-negative."""
        with pytest.raises(ValueError, match="Line number must be non-negative"):
            PatternMatch(
                pattern_name="TEST",
                line_number=-1,
                confidence=0.5,
                description="test",
                matched_text="test"
            )


class TestStatisticalMetrics:
    """Tests for StatisticalMetrics model."""
    
    def test_valid_statistical_metrics(self):
        """Test creating valid statistical metrics."""
        sm = StatisticalMetrics(
            perplexity_score=45.0,
            predictability_score=60.0,
            token_distribution_score=55.0,
            anomaly_score=40.0
        )
        assert sm.perplexity_score == 45.0
    
    def test_score_out_of_bounds(self):
        """Test that scores must be between 0 and 100."""
        with pytest.raises(ValueError, match="must be between 0 and 100"):
            StatisticalMetrics(
                perplexity_score=150.0,
                predictability_score=60.0,
                token_distribution_score=55.0,
                anomaly_score=40.0
            )


class TestStyleMetrics:
    """Tests for StyleMetrics model."""
    
    def test_valid_style_metrics(self):
        """Test creating valid style metrics."""
        sm = StyleMetrics(
            indentation_consistency=90.0,
            naming_convention_score=85.0,
            line_length_variance=70.0,
            comment_density=60.0,
            whitespace_consistency=95.0
        )
        assert sm.indentation_consistency == 90.0


class TestGitMetrics:
    """Tests for GitMetrics model."""
    
    def test_valid_git_metrics(self):
        """Test creating valid git metrics."""
        gm = GitMetrics(
            authoring_speed_lpm=150.0,
            commit_size_avg=200.0,
            commit_interval_avg=300.0,
            unusual_speed_detected=True,
            unusual_timing_detected=False,
            total_commits=10
        )
        assert gm.authoring_speed_lpm == 150.0
    
    def test_negative_values_rejected(self):
        """Test that negative values are rejected."""
        with pytest.raises(ValueError, match="must be non-negative"):
            GitMetrics(
                authoring_speed_lpm=-10.0,
                commit_size_avg=200.0,
                commit_interval_avg=300.0,
                unusual_speed_detected=False,
                unusual_timing_detected=False,
                total_commits=10
            )


class TestVibeScore:
    """Tests for VibeScore model."""
    
    def test_valid_low_risk_score(self):
        """Test creating a valid low risk vibe score."""
        vs = VibeScore(
            overall_score=25.0,
            confidence=0.8,
            contributing_signals={"pattern": 20.0, "statistical": 30.0},
            risk_level=RiskLevel.LOW,
            explanation="Low AI likelihood"
        )
        assert vs.overall_score == 25.0
        assert vs.risk_level == RiskLevel.LOW
    
    def test_valid_medium_risk_score(self):
        """Test creating a valid medium risk vibe score."""
        vs = VibeScore(
            overall_score=50.0,
            confidence=0.85,
            contributing_signals={"pattern": 50.0},
            risk_level=RiskLevel.MEDIUM,
            explanation="Medium AI likelihood"
        )
        assert vs.risk_level == RiskLevel.MEDIUM
    
    def test_valid_high_risk_score(self):
        """Test creating a valid high risk vibe score."""
        vs = VibeScore(
            overall_score=85.0,
            confidence=0.9,
            contributing_signals={"pattern": 85.0},
            risk_level=RiskLevel.HIGH,
            explanation="High AI likelihood"
        )
        assert vs.risk_level == RiskLevel.HIGH
    
    def test_score_bounds_validation(self):
        """Test that overall_score must be between 0 and 100."""
        with pytest.raises(ValueError, match="overall_score must be between 0 and 100"):
            VibeScore(
                overall_score=150.0,
                confidence=0.8,
                contributing_signals={},
                risk_level=RiskLevel.HIGH,
                explanation="test"
            )
    
    def test_confidence_bounds_validation(self):
        """Test that confidence must be between 0 and 1."""
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            VibeScore(
                overall_score=50.0,
                confidence=1.5,
                contributing_signals={},
                risk_level=RiskLevel.MEDIUM,
                explanation="test"
            )
    
    def test_risk_level_consistency_low(self):
        """Test that risk level must be LOW for score < 30."""
        with pytest.raises(ValueError, match="Risk level must be LOW"):
            VibeScore(
                overall_score=25.0,
                confidence=0.8,
                contributing_signals={},
                risk_level=RiskLevel.MEDIUM,
                explanation="test"
            )
    
    def test_risk_level_consistency_medium(self):
        """Test that risk level must be MEDIUM for score 30-70."""
        with pytest.raises(ValueError, match="Risk level must be MEDIUM"):
            VibeScore(
                overall_score=50.0,
                confidence=0.8,
                contributing_signals={},
                risk_level=RiskLevel.LOW,
                explanation="test"
            )
    
    def test_risk_level_consistency_high(self):
        """Test that risk level must be HIGH for score >= 70."""
        with pytest.raises(ValueError, match="Risk level must be HIGH"):
            VibeScore(
                overall_score=75.0,
                confidence=0.8,
                contributing_signals={},
                risk_level=RiskLevel.MEDIUM,
                explanation="test"
            )
    
    def test_boundary_score_30(self):
        """Test boundary at score 30 (should be MEDIUM)."""
        vs = VibeScore(
            overall_score=30.0,
            confidence=0.8,
            contributing_signals={},
            risk_level=RiskLevel.MEDIUM,
            explanation="test"
        )
        assert vs.risk_level == RiskLevel.MEDIUM
    
    def test_boundary_score_70(self):
        """Test boundary at score 70 (should be HIGH)."""
        vs = VibeScore(
            overall_score=70.0,
            confidence=0.8,
            contributing_signals={},
            risk_level=RiskLevel.HIGH,
            explanation="test"
        )
        assert vs.risk_level == RiskLevel.HIGH


class TestDetectionSignal:
    """Tests for DetectionSignal model."""
    
    def test_valid_detection_signal(self):
        """Test creating a valid detection signal."""
        evidence = [Evidence("TEST", 50.0)]
        ds = DetectionSignal(
            signal_type=SignalType.PATTERN,
            signal_name="pattern_detector",
            score=75.0,
            confidence=0.85,
            weight=0.3,
            evidence=evidence
        )
        assert ds.score == 75.0
        assert ds.signal_type == SignalType.PATTERN
    
    def test_empty_evidence_rejected(self):
        """Test that evidence list cannot be empty."""
        with pytest.raises(ValueError, match="Evidence list must not be empty"):
            DetectionSignal(
                signal_type=SignalType.PATTERN,
                signal_name="test",
                score=50.0,
                confidence=0.8,
                weight=0.3,
                evidence=[]
            )
    
    def test_score_bounds(self):
        """Test that score must be between 0 and 100."""
        evidence = [Evidence("TEST", 50.0)]
        with pytest.raises(ValueError, match="Score must be between 0 and 100"):
            DetectionSignal(
                signal_type=SignalType.PATTERN,
                signal_name="test",
                score=150.0,
                confidence=0.8,
                weight=0.3,
                evidence=evidence
            )


class TestScanConfig:
    """Tests for ScanConfig model."""
    
    def test_valid_scan_config(self, tmp_path):
        """Test creating a valid scan config."""
        config = ScanConfig(
            repo_path=str(tmp_path),
            max_file_size=2048,
            parallel_workers=2
        )
        assert config.max_file_size == 2048
        assert config.parallel_workers == 2
    
    def test_nonexistent_path_rejected(self):
        """Test that nonexistent paths are rejected."""
        with pytest.raises(ValueError, match="Repository path does not exist"):
            ScanConfig(repo_path="/nonexistent/path")
    
    def test_negative_max_file_size_rejected(self, tmp_path):
        """Test that negative max_file_size is rejected."""
        with pytest.raises(ValueError, match="max_file_size must be positive"):
            ScanConfig(
                repo_path=str(tmp_path),
                max_file_size=-100
            )


class TestFileAnalysisResult:
    """Tests for FileAnalysisResult model."""
    
    def test_valid_file_analysis_result(self):
        """Test creating a valid file analysis result."""
        vibe_score = VibeScore(
            overall_score=60.0,
            confidence=0.8,
            contributing_signals={},
            risk_level=RiskLevel.MEDIUM,
            explanation="test"
        )
        stat_metrics = StatisticalMetrics(50.0, 50.0, 50.0, 50.0)
        style_metrics = StyleMetrics(50.0, 50.0, 50.0, 50.0, 50.0)
        
        result = FileAnalysisResult(
            file_path="test.py",
            language="python",
            total_lines=100,
            code_lines=80,
            vibe_score=vibe_score,
            pattern_matches=[],
            statistical_metrics=stat_metrics,
            style_metrics=style_metrics,
            git_metrics=None
        )
        assert result.file_path == "test.py"
        assert result.total_lines == 100
    
    def test_total_lines_less_than_code_lines_rejected(self):
        """Test that total_lines must be >= code_lines."""
        vibe_score = VibeScore(
            overall_score=60.0,
            confidence=0.8,
            contributing_signals={},
            risk_level=RiskLevel.MEDIUM,
            explanation="test"
        )
        stat_metrics = StatisticalMetrics(50.0, 50.0, 50.0, 50.0)
        style_metrics = StyleMetrics(50.0, 50.0, 50.0, 50.0, 50.0)
        
        with pytest.raises(ValueError, match="total_lines.*must be >= code_lines"):
            FileAnalysisResult(
                file_path="test.py",
                language="python",
                total_lines=50,
                code_lines=100,
                vibe_score=vibe_score,
                pattern_matches=[],
                statistical_metrics=stat_metrics,
                style_metrics=style_metrics,
                git_metrics=None
            )


class TestScanResult:
    """Tests for ScanResult model."""
    
    def test_valid_scan_result(self):
        """Test creating a valid scan result."""
        vibe_score = VibeScore(
            overall_score=60.0,
            confidence=0.8,
            contributing_signals={},
            risk_level=RiskLevel.MEDIUM,
            explanation="test"
        )
        stat_metrics = StatisticalMetrics(50.0, 50.0, 50.0, 50.0)
        style_metrics = StyleMetrics(50.0, 50.0, 50.0, 50.0, 50.0)
        
        file_result = FileAnalysisResult(
            file_path="test.py",
            language="python",
            total_lines=100,
            code_lines=80,
            vibe_score=vibe_score,
            pattern_matches=[],
            statistical_metrics=stat_metrics,
            style_metrics=style_metrics,
            git_metrics=None
        )
        
        risk_summary = RiskSummary(
            high_risk_files=0,
            medium_risk_files=1,
            low_risk_files=0
        )
        
        result = ScanResult(
            repo_path="/test/repo",
            scan_timestamp=datetime.now(),
            total_files_scanned=1,
            total_lines_analyzed=80,
            overall_vibe_score=vibe_score,
            file_results=[file_result],
            ai_generated_lines=50,
            human_written_lines=30,
            risk_summary=risk_summary,
            scan_duration=2.5
        )
        assert result.total_files_scanned == 1
        assert result.total_lines_analyzed == 80
    
    def test_file_count_mismatch_rejected(self):
        """Test that total_files_scanned must match file_results length."""
        vibe_score = VibeScore(
            overall_score=60.0,
            confidence=0.8,
            contributing_signals={},
            risk_level=RiskLevel.MEDIUM,
            explanation="test"
        )
        risk_summary = RiskSummary(0, 0, 0)
        
        with pytest.raises(ValueError, match="total_files_scanned.*must equal"):
            ScanResult(
                repo_path="/test",
                scan_timestamp=datetime.now(),
                total_files_scanned=5,
                total_lines_analyzed=0,
                overall_vibe_score=vibe_score,
                file_results=[],
                ai_generated_lines=0,
                human_written_lines=0,
                risk_summary=risk_summary,
                scan_duration=1.0
            )
    
    def test_line_classification_completeness(self):
        """Test that ai_generated_lines + human_written_lines = total_lines_analyzed."""
        vibe_score = VibeScore(
            overall_score=60.0,
            confidence=0.8,
            contributing_signals={},
            risk_level=RiskLevel.MEDIUM,
            explanation="test"
        )
        stat_metrics = StatisticalMetrics(50.0, 50.0, 50.0, 50.0)
        style_metrics = StyleMetrics(50.0, 50.0, 50.0, 50.0, 50.0)
        
        file_result = FileAnalysisResult(
            file_path="test.py",
            language="python",
            total_lines=100,
            code_lines=100,
            vibe_score=vibe_score,
            pattern_matches=[],
            statistical_metrics=stat_metrics,
            style_metrics=style_metrics,
            git_metrics=None
        )
        risk_summary = RiskSummary(0, 1, 0)
        
        with pytest.raises(ValueError, match="ai_generated_lines.*human_written_lines.*must equal"):
            ScanResult(
                repo_path="/test",
                scan_timestamp=datetime.now(),
                total_files_scanned=1,
                total_lines_analyzed=100,
                overall_vibe_score=vibe_score,
                file_results=[file_result],
                ai_generated_lines=50,
                human_written_lines=30,  # Should be 50 to sum to 100
                risk_summary=risk_summary,
                scan_duration=1.0
            )
