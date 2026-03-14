"""
Style analysis for AI-generated code detection.

This module implements style analysis including:
- Style feature extraction (indentation, naming, line length)
- Developer baseline building from git history
- Style deviation detection
- Style consistency scoring
"""

import re
from typing import List, Dict, Any, Optional
from collections import Counter

from ..models import DetectionSignal, SignalType, Evidence


class StyleAnalyzer:
    """
    Analyzes coding style consistency and linguistic fingerprinting.
    
    Detects AI-generated code by analyzing style features and comparing
    against developer baselines.
    """
    
    def __init__(self):
        """Initialize the style analyzer."""
        self.weight = 0.20
    
    def analyze(self, code: str, language: str, context: Optional[Dict[str, Any]] = None) -> DetectionSignal:
        """
        Perform style analysis on code.
        
        Args:
            code: Source code to analyze
            language: Programming language
            context: Optional context with baseline style information
            
        Returns:
            DetectionSignal with style analysis results
        """
        if not code or not code.strip():
            return self._create_null_signal()
        
        # Step 1: Extract style features
        features = self._extract_style_features(code, language)
        
        # Step 2: Build or use baseline
        baseline = context.get("baseline") if context else None
        if baseline is None:
            baseline = self._build_default_baseline(language)
        
        # Step 3: Detect style deviations
        deviation_score = self._compare_with_baseline(features, baseline)
        
        # Step 4: Calculate style consistency
        consistency_score = self._calculate_consistency(features)
        
        # Step 5: Combine style metrics
        overall_score = (deviation_score * 0.6 + consistency_score * 0.4)
        confidence = self._calculate_confidence(features, baseline)
        
        evidence = [
            Evidence("STYLE_DEVIATION", deviation_score, {
                "indentation": features.get("indentation_style"),
                "naming": features.get("naming_style")
            }),
            Evidence("STYLE_CONSISTENCY", consistency_score, {
                "line_length_variance": features.get("line_length_variance", 0)
            })
        ]
        
        return DetectionSignal(
            signal_type=SignalType.STYLE,
            signal_name="style_analysis",
            score=overall_score,
            confidence=confidence,
            weight=self.weight,
            evidence=evidence,
            metadata={
                "features": features,
                "language": language
            }
        )
    
    def _extract_style_features(self, code: str, language: str) -> Dict[str, Any]:
        """
        Extract style features from code.
        
        Features include:
        - Indentation style (spaces vs tabs, indent size)
        - Naming conventions (camelCase, snake_case, etc.)
        - Line length patterns
        - Comment density
        - Whitespace usage
        """
        lines = code.split('\n')
        
        # Indentation analysis
        indents = []
        for line in lines:
            if line.strip():
                leading_spaces = len(line) - len(line.lstrip(' '))
                leading_tabs = len(line) - len(line.lstrip('\t'))
                if leading_spaces > 0:
                    indents.append(('spaces', leading_spaces))
                elif leading_tabs > 0:
                    indents.append(('tabs', leading_tabs))
        
        indent_style = self._determine_indent_style(indents)
        
        # Naming convention analysis
        identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)
        naming_style = self._determine_naming_style(identifiers)
        
        # Line length analysis
        line_lengths = [len(line) for line in lines if line.strip()]
        avg_line_length = sum(line_lengths) / len(line_lengths) if line_lengths else 0
        line_length_variance = self._calculate_variance(line_lengths)
        
        # Comment density
        comment_lines = sum(1 for line in lines if line.strip().startswith('#') or line.strip().startswith('//'))
        comment_density = comment_lines / len(lines) if lines else 0
        
        return {
            "indentation_style": indent_style,
            "naming_style": naming_style,
            "avg_line_length": avg_line_length,
            "line_length_variance": line_length_variance,
            "comment_density": comment_density
        }
    
    def _determine_indent_style(self, indents: List[tuple]) -> str:
        """Determine predominant indentation style."""
        if not indents:
            return "unknown"
        
        space_count = sum(1 for style, _ in indents if style == 'spaces')
        tab_count = sum(1 for style, _ in indents if style == 'tabs')
        
        if space_count > tab_count:
            # Determine indent size
            space_sizes = [size for style, size in indents if style == 'spaces' and size > 0]
            if space_sizes:
                common_size = Counter(space_sizes).most_common(1)[0][0]
                return f"spaces_{common_size}"
        elif tab_count > 0:
            return "tabs"
        
        return "mixed"
    
    def _determine_naming_style(self, identifiers: List[str]) -> str:
        """Determine predominant naming convention."""
        if not identifiers:
            return "unknown"
        
        snake_case = sum(1 for id in identifiers if '_' in id and id.islower())
        camel_case = sum(1 for id in identifiers if id[0].islower() and any(c.isupper() for c in id))
        pascal_case = sum(1 for id in identifiers if id[0].isupper() and any(c.isupper() for c in id[1:]))
        
        styles = {"snake_case": snake_case, "camelCase": camel_case, "PascalCase": pascal_case}
        return max(styles, key=styles.get) if max(styles.values()) > 0 else "unknown"
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return variance
    
    def _build_default_baseline(self, language: str) -> Dict[str, Any]:
        """Build a default baseline for the language."""
        # Language-specific defaults
        defaults = {
            "python": {"indentation": "spaces_4", "naming": "snake_case", "avg_line_length": 60},
            "javascript": {"indentation": "spaces_2", "naming": "camelCase", "avg_line_length": 70},
            "java": {"indentation": "spaces_4", "naming": "camelCase", "avg_line_length": 80},
            "go": {"indentation": "tabs", "naming": "camelCase", "avg_line_length": 80},
        }
        
        return defaults.get(language.lower(), {"indentation": "spaces_4", "naming": "mixed", "avg_line_length": 70})
    
    def _compare_with_baseline(self, features: Dict[str, Any], baseline: Dict[str, Any]) -> float:
        """Compare features with baseline to detect deviations."""
        deviation_score = 0.0
        
        # Check indentation deviation
        if features["indentation_style"] != baseline.get("indentation", "unknown"):
            deviation_score += 30.0
        
        # Check naming deviation
        if features["naming_style"] != baseline.get("naming", "unknown"):
            deviation_score += 25.0
        
        # Check line length deviation
        baseline_line_length = baseline.get("avg_line_length", 70)
        line_length_diff = abs(features["avg_line_length"] - baseline_line_length)
        deviation_score += min(line_length_diff / 2, 25.0)
        
        # AI code tends to be more uniform
        if features["line_length_variance"] < 100:
            deviation_score += 20.0
        
        return min(deviation_score, 100.0)
    
    def _calculate_consistency(self, features: Dict[str, Any]) -> float:
        """Calculate style consistency score."""
        consistency_score = 0.0
        
        # Low variance in line length = high consistency = more AI-like
        if features["line_length_variance"] < 200:
            consistency_score += 50.0
        
        # Consistent indentation
        if "mixed" not in features["indentation_style"]:
            consistency_score += 30.0
        
        # Consistent naming
        if features["naming_style"] != "unknown":
            consistency_score += 20.0
        
        return min(consistency_score, 100.0)
    
    def _calculate_confidence(self, features: Dict[str, Any], baseline: Dict[str, Any]) -> float:
        """Calculate confidence in style analysis."""
        # More features analyzed = higher confidence
        feature_count = sum(1 for v in features.values() if v not in [None, "unknown", 0])
        confidence = min(feature_count / 5.0, 0.8)
        
        return confidence
    
    def _create_null_signal(self) -> DetectionSignal:
        """Create a null signal for empty or invalid input."""
        return DetectionSignal(
            signal_type=SignalType.STYLE,
            signal_name="style_analysis",
            score=0.0,
            confidence=0.0,
            weight=self.weight,
            evidence=[Evidence("NO_STYLE_DATA", 0.0, {})],
            metadata={}
        )
