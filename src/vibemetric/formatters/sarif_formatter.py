"""
SARIF (Static Analysis Results Interchange Format) Formatter

Generates SARIF 2.1.0 compliant output for GitHub Code Scanning integration.
"""

import json
from typing import Any, Optional


class SARIFFormatter:
    """
    Formats Vibemetric scan results as SARIF 2.1.0.

    SARIF is the standard format for static analysis tools,
    enabling integration with GitHub Code Scanning and other platforms.
    """

    SARIF_VERSION = "2.1.0"
    SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"

    def __init__(self, version: str = "0.1.0"):
        """
        Initialize SARIF formatter.

        Args:
            version: Vibemetric version string
        """
        self.version = version

    def format(self, results: dict[str, Any]) -> str:
        """
        Format scan results as SARIF JSON.

        Args:
            results: Scan results dictionary from CLI

        Returns:
            SARIF JSON string
        """
        sarif_output = {
            "version": self.SARIF_VERSION,
            "$schema": self.SARIF_SCHEMA,
            "runs": [self._create_run(results)],
        }

        return json.dumps(sarif_output, indent=2)

    def _create_run(self, results: dict[str, Any]) -> dict[str, Any]:
        """Create SARIF run object."""
        return {
            "tool": self._create_tool(),
            "results": self._create_results(results),
            "properties": {
                "vibemetric": {
                    "overall_score": results["vibe_score"]["overall_score"],
                    "ai_assistance_level": results["vibe_score"]["ai_assistance_level"],
                    "confidence": results["vibe_score"]["confidence"],
                }
            },
        }

    def _create_tool(self) -> dict[str, Any]:
        """Create SARIF tool object."""
        return {
            "driver": {
                "name": "Vibemetric",
                "version": self.version,
                "informationUri": "https://vibemetric.ai",
                "organization": "Vibemetric",
                "shortDescription": {"text": "AI code detection platform"},
                "fullDescription": {
                    "text": "Vibemetric detects AI-generated code using 4-layer detection system: artifact detection, velocity analysis, pattern recognition, and ML-based analysis."
                },
                "rules": self._create_rules(),
            }
        }

    def _create_rules(self) -> list[dict[str, Any]]:
        """Create SARIF rule definitions."""
        return [
            {
                "id": "substantial-ai-assistance",
                "name": "SubstantialAIAssistance",
                "shortDescription": {"text": "File shows substantial AI assistance"},
                "fullDescription": {
                    "text": "This file has a high AI likelihood score (70-100/100), indicating substantial AI tool usage. Multiple detection layers confirm significant AI contribution."
                },
                "defaultConfiguration": {"level": "error"},
                "help": {
                    "text": "Review this file for AI-generated code. Ensure proper code review and quality standards are maintained.",
                    "markdown": "## Substantial AI Assistance\n\nThis file shows substantial AI assistance (70-100/100).\n\n### Recommendations\n- Review AI tool usage policies\n- Ensure proper code review\n- Verify code quality and correctness\n- Document AI tool usage",
                },
                "properties": {"tags": ["ai-detection", "code-quality"], "precision": "high"},
            },
            {
                "id": "partial-ai-assistance",
                "name": "PartialAIAssistance",
                "shortDescription": {"text": "File shows partial AI assistance"},
                "fullDescription": {
                    "text": "This file has a moderate AI likelihood score (40-70/100), suggesting mixed human-AI collaboration or selective AI usage."
                },
                "defaultConfiguration": {"level": "warning"},
                "help": {
                    "text": "This file shows partial AI assistance. Consider establishing clear AI usage guidelines.",
                    "markdown": "## Partial AI Assistance\n\nThis file shows partial AI assistance (40-70/100).\n\n### Recommendations\n- Establish clear AI usage guidelines\n- Track AI adoption across team\n- Review code patterns for consistency",
                },
                "properties": {"tags": ["ai-detection", "code-quality"], "precision": "medium"},
            },
            {
                "id": "minimal-ai-assistance",
                "name": "MinimalAIAssistance",
                "shortDescription": {"text": "File shows minimal AI assistance"},
                "fullDescription": {
                    "text": "This file has a low AI likelihood score (0-40/100), indicating primarily human-authored code with little to no AI tool usage."
                },
                "defaultConfiguration": {"level": "note"},
                "help": {
                    "text": "This file appears to be primarily human-written. No immediate action needed.",
                    "markdown": "## Minimal AI Assistance\n\nThis file shows minimal AI assistance (0-40/100).\n\nLikely human-written with traditional development practices.",
                },
                "properties": {"tags": ["ai-detection", "code-quality"], "precision": "medium"},
            },
        ]

    def _create_results(self, results: dict[str, Any]) -> list[dict[str, Any]]:
        """Create SARIF results from scan data."""
        sarif_results = []

        # Add file-level results from pattern detection
        if "pattern_results" in results and results["pattern_results"]:
            for file_result in results["pattern_results"]:
                sarif_result = self._create_file_result(file_result, results["repository"])
                if sarif_result:
                    sarif_results.append(sarif_result)

        # Add file-level results from ML detection
        if "ml_results" in results and results["ml_results"]:
            for file_result in results["ml_results"]:
                sarif_result = self._create_ml_file_result(file_result, results["repository"])
                if sarif_result:
                    sarif_results.append(sarif_result)

        # If no file-level results, add repository-level result
        if not sarif_results:
            sarif_results.append(self._create_repository_result(results))

        return sarif_results

    def _create_file_result(
        self, file_result: dict[str, Any], repo_path: str
    ) -> Optional[dict[str, Any]]:
        """Create SARIF result for a file from pattern detection."""
        score = file_result["score"]
        filename = file_result["file"]

        # Determine rule and level
        rule_id, level = self._get_rule_and_level(score)

        # Only report files with score > 40 (PARTIAL or SUBSTANTIAL)
        if score < 40:
            return None

        return {
            "ruleId": rule_id,
            "level": level,
            "message": {
                "text": f"This file shows {self._get_assistance_text(score)} AI assistance ({score:.1f}/100). Detected {file_result['patterns']} AI patterns."
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": filename, "uriBaseId": "%SRCROOT%"},
                        "region": {"startLine": 1},
                    }
                }
            ],
            "properties": {
                "ai_score": score,
                "confidence": file_result["confidence"],
                "patterns_detected": file_result["patterns"],
                "detection_method": "pattern",
            },
        }

    def _create_ml_file_result(
        self, file_result: dict[str, Any], repo_path: str
    ) -> Optional[dict[str, Any]]:
        """Create SARIF result for a file from ML detection."""
        score = file_result["score"]
        filename = file_result["file"]

        # Determine rule and level
        rule_id, level = self._get_rule_and_level(score)

        # Only report files with score > 50 (AI prediction)
        if score < 50:
            return None

        return {
            "ruleId": rule_id,
            "level": level,
            "message": {
                "text": f"ML model predicts {file_result['prediction']} ({score:.1f}/100 AI likelihood). Statistical analysis suggests AI-generated code."
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": filename, "uriBaseId": "%SRCROOT%"},
                        "region": {"startLine": 1},
                    }
                }
            ],
            "properties": {
                "ai_score": score,
                "confidence": file_result["confidence"],
                "prediction": file_result["prediction"],
                "detection_method": "ml",
            },
        }

    def _create_repository_result(self, results: dict[str, Any]) -> dict[str, Any]:
        """Create repository-level SARIF result."""
        vibe_score = results["vibe_score"]
        score = vibe_score["overall_score"]
        level_str = vibe_score["ai_assistance_level"]

        rule_id, level = self._get_rule_and_level(score)

        return {
            "ruleId": rule_id,
            "level": level,
            "message": {
                "text": f"Repository shows {level_str} AI assistance ({score:.1f}/100). {vibe_score['interpretation']}"
            },
            "locations": [
                {"physicalLocation": {"artifactLocation": {"uri": ".", "uriBaseId": "%SRCROOT%"}}}
            ],
            "properties": {
                "overall_score": score,
                "ai_assistance_level": level_str,
                "confidence": vibe_score["confidence"],
                "recommendations": vibe_score["recommendations"],
            },
        }

    def _get_rule_and_level(self, score: float) -> tuple[str, str]:
        """
        Get SARIF rule ID and level based on score.

        Args:
            score: AI likelihood score (0-100)

        Returns:
            Tuple of (rule_id, level)
        """
        if score >= 70:
            return ("substantial-ai-assistance", "error")
        elif score >= 40:
            return ("partial-ai-assistance", "warning")
        else:
            return ("minimal-ai-assistance", "note")

    def _get_assistance_text(self, score: float) -> str:
        """Get assistance level text from score."""
        if score >= 70:
            return "substantial"
        elif score >= 40:
            return "partial"
        else:
            return "minimal"
