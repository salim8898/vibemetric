"""
Statistical analysis for AI-generated code detection.

This module implements statistical analysis including:
- Code tokenization
- Perplexity calculation
- Predictability scoring
- Token distribution analysis
- Statistical anomaly detection
"""

import re
import math
from typing import List, Dict, Any, Optional
from collections import Counter

from ..models import DetectionSignal, SignalType, Evidence


class StatisticalAnalyzer:
    """
    Performs statistical analysis on code characteristics.
    
    Analyzes code using statistical methods to detect AI-generated patterns
    including perplexity, predictability, and token distribution.
    """
    
    def __init__(self):
        """Initialize the statistical analyzer."""
        self.weight = 0.25
    
    def analyze(self, code: str, language: str) -> DetectionSignal:
        """
        Perform statistical analysis on code.
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            DetectionSignal with statistical analysis results
        """
        if not code or not code.strip():
            return self._create_null_signal()
        
        # Step 1: Tokenize code
        tokens = self._tokenize(code, language)
        
        if not tokens:
            return self._create_null_signal()
        
        # Step 2: Calculate perplexity score
        perplexity = self._calculate_perplexity(tokens)
        perplexity_score = self._normalize_perplexity(perplexity)
        
        # Step 3: Calculate predictability
        predictability = self._calculate_predictability(tokens)
        predictability_score = self._normalize_predictability(predictability)
        
        # Step 4: Analyze token distribution
        distribution = self._analyze_token_distribution(tokens)
        distribution_score = self._score_distribution(distribution)
        
        # Step 5: Detect statistical anomalies
        anomalies = self._detect_anomalies(tokens, distribution)
        anomaly_score = self._score_anomalies(anomalies)
        
        # Step 6: Combine statistical metrics
        statistical_scores = [
            perplexity_score,
            predictability_score,
            distribution_score,
            anomaly_score
        ]
        weights = [0.3, 0.3, 0.2, 0.2]
        
        overall_score = sum(s * w for s, w in zip(statistical_scores, weights))
        confidence = self._calculate_statistical_confidence(statistical_scores)
        
        evidence = [
            Evidence("PERPLEXITY", perplexity_score, {"value": perplexity}),
            Evidence("PREDICTABILITY", predictability_score, {"value": predictability}),
            Evidence("DISTRIBUTION", distribution_score, {"entropy": distribution.get("entropy", 0)}),
            Evidence("ANOMALIES", anomaly_score, {"count": len(anomalies)})
        ]
        
        return DetectionSignal(
            signal_type=SignalType.STATISTICAL,
            signal_name="statistical_analysis",
            score=overall_score,
            confidence=confidence,
            weight=self.weight,
            evidence=evidence,
            metadata={
                "token_count": len(tokens),
                "unique_tokens": len(set(tokens)),
                "language": language
            }
        )
    
    def _tokenize(self, code: str, language: str) -> List[str]:
        """
        Tokenize code into tokens.
        
        Simple tokenization based on whitespace and common delimiters.
        """
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Split on whitespace and common delimiters
        tokens = re.findall(r'\w+|[^\w\s]', code)
        
        # Filter out empty tokens
        tokens = [t for t in tokens if t.strip()]
        
        return tokens
    
    def _calculate_perplexity(self, tokens: List[str]) -> float:
        """
        Calculate perplexity score.
        
        Lower perplexity indicates more predictable (AI-like) code.
        """
        if len(tokens) < 2:
            return 0.0
        
        # Calculate token frequencies
        token_counts = Counter(tokens)
        total_tokens = len(tokens)
        
        # Calculate entropy
        entropy = 0.0
        for count in token_counts.values():
            prob = count / total_tokens
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        # Perplexity is 2^entropy
        perplexity = 2 ** entropy
        
        return perplexity
    
    def _normalize_perplexity(self, perplexity: float) -> float:
        """Normalize perplexity to 0-100 range."""
        # Lower perplexity = higher AI likelihood
        # Typical perplexity ranges from 1 to 1000+
        # Invert and normalize
        if perplexity <= 1:
            return 100.0
        
        # Use logarithmic scale
        normalized = 100.0 - (math.log10(perplexity) * 33.3)
        return max(0.0, min(100.0, normalized))
    
    def _calculate_predictability(self, tokens: List[str]) -> float:
        """
        Calculate code predictability.
        
        Higher predictability indicates more AI-like code.
        """
        if len(tokens) < 3:
            return 0.0
        
        # Calculate bigram predictability
        bigrams = [(tokens[i], tokens[i+1]) for i in range(len(tokens)-1)]
        bigram_counts = Counter(bigrams)
        
        # Calculate average predictability
        total_predictability = 0.0
        for bigram, count in bigram_counts.items():
            first_token_count = tokens.count(bigram[0])
            predictability = count / first_token_count if first_token_count > 0 else 0
            total_predictability += predictability
        
        avg_predictability = total_predictability / len(bigram_counts) if bigram_counts else 0.0
        
        return avg_predictability
    
    def _normalize_predictability(self, predictability: float) -> float:
        """Normalize predictability to 0-100 range."""
        # Higher predictability = higher AI likelihood
        return min(predictability * 100.0, 100.0)
    
    def _analyze_token_distribution(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Analyze token distribution patterns.
        
        Returns distribution metrics including entropy and uniformity.
        """
        token_counts = Counter(tokens)
        total_tokens = len(tokens)
        
        # Calculate entropy
        entropy = 0.0
        for count in token_counts.values():
            prob = count / total_tokens
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        # Calculate uniformity (coefficient of variation)
        counts = list(token_counts.values())
        mean_count = sum(counts) / len(counts) if counts else 0
        variance = sum((c - mean_count) ** 2 for c in counts) / len(counts) if counts else 0
        std_dev = math.sqrt(variance)
        cv = std_dev / mean_count if mean_count > 0 else 0
        
        return {
            "entropy": entropy,
            "uniformity": 1.0 / (1.0 + cv) if cv > 0 else 1.0,
            "unique_ratio": len(token_counts) / total_tokens if total_tokens > 0 else 0
        }
    
    def _score_distribution(self, distribution: Dict[str, Any]) -> float:
        """Score the token distribution."""
        # Lower entropy and higher uniformity = more AI-like
        entropy_score = max(0, 100 - distribution["entropy"] * 10)
        uniformity_score = distribution["uniformity"] * 100
        
        return (entropy_score + uniformity_score) / 2
    
    def _detect_anomalies(self, tokens: List[str], distribution: Dict[str, Any]) -> List[str]:
        """Detect statistical anomalies in token patterns."""
        anomalies = []
        
        # Check for repeated token sequences
        for i in range(len(tokens) - 3):
            sequence = tuple(tokens[i:i+3])
            count = sum(1 for j in range(len(tokens)-2) if tuple(tokens[j:j+3]) == sequence)
            if count > 3:
                anomalies.append(f"Repeated sequence: {' '.join(sequence)}")
        
        return list(set(anomalies))[:10]  # Limit to 10 unique anomalies
    
    def _score_anomalies(self, anomalies: List[str]) -> float:
        """Score detected anomalies."""
        return min(len(anomalies) * 10.0, 100.0)
    
    def _calculate_statistical_confidence(self, scores: List[float]) -> float:
        """Calculate confidence based on score agreement."""
        if not scores:
            return 0.0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        # Lower variance = higher confidence
        confidence = 1.0 - min(variance / 1000.0, 0.5)
        
        return max(0.0, min(1.0, confidence))
    
    def _create_null_signal(self) -> DetectionSignal:
        """Create a null signal for empty or invalid input."""
        return DetectionSignal(
            signal_type=SignalType.STATISTICAL,
            signal_name="statistical_analysis",
            score=0.0,
            confidence=0.0,
            weight=self.weight,
            evidence=[Evidence("NO_DATA", 0.0, {})],
            metadata={}
        )
