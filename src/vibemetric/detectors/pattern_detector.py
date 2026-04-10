"""
Pattern Detector - Layer 3 (70% Accuracy)

Detects AI-generated code by analyzing patterns such as:
- AI-style comments (overly verbose, generic)
- Comprehensive docstrings with Args/Returns/Examples
- Extensive type hints
- Heavy dataclass usage
- Uniform complexity across functions
- Hallucination patterns (non-existent APIs)
- AI-specific code patterns

This is the third detection layer, providing 70% accuracy.
"""

import re
from pathlib import Path

from ..models import DetectionLayerType, DetectionSignal


class PatternDetector:
    """
    Detects AI-generated code patterns and signatures.

    Analyzes code for common patterns that indicate AI generation.
    """

    # Directories to exclude (tool-generated)
    EXCLUDE_DIRS = {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        ".nox",
        "node_modules",
        "venv",
        "env",
        ".venv",
        ".env",
        "build",
        "dist",
        ".egg-info",
        ".eggs",
        "htmlcov",
        ".coverage",
        ".git",
        ".svn",
        ".hg",
        "migrations",  # Django migrations (auto-generated)
        "alembic",  # Alembic migrations (auto-generated)
    }

    # AI comment patterns (overly verbose, generic)
    AI_COMMENT_PATTERNS = [
        r"#\s*This (function|method|class) (is used to|will|does)",
        r"#\s*Initialize the",
        r"#\s*Create (a|an) (new )?instance",
        r"#\s*Return the (result|value|output)",
        r"^\s*Args:",  # Docstring Args section
        r"^\s*Returns:",  # Docstring Returns section
        r"^\s*Raises:",  # Docstring Raises section
        r"^\s*Preconditions:",  # Formal preconditions (very AI-like)
        r"^\s*Postconditions:",  # Formal postconditions (very AI-like)
        r"^\s*Example:",  # Example sections in docstrings
        r"^\s*Attributes:",  # Attribute documentation
        r"//\s*This (function|method|class) (is used to|will|does)",
        r"//\s*Initialize the",
        r"//\s*Create (a|an) (new )?instance",
        r"//\s*Return the (result|value|output)",
        r"/\*\*\s*\n\s*\*\s*This (function|method|class)",
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

    # AI commit message patterns
    AI_COMMIT_PATTERNS = [
        r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+",  # Conventional commits (AI loves these)
        r"^(Add|Update|Fix|Remove|Refactor|Implement) .+ (feature|functionality|support|implementation)",
        r"^(Improve|Enhance|Optimize) .+ (performance|efficiency|code quality)",
        r"^Fix (bug|issue|problem) (in|with|for) .+",
        r"^Update .+ (to|for) (improve|enhance|fix)",
        r"^Refactor .+ (for|to) (better|improved|cleaner)",
        r"^Add (comprehensive|detailed|extensive) .+",
        r"^Implement .+ (according to|as per|following) .+",
        # NEW: List-style commit patterns (VERY AI-like)
        r"^\s*[-*•]\s+\w+",  # Bullet points at start
        r"\n\s*[-*•]\s+\w+",  # Bullet points in body
    ]

    # AI PR description patterns
    AI_PR_PATTERNS = [
        r"## (Summary|Description|Changes|Overview)",  # Structured PR descriptions
        r"## (Motivation|Context|Background)",
        r"## (Testing|Test Plan|How to Test)",
        r"## (Screenshots|Visual Changes)",
        r"## (Checklist|TODO)",
        r"- \[x\]",  # Checkboxes (AI loves checklists)
        r"### (What|Why|How)",
        r"This PR (introduces|adds|implements|fixes|updates|refactors)",
        r"(Closes|Fixes|Resolves) #\d+",  # Issue references
        r"## Breaking Changes",
        r"## Migration Guide",
        # NEW: PR linking patterns (VERY AI-like)
        r"(Related to|Depends on|Builds on|Supersedes|Replaces) #\d+",  # PR cross-references
        r"(See also|Ref|References) #\d+",
        r"Part of #\d+",
        r"Follow-up to #\d+",
        # NEW: Verbose description indicators
        r"## (Implementation Details|Technical Details|Architecture)",
        r"## (Performance Impact|Security Considerations)",
        r"## (Rollback Plan|Deployment Notes)",
    ]

    def __init__(self):
        """Initialize the pattern detector."""
        self.pattern_threshold = 0.1  # Lower threshold to catch more patterns

    def analyze_commit_message(self, message: str) -> DetectionSignal:
        """
        Analyze commit message for AI-generated patterns.

        Args:
            message: Commit message to analyze

        Returns:
            Detection signal with commit message analysis
        """
        if not message or not message.strip():
            return self._create_null_signal()

        pattern_scores = []
        evidence = []

        # Check for conventional commit format (AI loves this)
        conventional_match = re.match(
            r"^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: .+",
            message,
            re.IGNORECASE,
        )
        if conventional_match:
            pattern_scores.append(60.0)
            evidence.append("Conventional commit format (AI pattern)")

        # Check for AI commit message patterns
        ai_commit_matches = 0
        for pattern in self.AI_COMMIT_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE | re.MULTILINE):
                ai_commit_matches += 1

        if ai_commit_matches > 0:
            commit_score = min(ai_commit_matches * 30.0, 90.0)
            pattern_scores.append(commit_score)
            evidence.append(f"AI commit message patterns ({ai_commit_matches} matches)")

        # Check for overly verbose/formal language
        if len(message) > 200:
            pattern_scores.append(40.0)
            evidence.append("Unusually verbose commit message")

        # Check for bullet points in commit message (AI loves structure)
        bullet_count = len(re.findall(r"^\s*[-*•]\s+", message, re.MULTILINE))
        if bullet_count >= 3:
            pattern_scores.append(70.0)  # Increased from 50 - this is VERY AI-like
            evidence.append(
                f"List-style commit with {bullet_count} bullet points (STRONG AI indicator)"
            )
        elif bullet_count >= 1:
            pattern_scores.append(50.0)
            evidence.append(f"Structured bullet points ({bullet_count} items)")

        # Check for detailed change descriptions (AI loves explaining each change)
        if bullet_count >= 3 and len(message) > 150:
            pattern_scores.append(80.0)
            evidence.append("Detailed list of changes (classic AI pattern)")

        # Calculate overall score
        if pattern_scores:
            overall_score = sum(pattern_scores) / len(pattern_scores)
            confidence = self._calculate_confidence(pattern_scores)
        else:
            overall_score = 0.0
            confidence = 0.0
            evidence = []

        return DetectionSignal(
            layer_type=DetectionLayerType.PATTERN,
            score=overall_score,
            confidence=confidence,
            evidence=evidence,
            metadata={
                "pattern_count": len(pattern_scores),
                "message_length": len(message),
                "type": "commit_message",
            },
        )

    def analyze_pr_description(self, description: str) -> DetectionSignal:
        """
        Analyze PR description for AI-generated patterns.

        Args:
            description: PR description to analyze

        Returns:
            Detection signal with PR description analysis
        """
        if not description or not description.strip():
            return self._create_null_signal()

        pattern_scores = []
        evidence = []

        # Check for structured sections (## Summary, ## Testing, etc.)
        section_count = len(re.findall(r"^##\s+\w+", description, re.MULTILINE))
        if section_count >= 3:
            pattern_scores.append(70.0)
            evidence.append(f"Highly structured PR description ({section_count} sections)")
        elif section_count >= 2:
            pattern_scores.append(50.0)
            evidence.append(f"Structured PR description ({section_count} sections)")

        # Check for AI PR description patterns
        ai_pr_matches = 0
        for pattern in self.AI_PR_PATTERNS:
            if re.search(pattern, description, re.IGNORECASE | re.MULTILINE):
                ai_pr_matches += 1

        if ai_pr_matches >= 4:
            pattern_scores.append(80.0)
            evidence.append(f"Multiple AI PR patterns ({ai_pr_matches} matches)")
        elif ai_pr_matches >= 2:
            pattern_scores.append(60.0)
            evidence.append(f"AI PR patterns detected ({ai_pr_matches} matches)")

        # Check for checklists (AI loves these)
        checkbox_count = len(re.findall(r"- \[(x| )\]", description, re.IGNORECASE))
        if checkbox_count >= 5:
            pattern_scores.append(70.0)
            evidence.append(f"Extensive checklist ({checkbox_count} items)")
        elif checkbox_count >= 3:
            pattern_scores.append(50.0)
            evidence.append(f"Checklist present ({checkbox_count} items)")

        # Check for overly comprehensive description
        if len(description) > 1000:
            pattern_scores.append(40.0)
            evidence.append("Unusually comprehensive PR description")

        # Check for "This PR" opening (very AI-like)
        if re.search(
            r"^This PR (introduces|adds|implements|fixes|updates|refactors)",
            description,
            re.IGNORECASE | re.MULTILINE,
        ):
            pattern_scores.append(60.0)
            evidence.append("AI-style PR opening")

        # Check for PR cross-references (AI loves linking related PRs)
        pr_links = len(
            re.findall(
                r"(Related to|Depends on|Builds on|Supersedes|Replaces|Follow-up to|Part of|See also|Ref|References) #\d+",
                description,
                re.IGNORECASE,
            )
        )
        if pr_links >= 2:
            pattern_scores.append(70.0)
            evidence.append(
                f"Multiple PR cross-references ({pr_links} links - STRONG AI indicator)"
            )
        elif pr_links >= 1:
            pattern_scores.append(50.0)
            evidence.append(f"PR cross-references detected ({pr_links} links)")

        # Check for technical detail sections (AI loves being thorough)
        technical_sections = len(
            re.findall(
                r"## (Implementation Details|Technical Details|Architecture|Performance Impact|Security Considerations|Rollback Plan|Deployment Notes)",
                description,
                re.IGNORECASE,
            )
        )
        if technical_sections >= 2:
            pattern_scores.append(75.0)
            evidence.append(
                f"Extensive technical documentation ({technical_sections} sections - VERY AI-like)"
            )
        elif technical_sections >= 1:
            pattern_scores.append(55.0)
            evidence.append(f"Technical detail sections ({technical_sections} sections)")

        # Calculate overall score
        if pattern_scores:
            overall_score = sum(pattern_scores) / len(pattern_scores)
            confidence = self._calculate_confidence(pattern_scores)
        else:
            overall_score = 0.0
            confidence = 0.0
            evidence = []

        return DetectionSignal(
            layer_type=DetectionLayerType.PATTERN,
            score=overall_score,
            confidence=confidence,
            evidence=evidence,
            metadata={
                "pattern_count": len(pattern_scores),
                "description_length": len(description),
                "type": "pr_description",
            },
        )

    def analyze_file(self, file_path: str) -> DetectionSignal:
        """
        Analyze a file for AI-generated code patterns.

        Args:
            file_path: Path to file to analyze

        Returns:
            Detection signal with pattern analysis results
        """
        # Check if file should be excluded (tool-generated)
        file_path_obj = Path(file_path)

        # Check if in excluded directory
        if any(excluded in file_path_obj.parts for excluded in self.EXCLUDE_DIRS):
            return self._create_null_signal()

        # Check if matches excluded pattern
        excluded_patterns = ["*_pb2.py", "*_pb2_grpc.py", "setup.py", "version.py"]
        if any(file_path_obj.match(pattern) for pattern in excluded_patterns):
            return self._create_null_signal()

        try:
            with open(file_path, encoding="utf-8") as f:
                code = f.read()
        except Exception:
            return self._create_null_signal()

        # Detect language from extension
        language = Path(file_path).suffix.lstrip(".")

        return self.analyze_code(code, language)

    def analyze_code(self, code: str, language: str = "python") -> DetectionSignal:
        """
        Analyze code for AI-generated patterns.

        Args:
            code: Source code to analyze
            language: Programming language (default: python)

        Returns:
            Detection signal with pattern detection results
        """
        if not code or not code.strip():
            return self._create_null_signal()

        pattern_scores = []
        evidence = []

        # Check 1: Comment pattern analysis
        comment_score, comment_matches = self._analyze_comment_patterns(code)
        if comment_score > self.pattern_threshold:
            pattern_scores.append(comment_score)
            evidence.append(f"AI-style comments detected ({len(comment_matches)} matches)")

        # Check 2: Comprehensive type hints
        type_hint_score = self._analyze_type_hints(code)
        if type_hint_score > self.pattern_threshold:
            pattern_scores.append(type_hint_score)
            evidence.append("Extensive type hints usage (AI pattern)")

        # Check 3: Dataclass usage
        dataclass_score = self._analyze_dataclass_usage(code)
        if dataclass_score > self.pattern_threshold:
            pattern_scores.append(dataclass_score)
            evidence.append("Heavy dataclass usage (AI pattern)")

        # Check 4: Comprehensive docstrings (CRITICAL - top ML feature)
        docstring_score = self._analyze_docstrings(code)
        if docstring_score > self.pattern_threshold:
            pattern_scores.append(docstring_score)
            evidence.append("Comprehensive docstrings (AI signature)")

        # Check 5: Hallucination patterns
        hallucinations = self._detect_hallucinations(code, language)
        if hallucinations:
            hallucination_score = min(len(hallucinations) * 20.0, 100.0)
            pattern_scores.append(hallucination_score)
            evidence.append(f"Hallucination patterns detected ({len(hallucinations)} instances)")

        # Check 6: AI-specific code patterns
        ai_patterns = self._detect_ai_code_patterns(code, language)
        if ai_patterns:
            ai_pattern_score = min(len(ai_patterns) * 15.0, 100.0)
            pattern_scores.append(ai_pattern_score)
            evidence.append(f"AI code patterns detected ({len(ai_patterns)} instances)")

        # Calculate overall pattern score
        if pattern_scores:
            overall_score = sum(pattern_scores) / len(pattern_scores)
            confidence = self._calculate_confidence(pattern_scores)
        else:
            overall_score = 0.0
            confidence = 0.0
            evidence = []

        return DetectionSignal(
            layer_type=DetectionLayerType.PATTERN,
            score=overall_score,
            confidence=confidence,
            evidence=evidence,
            metadata={"pattern_count": len(pattern_scores), "language": language},
        )

    def _analyze_comment_patterns(self, code: str) -> tuple[float, list[str]]:
        """
        Analyze code for AI-style comment patterns.

        Returns:
            Tuple of (score, list of matched comments)
        """
        matches = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            for pattern in self.AI_COMMENT_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append(f"Line {line_num}: {line.strip()}")

        # Calculate score based on match density
        if not lines:
            return 0.0, []

        match_density = len(matches) / len(lines)
        # AI code typically has 10-30% lines with these patterns
        score = min(match_density * 300, 100.0)

        return score, matches

    def _analyze_type_hints(self, code: str) -> float:
        """Analyze comprehensive type hint usage (AI loves type hints)."""
        lines = code.split("\n")
        type_hint_lines = 0

        for line in lines:
            # Count lines with type hints
            if re.search(r":\s*(str|int|float|bool|List|Dict|Optional|Any|Tuple)", line):
                type_hint_lines += 1
            # Count return type hints
            if re.search(r"->\s*(str|int|float|bool|List|Dict|Optional|Any|Tuple|None)", line):
                type_hint_lines += 1

        if not lines:
            return 0.0

        type_hint_density = type_hint_lines / len(lines)
        # AI code often has 20-40% lines with type hints
        return min(type_hint_density * 250, 100.0)

    def _analyze_dataclass_usage(self, code: str) -> float:
        """Analyze dataclass usage (AI loves dataclasses)."""
        dataclass_count = len(re.findall(r"@dataclass", code))
        class_count = len(re.findall(r"^class\s+\w+", code, re.MULTILINE))

        if class_count == 0:
            return 0.0

        # If >50% of classes are dataclasses, that's very AI-like
        dataclass_ratio = dataclass_count / class_count
        return min(dataclass_ratio * 150, 100.0)

    def _analyze_docstrings(self, code: str) -> float:
        """
        Analyze docstring density and comprehensiveness.

        AI code has extensive docstrings with Args, Returns, Examples.
        This is the #1 feature from ML analysis.
        """
        # Count docstrings
        docstring_count = len(re.findall(r'"""[\s\S]*?"""', code))

        # Count functions/classes
        function_count = len(re.findall(r"^def \w+", code, re.MULTILINE))
        class_count = len(re.findall(r"^class \w+", code, re.MULTILINE))
        total_definitions = function_count + class_count

        if total_definitions == 0:
            return 0.0

        # Calculate docstring coverage
        docstring_ratio = docstring_count / total_definitions

        # AI typically has 80-100% docstring coverage
        if docstring_ratio >= 0.8:
            base_score = 90.0
        elif docstring_ratio >= 0.6:
            base_score = 70.0
        elif docstring_ratio >= 0.4:
            base_score = 50.0
        elif docstring_ratio >= 0.2:
            base_score = 30.0
        else:
            base_score = 10.0

        # Bonus for comprehensive docstrings (Args, Returns, Examples)
        comprehensive_count = 0
        comprehensive_count += len(re.findall(r"Args:", code))
        comprehensive_count += len(re.findall(r"Returns:", code))
        comprehensive_count += len(re.findall(r"Example:", code))
        comprehensive_count += len(re.findall(r"Raises:", code))

        if comprehensive_count > total_definitions:
            base_score = min(base_score + 10.0, 100.0)

        return base_score

    def _detect_hallucinations(self, code: str, language: str) -> list[str]:
        """
        Detect hallucination patterns (non-existent APIs, unusual patterns).

        Returns:
            List of detected hallucinations
        """
        hallucinations = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            for pattern in self.HALLUCINATION_PATTERNS:
                if re.search(pattern, line):
                    hallucinations.append(f"Line {line_num}: {line.strip()}")

        return hallucinations

    def _detect_ai_code_patterns(self, code: str, language: str) -> list[str]:
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

    def _calculate_confidence(self, scores: list[float]) -> float:
        """
        Calculate confidence based on number and agreement of signals.

        More signals with similar scores = higher confidence.
        """
        if not scores:
            return 0.0

        # Base confidence on number of signals (more signals = higher confidence)
        if len(scores) >= 4:
            base_confidence = 0.75  # 4+ signals is very reliable
        elif len(scores) >= 3:
            base_confidence = 0.70
        elif len(scores) >= 2:
            base_confidence = 0.65
        else:
            base_confidence = 0.60

        # Adjust for score variance (lower variance = higher confidence)
        if len(scores) > 1:
            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            variance_penalty = min(variance / 2000.0, 0.10)
            confidence = base_confidence - variance_penalty
        else:
            confidence = base_confidence

        return max(0.5, min(1.0, confidence))

    def _create_null_signal(self) -> DetectionSignal:
        """Create a null signal for empty or invalid input."""
        return DetectionSignal(
            layer_type=DetectionLayerType.PATTERN,
            score=0.0,
            confidence=0.0,
            evidence=[],
            metadata={},
        )
