"""
Pattern detection for AI-generated code.

This module implements pattern-based detection of AI-generated code by identifying
common signatures such as:
- AI-style comments (overly verbose, generic)
- Uniform complexity across functions
- Hallucination patterns (non-existent APIs)
- AI-specific code patterns (boilerplate, repetitive structures)
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..models import DetectionSignal, SignalType, Evidence


@dataclass
class PatternMatch:
    """Represents a pattern match found in code."""
    pattern_type: str
    line_number: int
    matched_text: str
    confidence: float


class PatternDetector:
    """
    Detects AI-generated code patterns and signatures.
    
    This detector analyzes code for common patterns that indicate AI generation,
    including comment styles, complexity uniformity, and hallucination patterns.
    """
    
    # AI comment patterns (overly verbose, generic)
    AI_COMMENT_PATTERNS = [
        r"#\s*This (function|method|class) (is used to|will|does)",
        r"#\s*Initialize the",
        r"#\s*Create (a|an) (new )?instance",
        r"#\s*Return the (result|value|output)",
        r"#\s*Args:",
        r"#\s*Returns:",
        r"#\s*Raises:",
        r"//\s*This (function|method|class) (is used to|will|does)",
        r"//\s*Initialize the",
        r"//\s*Create (a|an) (new )?instance",
        r"//\s*Return the (result|value|output)",
        r"/\*\*\s*\n\s*\*\s*This (function|method|class)",
        r'"""[\s\S]*?Args:[\s\S]*?"""',  # Docstrings with Args
        r'"""[\s\S]*?Returns:[\s\S]*?"""',  # Docstrings with Returns
    ]
    
    # Hallucination patterns (non-existent or unusual API calls)
    HALLUCINATION_PATTERNS = [
        r"\.get_all_data\(\)",
        r"\.fetch_everything\(\)",
        r"\.do_magic\(\)",
        r"\.auto_fix\(\)",
        r"\.smart_process\(\)",
    ]
    
    # AI-specific code patterns
    AI_CODE_PATTERNS = [
        r"if\s+\w+\s+is\s+not\s+None:\s*\n\s+return\s+\w+\s*\n\s*return\s+None",
        r"try:\s*\n\s+.*\s*\n\s*except\s+Exception\s+as\s+e:\s*\n\s+pass",
    ]
    
    def __init__(self):
        """Initialize the pattern detector."""
        self.pattern_threshold = 0.3
        self.weight = 0.25
    
    def detect(self, code: str, language: str, ast: Optional[Any] = None) -> DetectionSignal:
        """
        Detect AI-generated code patterns.
        
        Args:
            code: Source code to analyze
            language: Programming language
            ast: Optional AST for the code
            
        Returns:
            DetectionSignal with pattern detection results
            
        Preconditions:
            - code is non-empty string
            - language is supported language identifier
            
        Postconditions:
            - signal.score is between 0 and 100
            - signal.confidence is between 0 and 1
            - signal.evidence contains all detected patterns
        """
        if not code or not code.strip():
            return self._create_null_signal()
        
        pattern_scores = []
        evidence = []
        
        # Check 1: Comment pattern analysis
        comment_score, comment_matches = self._analyze_comment_patterns(code)
        if comment_score > self.pattern_threshold:
            pattern_scores.append(comment_score)
            evidence.append(Evidence(
                "AI_COMMENT_STYLE",
                comment_score,
                {"matches": len(comment_matches), "examples": comment_matches[:3]}
            ))
        
        # Check 2: Complexity uniformity (if AST available)
        if ast is not None:
            complexity_score = self._analyze_complexity_uniformity(ast)
            if complexity_score > self.pattern_threshold:
                pattern_scores.append(complexity_score)
                evidence.append(Evidence(
                    "UNIFORM_COMPLEXITY",
                    complexity_score,
                    {"description": "Functions have suspiciously uniform complexity"}
                ))
        
        # Check 3: Hallucination patterns
        hallucinations = self._detect_hallucinations(code, language)
        if hallucinations:
            hallucination_score = min(len(hallucinations) * 20.0, 100.0)
            pattern_scores.append(hallucination_score)
            evidence.append(Evidence(
                "HALLUCINATIONS",
                hallucination_score,
                {"count": len(hallucinations), "examples": hallucinations[:3]}
            ))
        
        # Check 4: AI-specific code patterns
        ai_patterns = self._detect_ai_code_patterns(code, language)
        if ai_patterns:
            ai_pattern_score = min(len(ai_patterns) * 15.0, 100.0)
            pattern_scores.append(ai_pattern_score)
            evidence.append(Evidence(
                "AI_CODE_PATTERNS",
                ai_pattern_score,
                {"count": len(ai_patterns), "examples": ai_patterns[:3]}
            ))
        
        # Calculate overall pattern score
        if pattern_scores:
            overall_score = sum(pattern_scores) / len(pattern_scores)
            confidence = self._calculate_confidence(pattern_scores)
        else:
            overall_score = 0.0
            confidence = 0.0
        
        return DetectionSignal(
            signal_type=SignalType.PATTERN,
            signal_name="pattern_detection",
            score=overall_score,
            confidence=confidence,
            weight=self.weight,
            evidence=evidence,
            metadata={
                "pattern_count": len(pattern_scores),
                "language": language
            }
        )
    
    def _analyze_comment_patterns(self, code: str) -> tuple[float, List[str]]:
        """
        Analyze code for AI-style comment patterns.
        
        Returns:
            Tuple of (score, list of matched comments)
        """
        matches = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.AI_COMMENT_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append(f"Line {line_num}: {line.strip()}")
        
        # Calculate score based on match density
        if not lines:
            return 0.0, []
        
        match_density = len(matches) / len(lines)
        score = min(match_density * 500, 100.0)  # Scale up density
        
        return score, matches
    
    def _analyze_complexity_uniformity(self, ast: Any) -> float:
        """
        Analyze AST for uniform complexity across functions.
        
        AI-generated code often has suspiciously uniform complexity.
        
        Returns:
            Score indicating uniformity (higher = more uniform = more AI-like)
        """
        # Placeholder implementation - would need actual AST analysis
        # For now, return a moderate score
        return 50.0
    
    def _detect_hallucinations(self, code: str, language: str) -> List[str]:
        """
        Detect hallucination patterns (non-existent APIs, unusual patterns).
        
        Returns:
            List of detected hallucinations
        """
        hallucinations = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.HALLUCINATION_PATTERNS:
                if re.search(pattern, line):
                    hallucinations.append(f"Line {line_num}: {line.strip()}")
        
        return hallucinations
    
    def _detect_ai_code_patterns(self, code: str, language: str) -> List[str]:
        """
        Detect AI-specific code patterns.
        
        Returns:
            List of detected AI code patterns
        """
        ai_patterns = []
        
        for pattern in self.AI_CODE_PATTERNS:
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                ai_patterns.append(match.group(0)[:100])  # First 100 chars
        
        return ai_patterns
    
    def _calculate_confidence(self, scores: List[float]) -> float:
        """
        Calculate confidence based on number and agreement of signals.
        
        More signals with similar scores = higher confidence.
        """
        if not scores:
            return 0.0
        
        # Base confidence on number of signals
        base_confidence = min(len(scores) / 4.0, 0.8)
        
        # Adjust for score variance (lower variance = higher confidence)
        if len(scores) > 1:
            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            variance_penalty = min(variance / 1000.0, 0.2)
            confidence = base_confidence - variance_penalty
        else:
            confidence = base_confidence * 0.7  # Lower confidence with single signal
        
        return max(0.0, min(1.0, confidence))
    
    def _create_null_signal(self) -> DetectionSignal:
        """Create a null signal for empty or invalid input."""
        return DetectionSignal(
            signal_type=SignalType.PATTERN,
            signal_name="pattern_detection",
            score=0.0,
            confidence=0.0,
            weight=self.weight,
            evidence=[Evidence("NO_PATTERNS", 0.0, {})],
            metadata={}
        )
