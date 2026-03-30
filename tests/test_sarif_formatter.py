"""
Tests for SARIF Formatter
"""

import json
import pytest
from src.vibemetric.formatters import SARIFFormatter


class TestSARIFFormatter:
    """Test suite for SARIF formatter"""
    
    def test_sarif_version(self):
        """Test SARIF version is 2.1.0"""
        formatter = SARIFFormatter()
        assert formatter.SARIF_VERSION == "2.1.0"
    
    def test_format_basic_results(self):
        """Test formatting basic scan results"""
        formatter = SARIFFormatter(version="0.1.0")
        
        results = {
            "repository": "/path/to/repo",
            "vibe_score": {
                "overall_score": 45.0,
                "ai_assistance_level": "PARTIAL",
                "confidence": 0.8,
                "interpretation": "Test interpretation",
                "recommendations": ["Test recommendation"]
            },
            "pattern_results": [],
            "ml_results": []
        }
        
        sarif_output = formatter.format(results)
        sarif_data = json.loads(sarif_output)
        
        # Validate structure
        assert sarif_data["version"] == "2.1.0"
        assert "$schema" in sarif_data
        assert "runs" in sarif_data
        assert len(sarif_data["runs"]) == 1
    
    def test_tool_metadata(self):
        """Test tool metadata in SARIF output"""
        formatter = SARIFFormatter(version="0.1.0")
        
        results = {
            "repository": "/path/to/repo",
            "vibe_score": {
                "overall_score": 45.0,
                "ai_assistance_level": "PARTIAL",
                "confidence": 0.8,
                "interpretation": "Test",
                "recommendations": []
            },
            "pattern_results": [],
            "ml_results": []
        }
        
        sarif_output = formatter.format(results)
        sarif_data = json.loads(sarif_output)
        
        tool = sarif_data["runs"][0]["tool"]["driver"]
        assert tool["name"] == "Vibemetric"
        assert tool["version"] == "0.1.0"
        assert tool["informationUri"] == "https://vibemetric.ai"
        assert "rules" in tool
        assert len(tool["rules"]) == 3  # 3 rules defined
    
    def test_rules_defined(self):
        """Test that all rules are properly defined"""
        formatter = SARIFFormatter()
        
        results = {
            "repository": "/path/to/repo",
            "vibe_score": {
                "overall_score": 45.0,
                "ai_assistance_level": "PARTIAL",
                "confidence": 0.8,
                "interpretation": "Test",
                "recommendations": []
            },
            "pattern_results": [],
            "ml_results": []
        }
        
        sarif_output = formatter.format(results)
        sarif_data = json.loads(sarif_output)
        
        rules = sarif_data["runs"][0]["tool"]["driver"]["rules"]
        rule_ids = [rule["id"] for rule in rules]
        
        assert "substantial-ai-assistance" in rule_ids
        assert "partial-ai-assistance" in rule_ids
        assert "minimal-ai-assistance" in rule_ids
    
    def test_file_level_results(self):
        """Test file-level results in SARIF output"""
        formatter = SARIFFormatter()
        
        results = {
            "repository": "/path/to/repo",
            "vibe_score": {
                "overall_score": 45.0,
                "ai_assistance_level": "PARTIAL",
                "confidence": 0.8,
                "interpretation": "Test",
                "recommendations": []
            },
            "pattern_results": [
                {
                    "file": "test.py",
                    "score": 75.0,
                    "confidence": 0.8,
                    "patterns": 5
                }
            ],
            "ml_results": []
        }
        
        sarif_output = formatter.format(results)
        sarif_data = json.loads(sarif_output)
        
        results_list = sarif_data["runs"][0]["results"]
        assert len(results_list) == 1
        
        result = results_list[0]
        assert result["ruleId"] == "substantial-ai-assistance"
        assert result["level"] == "error"
        assert "75.0" in result["message"]["text"]
        assert "5 AI patterns" in result["message"]["text"]
        
        # Check location includes filename
        location = result["locations"][0]["physicalLocation"]["artifactLocation"]
        assert location["uri"] == "test.py"
    
    def test_severity_mapping(self):
        """Test severity level mapping"""
        formatter = SARIFFormatter()
        
        # Test SUBSTANTIAL (70-100) -> error
        rule_id, level = formatter._get_rule_and_level(85.0)
        assert rule_id == "substantial-ai-assistance"
        assert level == "error"
        
        # Test PARTIAL (40-70) -> warning
        rule_id, level = formatter._get_rule_and_level(55.0)
        assert rule_id == "partial-ai-assistance"
        assert level == "warning"
        
        # Test MINIMAL (0-40) -> note
        rule_id, level = formatter._get_rule_and_level(25.0)
        assert rule_id == "minimal-ai-assistance"
        assert level == "note"
    
    def test_ml_results_included(self):
        """Test ML detection results are included"""
        formatter = SARIFFormatter()
        
        results = {
            "repository": "/path/to/repo",
            "vibe_score": {
                "overall_score": 45.0,
                "ai_assistance_level": "PARTIAL",
                "confidence": 0.8,
                "interpretation": "Test",
                "recommendations": []
            },
            "pattern_results": [],
            "ml_results": [
                {
                    "file": "module.py",
                    "score": 85.0,
                    "confidence": 0.85,
                    "prediction": "AI"
                }
            ]
        }
        
        sarif_output = formatter.format(results)
        sarif_data = json.loads(sarif_output)
        
        results_list = sarif_data["runs"][0]["results"]
        assert len(results_list) == 1
        
        result = results_list[0]
        assert result["properties"]["detection_method"] == "ml"
        assert result["properties"]["prediction"] == "AI"
    
    def test_low_score_files_excluded(self):
        """Test that low-score files are excluded from SARIF"""
        formatter = SARIFFormatter()
        
        results = {
            "repository": "/path/to/repo",
            "vibe_score": {
                "overall_score": 45.0,
                "ai_assistance_level": "PARTIAL",
                "confidence": 0.8,
                "interpretation": "Test",
                "recommendations": []
            },
            "pattern_results": [
                {
                    "file": "low_score.py",
                    "score": 25.0,  # Below 40 threshold
                    "confidence": 0.6,
                    "patterns": 1
                }
            ],
            "ml_results": [
                {
                    "file": "human.py",
                    "score": 30.0,  # Below 50 threshold for ML
                    "confidence": 0.85,
                    "prediction": "Human"
                }
            ]
        }
        
        sarif_output = formatter.format(results)
        sarif_data = json.loads(sarif_output)
        
        results_list = sarif_data["runs"][0]["results"]
        # Should have 1 result (repository-level) since files are below threshold
        assert len(results_list) == 1
        assert results_list[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "."
    
    def test_repository_level_result(self):
        """Test repository-level result when no file results"""
        formatter = SARIFFormatter()
        
        results = {
            "repository": "/path/to/repo",
            "vibe_score": {
                "overall_score": 75.0,
                "ai_assistance_level": "SUBSTANTIAL",
                "confidence": 0.9,
                "interpretation": "High AI usage detected",
                "recommendations": ["Review policies"]
            },
            "pattern_results": [],
            "ml_results": []
        }
        
        sarif_output = formatter.format(results)
        sarif_data = json.loads(sarif_output)
        
        results_list = sarif_data["runs"][0]["results"]
        assert len(results_list) == 1
        
        result = results_list[0]
        assert result["ruleId"] == "substantial-ai-assistance"
        assert result["level"] == "error"
        assert "SUBSTANTIAL" in result["message"]["text"]
        assert result["properties"]["overall_score"] == 75.0
    
    def test_properties_included(self):
        """Test that properties are included in results"""
        formatter = SARIFFormatter()
        
        results = {
            "repository": "/path/to/repo",
            "vibe_score": {
                "overall_score": 65.0,
                "ai_assistance_level": "PARTIAL",
                "confidence": 0.85,
                "interpretation": "Test",
                "recommendations": ["Rec 1", "Rec 2"]
            },
            "pattern_results": [],
            "ml_results": []
        }
        
        sarif_output = formatter.format(results)
        sarif_data = json.loads(sarif_output)
        
        properties = sarif_data["runs"][0]["properties"]["vibemetric"]
        assert properties["overall_score"] == 65.0
        assert properties["ai_assistance_level"] == "PARTIAL"
        assert properties["confidence"] == 0.85
