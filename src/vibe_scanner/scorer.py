"""
Vibe score calculation and aggregation.

This module implements score calculation including:
- Signal weighting and aggregation
- Confidence calculation based on signal agreement
- Risk level determination
- Score explanation generation
"""

from typing import List, Dict, Any
from enum import Enum

from .models import DetectionSignal, VibeScore, RiskLevel, FileAnalysisResult


class VibeScoreCalculator:
    """
    Aggregates detection signals into final Vibe Scores.
    
    Combines multiple detection signals with appropriate weighting to produce
    overall vibe scores with confidence intervals and risk levels.
    """
    
    def __init__(self):
        """Initialize the vibe score calculator."""
        pass
    
    def calculate_file_score(self, signals: List[DetectionSignal]) -> VibeScore:
        """
        Calculate vibe score for a single file.
        
        Args:
            signals: List of detection signals from various analyzers
            
        Returns:
            VibeScore with aggregated results
            
        Preconditions:
            - signals list is not empty
            - All signals have valid score (0-100), confidence (0-1), and weight (0-1)
            
        Postconditions:
            - score.overall_score is between 0 and 100
            - score.confidence is between 0 and 1
            - score.risk_level is correctly assigned based on overall_score
        """
        if not signals:
            return self._create_null_score()
        
        # Filter out signals with zero weight
        active_signals = [s for s in signals if s.weight > 0]
        
        if not active_signals:
            return self._create_null_score()
        
        # Normalize and weight signals
        weighted_scores = {}
        total_weight = 0.0
        
        for signal in active_signals:
            # Apply confidence weighting
            normalized_score = signal.score * signal.confidence
            weighted_score = normalized_score * signal.weight
            weighted_scores[signal.signal_name] = weighted_score
            total_weight += signal.weight
        
        # Calculate overall score
        if total_weight > 0:
            overall_score = sum(weighted_scores.values()) / total_weight
        else:
            overall_score = 0.0
        
        # Ensure score is in valid range
        overall_score = max(0.0, min(100.0, overall_score))
        
        # Calculate confidence based on signal agreement
        confidence = self._calculate_signal_agreement(active_signals)
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        # Generate explanation
        explanation = self._generate_explanation(active_signals, overall_score, risk_level)
        
        return VibeScore(
            overall_score=overall_score,
            confidence=confidence,
            contributing_signals=weighted_scores,
            risk_level=risk_level,
            explanation=explanation,
            line_scores=None
        )
    
    def calculate_repo_score(self, file_results: List[FileAnalysisResult]) -> VibeScore:
        """
        Calculate aggregate vibe score for entire repository.
        
        Args:
            file_results: List of file analysis results
            
        Returns:
            VibeScore for the repository
        """
        if not file_results:
            return self._create_null_score()
        
        # Weight by lines of code
        total_lines = sum(f.code_lines for f in file_results)
        
        if total_lines == 0:
            return self._create_null_score()
        
        # Calculate weighted average score
        weighted_score = sum(
            f.vibe_score.overall_score * f.code_lines 
            for f in file_results
        ) / total_lines
        
        # Calculate average confidence
        avg_confidence = sum(f.vibe_score.confidence for f in file_results) / len(file_results)
        
        # Determine risk level
        risk_level = self._determine_risk_level(weighted_score)
        
        # Aggregate contributing signals
        all_signals = {}
        for f in file_results:
            for signal_name, score in f.vibe_score.contributing_signals.items():
                if signal_name not in all_signals:
                    all_signals[signal_name] = []
                all_signals[signal_name].append(score)
        
        # Average signal scores
        contributing_signals = {
            name: sum(scores) / len(scores)
            for name, scores in all_signals.items()
        }
        
        explanation = f"Repository-wide analysis of {len(file_results)} files"
        
        return VibeScore(
            overall_score=weighted_score,
            confidence=avg_confidence,
            contributing_signals=contributing_signals,
            risk_level=risk_level,
            explanation=explanation,
            line_scores=None
        )
    
    def _calculate_signal_agreement(self, signals: List[DetectionSignal]) -> float:
        """
        Calculate confidence based on signal agreement.
        
        More signals with similar scores = higher confidence.
        """
        if not signals:
            return 0.0
        
        # Base confidence on number of signals
        base_confidence = min(len(signals) / 4.0, 0.7)
        
        # Adjust for score variance (lower variance = higher confidence)
        if len(signals) > 1:
            scores = [s.score for s in signals]
            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            variance_penalty = min(variance / 2000.0, 0.3)
            confidence = base_confidence + (0.3 - variance_penalty)
        else:
            confidence = base_confidence
        
        # Factor in individual signal confidences
        avg_signal_confidence = sum(s.confidence for s in signals) / len(signals)
        final_confidence = (confidence + avg_signal_confidence) / 2
        
        return max(0.0, min(1.0, final_confidence))
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """
        Determine risk level based on score.
        
        LOW: < 30
        MEDIUM: 30-70
        HIGH: > 70
        """
        if score < 30:
            return RiskLevel.LOW
        elif score < 70:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH
    
    def _generate_explanation(self, signals: List[DetectionSignal], score: float, risk_level: RiskLevel) -> str:
        """Generate human-readable explanation of the score."""
        # Find top contributing signals
        top_signals = sorted(signals, key=lambda s: s.score * s.weight, reverse=True)[:3]
        
        signal_names = {
            "pattern_detection": "AI code patterns",
            "statistical_analysis": "statistical anomalies",
            "style_analysis": "style inconsistencies",
            "git_metadata": "rapid authoring speed"
        }
        
        contributors = [signal_names.get(s.signal_name, s.signal_name) for s in top_signals]
        
        if risk_level == RiskLevel.HIGH:
            level_desc = "High AI likelihood"
        elif risk_level == RiskLevel.MEDIUM:
            level_desc = "Moderate AI likelihood"
        else:
            level_desc = "Low AI likelihood"
        
        if contributors:
            return f"{level_desc} due to {', '.join(contributors)}"
        else:
            return level_desc
    
    def _create_null_score(self) -> VibeScore:
        """Create a null score for empty input."""
        return VibeScore(
            overall_score=0.0,
            confidence=0.0,
            contributing_signals={},
            risk_level=RiskLevel.LOW,
            explanation="No analysis data available",
            line_scores=None
        )
