"""
Feature extraction for ML-based AI code detection.

Extracts numerical features from code that ML models can use for classification.
Based on research showing whitespace variance, token entropy, and style metrics
are most discriminative for AI detection.
"""

import re
import math
from typing import Dict, List
from collections import Counter


class FeatureExtractor:
    """
    Extracts features from code for ML classification.

    Features are based on research papers achieving 95%+ accuracy:
    - Whitespace patterns (most discriminative)
    - Token-level statistics
    - Style consistency metrics
    - Linguistic patterns
    """

    def extract_features(self, code: str, language: str = "python") -> Dict[str, float]:
        """
        Extract all features from code.

        Args:
            code: Source code string
            language: Programming language

        Returns:
            Dictionary of feature_name → value
        """
        if not code or not code.strip():
            return self._empty_features()

        lines = code.split("\n")

        # Extract feature groups
        whitespace_features = self._extract_whitespace_features(lines)
        token_features = self._extract_token_features(code)
        style_features = self._extract_style_features(code, lines, language)
        linguistic_features = self._extract_linguistic_features(code, lines)

        # Combine all features
        features = {}
        features.update(whitespace_features)
        features.update(token_features)
        features.update(style_features)
        features.update(linguistic_features)

        return features

    def _extract_whitespace_features(self, lines: List[str]) -> Dict[str, float]:
        """Extract whitespace-based features (most discriminative)."""
        leading_spaces = []
        trailing_spaces = []
        blank_lines = 0

        for line in lines:
            if not line.strip():
                blank_lines += 1
                continue

            # Leading whitespace
            spaces = len(line) - len(line.lstrip(" "))
            if spaces > 0:
                leading_spaces.append(spaces)

            # Trailing whitespace
            trailing = len(line) - len(line.rstrip())
            if trailing > 0:
                trailing_spaces.append(trailing)

        # Calculate statistics
        spaces_mean = sum(leading_spaces) / len(leading_spaces) if leading_spaces else 0
        spaces_variance = self._variance(leading_spaces) if len(leading_spaces) > 1 else 0
        blank_ratio = blank_lines / len(lines) if lines else 0
        trailing_count = len(trailing_spaces)

        return {
            "spaces_mean": spaces_mean,
            "spaces_variance": spaces_variance,
            "blank_line_ratio": blank_ratio,
            "trailing_whitespace_count": trailing_count,
        }

    def _extract_token_features(self, code: str) -> Dict[str, float]:
        """Extract token-level features."""
        # Tokenize (simple word-based)
        tokens = re.findall(r"\b\w+\b", code)

        if not tokens:
            return {
                "token_count": 0,
                "token_entropy": 0,
                "unique_token_ratio": 0,
                "avg_token_length": 0,
            }

        # Token statistics
        token_count = len(tokens)
        unique_tokens = len(set(tokens))
        unique_ratio = unique_tokens / token_count if token_count > 0 else 0
        avg_length = sum(len(t) for t in tokens) / token_count if token_count > 0 else 0

        # Token entropy (Shannon entropy)
        entropy = self._calculate_entropy(tokens)

        return {
            "token_count": token_count,
            "token_entropy": entropy,
            "unique_token_ratio": unique_ratio,
            "avg_token_length": avg_length,
        }

    def _extract_style_features(
        self, code: str, lines: List[str], language: str
    ) -> Dict[str, float]:
        """Extract style consistency features."""
        # Line lengths
        line_lengths = [len(line) for line in lines if line.strip()]
        avg_line_length = sum(line_lengths) / len(line_lengths) if line_lengths else 0
        line_length_variance = self._variance(line_lengths) if len(line_lengths) > 1 else 0

        # Comments
        comment_lines = self._count_comments(lines, language)
        comment_density = comment_lines / len(lines) if lines else 0

        # Docstrings (Python-specific)
        docstring_count = code.count('"""') + code.count("'''")
        docstring_ratio = docstring_count / len(lines) if lines else 0

        # Identifiers
        identifiers = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", code)
        identifier_entropy = self._calculate_entropy(identifiers) if identifiers else 0

        return {
            "avg_line_length": avg_line_length,
            "line_length_variance": line_length_variance,
            "comment_density": comment_density,
            "docstring_ratio": docstring_ratio,
            "identifier_entropy": identifier_entropy,
        }

    def _extract_linguistic_features(self, code: str, lines: List[str]) -> Dict[str, float]:
        """Extract linguistic patterns."""
        # Type hints (Python/TypeScript)
        type_hint_count = code.count("->") + code.count(": int") + code.count(": str")
        type_hint_ratio = type_hint_count / len(lines) if lines else 0

        # Formal words in comments
        formal_words = ["implement", "functionality", "comprehensive", "optimization"]
        formal_count = sum(code.lower().count(word) for word in formal_words)

        # Code-to-comment ratio
        code_lines = sum(1 for line in lines if line.strip() and not self._is_comment(line.strip()))
        comment_lines = len(lines) - code_lines
        code_comment_ratio = code_lines / comment_lines if comment_lines > 0 else 999

        return {
            "type_hint_ratio": type_hint_ratio,
            "formal_word_count": formal_count,
            "code_comment_ratio": min(code_comment_ratio, 100),  # Cap at 100
        }

    def _count_comments(self, lines: List[str], language: str) -> int:
        """Count comment lines."""
        comment_markers = {
            "python": ["#"],
            "javascript": ["//", "/*"],
            "java": ["//", "/*"],
            "cpp": ["//", "/*"],
            "c": ["//", "/*"],
            "go": ["//", "/*"],
            "rust": ["//", "/*"],
        }

        markers = comment_markers.get(language.lower(), ["#", "//"])
        count = 0

        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(m) for m in markers):
                count += 1

        return count

    def _is_comment(self, line: str) -> bool:
        """Check if line is a comment."""
        return line.startswith("#") or line.startswith("//") or line.startswith("/*")

    def _variance(self, values: List[float]) -> float:
        """Calculate variance."""
        if not values or len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)

    def _calculate_entropy(self, items: List[str]) -> float:
        """Calculate Shannon entropy."""
        if not items:
            return 0.0

        counts = Counter(items)
        total = len(items)

        entropy = 0.0
        for count in counts.values():
            prob = count / total
            if prob > 0:
                entropy -= prob * math.log2(prob)

        return entropy

    def _empty_features(self) -> Dict[str, float]:
        """Return empty feature dict."""
        return {
            "spaces_mean": 0,
            "spaces_variance": 0,
            "blank_line_ratio": 0,
            "trailing_whitespace_count": 0,
            "token_count": 0,
            "token_entropy": 0,
            "unique_token_ratio": 0,
            "avg_token_length": 0,
            "avg_line_length": 0,
            "line_length_variance": 0,
            "comment_density": 0,
            "docstring_ratio": 0,
            "identifier_entropy": 0,
            "type_hint_ratio": 0,
            "formal_word_count": 0,
            "code_comment_ratio": 0,
        }


"""
Feature extraction for ML-based AI code detection.

Extracts numerical features from code that ML models can use for classification.
Based on research showing whitespace variance, token entropy, and style metrics
are most discriminative for AI detection.
"""

import re
import math
from typing import Dict, List
from collections import Counter


class FeatureExtractor:
    """
    Extracts features from code for ML classification.

    Features are based on research papers achieving 95%+ accuracy:
    - Whitespace patterns (most discriminative)
    - Token-level statistics
    - Style consistency metrics
    - Linguistic patterns
    """

    def extract_features(self, code: str, language: str = "python") -> Dict[str, float]:
        """
        Extract all features from code.

        Args:
            code: Source code string
            language: Programming language

        Returns:
            Dictionary of feature_name → value
        """
        if not code or not code.strip():
            return self._empty_features()

        lines = code.split("\n")

        # Extract feature groups
        whitespace_features = self._extract_whitespace_features(lines)
        token_features = self._extract_token_features(code)
        style_features = self._extract_style_features(code, lines, language)
        linguistic_features = self._extract_linguistic_features(code, lines)

        # Combine all features
        features = {}
        features.update(whitespace_features)
        features.update(token_features)
        features.update(style_features)
        features.update(linguistic_features)

        return features

    def _extract_whitespace_features(self, lines: List[str]) -> Dict[str, float]:
        """Extract whitespace-based features (most discriminative)."""
        leading_spaces = []
        trailing_spaces = []
        blank_lines = 0

        for line in lines:
            if not line.strip():
                blank_lines += 1
                continue

            # Leading whitespace
            spaces = len(line) - len(line.lstrip(" "))
            if spaces > 0:
                leading_spaces.append(spaces)

            # Trailing whitespace
            trailing = len(line) - len(line.rstrip())
            if trailing > 0:
                trailing_spaces.append(trailing)

        # Calculate statistics
        spaces_mean = sum(leading_spaces) / len(leading_spaces) if leading_spaces else 0
        spaces_variance = self._variance(leading_spaces) if len(leading_spaces) > 1 else 0
        blank_ratio = blank_lines / len(lines) if lines else 0
        trailing_count = len(trailing_spaces)

        return {
            "spaces_mean": spaces_mean,
            "spaces_variance": spaces_variance,
            "blank_line_ratio": blank_ratio,
            "trailing_whitespace_count": trailing_count,
        }

    def _extract_token_features(self, code: str) -> Dict[str, float]:
        """Extract token-level features."""
        # Tokenize (simple word-based)
        tokens = re.findall(r"\b\w+\b", code)

        if not tokens:
            return {
                "token_count": 0,
                "token_entropy": 0,
                "unique_token_ratio": 0,
                "avg_token_length": 0,
            }

        # Token statistics
        token_count = len(tokens)
        unique_tokens = len(set(tokens))
        unique_ratio = unique_tokens / token_count if token_count > 0 else 0
        avg_length = sum(len(t) for t in tokens) / token_count if token_count > 0 else 0

        # Token entropy (Shannon entropy)
        entropy = self._calculate_entropy(tokens)

        return {
            "token_count": token_count,
            "token_entropy": entropy,
            "unique_token_ratio": unique_ratio,
            "avg_token_length": avg_length,
        }

    def _extract_style_features(
        self, code: str, lines: List[str], language: str
    ) -> Dict[str, float]:
        """Extract style consistency features."""
        # Line lengths
        line_lengths = [len(line) for line in lines if line.strip()]
        avg_line_length = sum(line_lengths) / len(line_lengths) if line_lengths else 0
        line_length_variance = self._variance(line_lengths) if len(line_lengths) > 1 else 0

        # Comments
        comment_lines = self._count_comments(lines, language)
        comment_density = comment_lines / len(lines) if lines else 0

        # Docstrings (Python-specific)
        docstring_count = code.count('"""') + code.count("'''")
        docstring_ratio = docstring_count / len(lines) if lines else 0

        # Identifiers
        identifiers = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", code)
        identifier_entropy = self._calculate_entropy(identifiers) if identifiers else 0

        return {
            "avg_line_length": avg_line_length,
            "line_length_variance": line_length_variance,
            "comment_density": comment_density,
            "docstring_ratio": docstring_ratio,
            "identifier_entropy": identifier_entropy,
        }

    def _extract_linguistic_features(self, code: str, lines: List[str]) -> Dict[str, float]:
        """Extract linguistic patterns."""
        # Type hints (Python/TypeScript)
        type_hint_count = code.count("->") + code.count(": int") + code.count(": str")
        type_hint_ratio = type_hint_count / len(lines) if lines else 0

        # Formal words in comments
        formal_words = ["implement", "functionality", "comprehensive", "optimization"]
        formal_count = sum(code.lower().count(word) for word in formal_words)

        # Code-to-comment ratio
        code_lines = sum(1 for line in lines if line.strip() and not self._is_comment(line.strip()))
        comment_lines = len(lines) - code_lines
        code_comment_ratio = code_lines / comment_lines if comment_lines > 0 else 999

        return {
            "type_hint_ratio": type_hint_ratio,
            "formal_word_count": formal_count,
            "code_comment_ratio": min(code_comment_ratio, 100),  # Cap at 100
        }

    def _count_comments(self, lines: List[str], language: str) -> int:
        """Count comment lines."""
        comment_markers = {
            "python": ["#"],
            "javascript": ["//", "/*"],
            "java": ["//", "/*"],
            "cpp": ["//", "/*"],
            "c": ["//", "/*"],
            "go": ["//", "/*"],
            "rust": ["//", "/*"],
        }

        markers = comment_markers.get(language.lower(), ["#", "//"])
        count = 0

        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(m) for m in markers):
                count += 1

        return count

    def _is_comment(self, line: str) -> bool:
        """Check if line is a comment."""
        return line.startswith("#") or line.startswith("//") or line.startswith("/*")

    def _variance(self, values: List[float]) -> float:
        """Calculate variance."""
        if not values or len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)

    def _calculate_entropy(self, items: List[str]) -> float:
        """Calculate Shannon entropy."""
        if not items:
            return 0.0

        counts = Counter(items)
        total = len(items)

        entropy = 0.0
        for count in counts.values():
            prob = count / total
            if prob > 0:
                entropy -= prob * math.log2(prob)

        return entropy

    def _empty_features(self) -> Dict[str, float]:
        """Return empty feature dict."""
        return {
            "spaces_mean": 0,
            "spaces_variance": 0,
            "blank_line_ratio": 0,
            "trailing_whitespace_count": 0,
            "token_count": 0,
            "token_entropy": 0,
            "unique_token_ratio": 0,
            "avg_token_length": 0,
            "avg_line_length": 0,
            "line_length_variance": 0,
            "comment_density": 0,
            "docstring_ratio": 0,
            "identifier_entropy": 0,
            "type_hint_ratio": 0,
            "formal_word_count": 0,
            "code_comment_ratio": 0,
        }
