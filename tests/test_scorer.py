"""
Tests for Score Combination Engine
"""

from src.vibemetric.models import AIAssistanceLevel, DetectionLayerType, DetectionSignal, VibeScore
from src.vibemetric.scorer import Scorer


class TestScorer:
    """Test suite for Scorer"""

    def test_null_score_with_empty_signals(self):
        """Test that empty signals return null score"""
        scorer = Scorer()
        vibe_score = scorer.calculate_vibe_score([])

        assert vibe_score.overall_score == 0.0
        assert vibe_score.confidence == 0.0
        assert vibe_score.ai_assistance_level == AIAssistanceLevel.MINIMAL
        assert len(vibe_score.contributing_signals) == 0

    def test_single_high_artifact_signal(self):
        """Test scoring with single high artifact signal"""
        scorer = Scorer()

        signal = DetectionSignal(
            layer_type=DetectionLayerType.ARTIFACT,
            score=90.0,
            confidence=0.9,
            evidence=["Detected Cursor (.cursorrules)"],
        )

        vibe_score = scorer.calculate_vibe_score([signal])

        assert vibe_score.overall_score == 90.0
        assert vibe_score.confidence == 0.9
        assert vibe_score.ai_assistance_level == AIAssistanceLevel.SUBSTANTIAL
        assert len(vibe_score.contributing_signals) == 1

    def test_multiple_signals_weighted_average(self):
        """Test weighted averaging of multiple signals"""
        scorer = Scorer()

        signals = [
            DetectionSignal(
                layer_type=DetectionLayerType.ARTIFACT,
                score=80.0,
                confidence=0.9,
                evidence=["Tool detected"],
            ),
            DetectionSignal(
                layer_type=DetectionLayerType.VELOCITY,
                score=60.0,
                confidence=0.8,
                evidence=["Velocity spike"],
            ),
            DetectionSignal(
                layer_type=DetectionLayerType.PATTERN,
                score=70.0,
                confidence=0.7,
                evidence=["AI patterns"],
            ),
        ]

        vibe_score = scorer.calculate_vibe_score(signals)

        # Weighted by both layer importance and confidence
        # Artifact (80) has highest weight and confidence, pulls score up
        assert 70.0 <= vibe_score.overall_score <= 75.0
        assert (
            vibe_score.ai_assistance_level == AIAssistanceLevel.SUBSTANTIAL
        )  # Score ~72 = SUBSTANTIAL
        assert len(vibe_score.contributing_signals) == 3

    def test_all_four_layers(self):
        """Test scoring with all 4 detection layers"""
        scorer = Scorer()

        signals = [
            DetectionSignal(
                layer_type=DetectionLayerType.ARTIFACT,
                score=90.0,
                confidence=0.9,
                evidence=["Cursor detected"],
            ),
            DetectionSignal(
                layer_type=DetectionLayerType.VELOCITY,
                score=80.0,
                confidence=0.82,
                evidence=["2.5x velocity increase"],
            ),
            DetectionSignal(
                layer_type=DetectionLayerType.PATTERN,
                score=75.0,
                confidence=0.7,
                evidence=["AI code patterns"],
            ),
            DetectionSignal(
                layer_type=DetectionLayerType.ML,
                score=85.0,
                confidence=0.85,
                evidence=["ML prediction: 85% AI"],
            ),
        ]

        vibe_score = scorer.calculate_vibe_score(signals)

        # All layers agree on high AI likelihood
        assert vibe_score.overall_score >= 80.0
        assert vibe_score.ai_assistance_level == AIAssistanceLevel.SUBSTANTIAL
        assert vibe_score.confidence >= 0.8  # High confidence with 4 layers
        assert len(vibe_score.contributing_signals) == 4

    def test_null_signals_filtered_out(self):
        """Test that null signals (score=0, confidence=0) are filtered"""
        scorer = Scorer()

        signals = [
            DetectionSignal(
                layer_type=DetectionLayerType.ARTIFACT,
                score=70.0,
                confidence=0.9,
                evidence=["Tool detected"],
            ),
            DetectionSignal(
                layer_type=DetectionLayerType.VELOCITY, score=0.0, confidence=0.0, evidence=[]
            ),
            DetectionSignal(
                layer_type=DetectionLayerType.ML,
                score=0.0,
                confidence=0.0,
                evidence=["Model not available"],
            ),
        ]

        vibe_score = scorer.calculate_vibe_score(signals)

        # Should only use artifact signal
        assert vibe_score.overall_score == 70.0
        assert vibe_score.ai_assistance_level == AIAssistanceLevel.SUBSTANTIAL

    def test_assistance_level_boundaries(self):
        """Test AI assistance level classification boundaries"""
        scorer = Scorer()

        # Test MINIMAL (0-40)
        signal_minimal = DetectionSignal(
            layer_type=DetectionLayerType.PATTERN, score=30.0, confidence=0.6, evidence=[]
        )
        vibe_minimal = scorer.calculate_vibe_score([signal_minimal])
        assert vibe_minimal.ai_assistance_level == AIAssistanceLevel.MINIMAL

        # Test PARTIAL (40-70)
        signal_partial = DetectionSignal(
            layer_type=DetectionLayerType.PATTERN, score=55.0, confidence=0.6, evidence=[]
        )
        vibe_partial = scorer.calculate_vibe_score([signal_partial])
        assert vibe_partial.ai_assistance_level == AIAssistanceLevel.PARTIAL

        # Test SUBSTANTIAL (70-100)
        signal_substantial = DetectionSignal(
            layer_type=DetectionLayerType.ARTIFACT, score=85.0, confidence=0.9, evidence=[]
        )
        vibe_substantial = scorer.calculate_vibe_score([signal_substantial])
        assert vibe_substantial.ai_assistance_level == AIAssistanceLevel.SUBSTANTIAL

    def test_confidence_boost_with_multiple_layers(self):
        """Test that confidence increases with more agreeing layers"""
        scorer = Scorer()

        # Single layer
        single_signal = [
            DetectionSignal(
                layer_type=DetectionLayerType.PATTERN, score=60.0, confidence=0.7, evidence=[]
            )
        ]
        vibe_single = scorer.calculate_vibe_score(single_signal)

        # Three layers
        three_signals = [
            DetectionSignal(
                layer_type=DetectionLayerType.ARTIFACT, score=60.0, confidence=0.7, evidence=[]
            ),
            DetectionSignal(
                layer_type=DetectionLayerType.VELOCITY, score=60.0, confidence=0.7, evidence=[]
            ),
            DetectionSignal(
                layer_type=DetectionLayerType.PATTERN, score=60.0, confidence=0.7, evidence=[]
            ),
        ]
        vibe_three = scorer.calculate_vibe_score(three_signals)

        # Three layers should have higher confidence
        assert vibe_three.confidence > vibe_single.confidence

    def test_interpretation_substantial_assistance(self):
        """Test interpretation for substantial AI assistance"""
        scorer = Scorer()

        vibe_score = VibeScore(
            overall_score=85.0,
            confidence=0.9,
            ai_assistance_level=AIAssistanceLevel.SUBSTANTIAL,
            contributing_signals=[],
        )

        interpretation = scorer.get_interpretation(vibe_score)

        assert "SUBSTANTIAL" in interpretation
        assert "85.0" in interpretation
        assert "AI" in interpretation

    def test_interpretation_partial_assistance(self):
        """Test interpretation for partial AI assistance"""
        scorer = Scorer()

        vibe_score = VibeScore(
            overall_score=55.0,
            confidence=0.7,
            ai_assistance_level=AIAssistanceLevel.PARTIAL,
            contributing_signals=[],
        )

        interpretation = scorer.get_interpretation(vibe_score)

        assert "PARTIAL" in interpretation
        assert "55.0" in interpretation

    def test_interpretation_minimal_assistance(self):
        """Test interpretation for minimal AI assistance"""
        scorer = Scorer()

        vibe_score = VibeScore(
            overall_score=25.0,
            confidence=0.6,
            ai_assistance_level=AIAssistanceLevel.MINIMAL,
            contributing_signals=[],
        )

        interpretation = scorer.get_interpretation(vibe_score)

        assert "MINIMAL" in interpretation
        assert "human-authored" in interpretation

    def test_recommendations_substantial_assistance(self):
        """Test recommendations for substantial AI assistance"""
        scorer = Scorer()

        signals = [
            DetectionSignal(
                layer_type=DetectionLayerType.ARTIFACT, score=90.0, confidence=0.9, evidence=[]
            ),
            DetectionSignal(
                layer_type=DetectionLayerType.VELOCITY, score=80.0, confidence=0.8, evidence=[]
            ),
        ]

        vibe_score = VibeScore(
            overall_score=85.0,
            confidence=0.85,
            ai_assistance_level=AIAssistanceLevel.SUBSTANTIAL,
            contributing_signals=signals,
        )

        recommendations = scorer.get_recommendations(vibe_score)

        assert len(recommendations) > 0
        assert any("review" in r.lower() for r in recommendations)

    def test_recommendations_minimal_assistance(self):
        """Test recommendations for minimal AI assistance"""
        scorer = Scorer()

        vibe_score = VibeScore(
            overall_score=20.0,
            confidence=0.6,
            ai_assistance_level=AIAssistanceLevel.MINIMAL,
            contributing_signals=[],
        )

        recommendations = scorer.get_recommendations(vibe_score)

        assert len(recommendations) > 0
        assert any("no immediate action" in r.lower() for r in recommendations)
