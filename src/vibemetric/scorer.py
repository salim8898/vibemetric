"""
Score Combination Engine

Combines signals from all 4 detection layers into a unified AI likelihood score.

Detection Layers:
1. Artifact Detector (90% accuracy) - Weight: 40%
2. Velocity Analyzer (80% accuracy) - Weight: 25%
3. Pattern Detector (70% accuracy) - Weight: 20%
4. ML Detector (85% accuracy) - Weight: 15%

AI Assistance Levels:
- MINIMAL: 0-40 (primarily human-authored)
- PARTIAL: 40-70 (mixed human-AI collaboration)
- SUBSTANTIAL: 70-100 (significant AI contribution)
"""

from typing import List, Optional
from .models import DetectionSignal, VibeScore, AIAssistanceLevel, DetectionLayerType


class Scorer:
    """
    Combines detection signals into unified AI likelihood score.
    
    Uses weighted averaging based on layer accuracy and reliability.
    """
    
    # Layer weights (sum to 1.0)
    WEIGHTS = {
        DetectionLayerType.ARTIFACT: 0.40,  # Most reliable
        DetectionLayerType.VELOCITY: 0.25,  # Good for adoption detection
        DetectionLayerType.PATTERN: 0.20,   # Catches specific patterns
        DetectionLayerType.ML: 0.15,        # Fallback for subtle patterns
    }
    
    def __init__(self):
        """Initialize scorer."""
        pass
    
    def calculate_vibe_score(
        self,
        signals: List[DetectionSignal],
        require_all_layers: bool = False
    ) -> VibeScore:
        """
        Calculate combined AI likelihood score from detection signals.
        
        Args:
            signals: List of detection signals from various layers
            require_all_layers: If True, requires signals from all 4 layers
            
        Returns:
            Combined VibeScore with overall assessment
        """
        if not signals:
            return self._create_null_score()
        
        # Filter out null signals (score=0, confidence=0)
        active_signals = [
            s for s in signals 
            if s.score > 0 or s.confidence > 0
        ]
        
        if not active_signals:
            return self._create_null_score()
        
        # Calculate weighted score
        total_weight = 0.0
        weighted_sum = 0.0
        confidence_sum = 0.0
        
        for signal in active_signals:
            weight = self.WEIGHTS.get(signal.layer_type, 0.0)
            
            # Weight by both layer importance and signal confidence
            effective_weight = weight * signal.confidence
            
            weighted_sum += signal.score * effective_weight
            total_weight += effective_weight
            confidence_sum += signal.confidence
        
        if total_weight == 0:
            return self._create_null_score()
        
        # Calculate overall score
        overall_score = weighted_sum / total_weight
        
        # Calculate overall confidence (average of active signals)
        overall_confidence = confidence_sum / len(active_signals)
        
        # Boost confidence if multiple layers agree
        if len(active_signals) >= 3:
            overall_confidence = min(overall_confidence * 1.1, 1.0)
        elif len(active_signals) >= 2:
            overall_confidence = min(overall_confidence * 1.05, 1.0)
        
        # Determine AI assistance level
        ai_assistance_level = self._calculate_assistance_level(overall_score)
        
        return VibeScore(
            overall_score=overall_score,
            confidence=overall_confidence,
            ai_assistance_level=ai_assistance_level,
            contributing_signals=signals
        )
    
    def _calculate_assistance_level(self, score: float) -> AIAssistanceLevel:
        """
        Determine AI assistance level from score.
        
        Args:
            score: AI likelihood score (0-100)
            
        Returns:
            AI assistance level classification
        """
        if score >= 70:
            return AIAssistanceLevel.SUBSTANTIAL
        elif score >= 40:
            return AIAssistanceLevel.PARTIAL
        else:
            return AIAssistanceLevel.MINIMAL
    
    def _create_null_score(self) -> VibeScore:
        """Create null score when no signals available."""
        return VibeScore(
            overall_score=0.0,
            confidence=0.0,
            ai_assistance_level=AIAssistanceLevel.MINIMAL,
            contributing_signals=[]
        )
    
    def get_interpretation(self, vibe_score: VibeScore) -> str:
        """
        Get human-readable interpretation of score.
        
        Args:
            vibe_score: Combined vibe score
            
        Returns:
            Interpretation text
        """
        score = vibe_score.overall_score
        level = vibe_score.ai_assistance_level
        
        if level == AIAssistanceLevel.SUBSTANTIAL:
            return (
                f"This code shows SUBSTANTIAL AI assistance ({score:.1f}/100). "
                "Multiple detection layers confirm significant AI tool usage. "
                "Likely generated with tools like GPT-4, Copilot, or Claude."
            )
        elif level == AIAssistanceLevel.PARTIAL:
            return (
                f"This code shows PARTIAL AI assistance ({score:.1f}/100). "
                "Some AI patterns detected, suggesting mixed human-AI collaboration. "
                "May be human-written with AI assistance or selective AI usage."
            )
        else:
            return (
                f"This code shows MINIMAL AI assistance ({score:.1f}/100). "
                "Primarily human-authored with little to no AI tool usage. "
                "Patterns consistent with traditional development practices."
            )
    
    def get_recommendations(self, vibe_score: VibeScore) -> List[str]:
        """
        Get actionable recommendations based on score.
        
        Args:
            vibe_score: Combined vibe score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        level = vibe_score.ai_assistance_level
        
        # Check which layers contributed
        has_artifact = any(
            s.layer_type == DetectionLayerType.ARTIFACT and s.score > 0
            for s in vibe_score.contributing_signals
        )
        has_velocity = any(
            s.layer_type == DetectionLayerType.VELOCITY and s.score > 0
            for s in vibe_score.contributing_signals
        )
        has_pattern = any(
            s.layer_type == DetectionLayerType.PATTERN and s.score > 0
            for s in vibe_score.contributing_signals
        )
        has_ml = any(
            s.layer_type == DetectionLayerType.ML and s.score > 0
            for s in vibe_score.contributing_signals
        )
        
        if level == AIAssistanceLevel.SUBSTANTIAL:
            recommendations.append("Review AI tool usage policies with team")
            recommendations.append("Ensure AI-generated code is properly reviewed")
            recommendations.append("Consider code quality audits for AI-assisted code")
            
            if has_artifact:
                recommendations.append("Document which AI tools are approved for use")
            
            if has_velocity:
                recommendations.append("Monitor velocity changes for quality impact")
        
        elif level == AIAssistanceLevel.PARTIAL:
            recommendations.append("Establish clear AI usage guidelines")
            recommendations.append("Track AI adoption across team members")
            
            if has_pattern:
                recommendations.append("Review code patterns for consistency")
        
        else:  # MINIMAL
            if not has_artifact and not has_velocity:
                recommendations.append("No immediate action needed")
                recommendations.append("Continue monitoring for AI adoption")
        
        return recommendations
