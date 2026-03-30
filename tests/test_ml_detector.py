"""
Tests for ML Detector
"""

import pytest
from vibemetric.detectors.ml_detector import MLDetector
from vibemetric.models import DetectionLayerType


class TestMLDetector:
    """Test ML detector functionality"""
    
    @pytest.fixture
    def detector(self):
        """Create ML detector instance"""
        return MLDetector()
    
    def test_model_initialization(self, detector):
        """Test that ML detector initializes"""
        assert detector is not None
        # Model may or may not be available depending on environment
    
    def test_analyze_code_with_model(self, detector):
        """Test code analysis when model is available"""
        code = '''
def calculate_sum(a: int, b: int) -> int:
    """
    Calculate the sum of two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b
'''
        signal = detector.analyze_code(code)
        
        assert signal.layer_type == DetectionLayerType.ML
        assert signal.score >= 0
        assert signal.score <= 100
        
        if detector.model_available:
            # If model is available, should have meaningful results
            assert signal.confidence > 0
            assert len(signal.evidence) > 0
        else:
            # If model not available, should return null signal
            assert signal.score == 0
            assert signal.confidence == 0
    
    def test_analyze_empty_code(self, detector):
        """Test handling of empty code"""
        signal = detector.analyze_code("")
        
        assert signal.score == 0.0
        assert signal.confidence == 0.0
    
    def test_analyze_code_without_model(self):
        """Test graceful fallback when model not available"""
        detector = MLDetector(model_path="nonexistent.pkl")
        
        code = "def test(): pass"
        signal = detector.analyze_code(code)
        
        assert signal.score == 0.0
        assert signal.confidence == 0.0
        assert not detector.model_available
    
    def test_metadata_includes_model_info(self, detector):
        """Test that metadata includes model information"""
        code = "def test(): pass"
        signal = detector.analyze_code(code)
        
        assert "model_available" in signal.metadata
        
        if detector.model_available:
            assert signal.metadata["model_type"] == "RandomForest"
            assert "DROID" in signal.metadata["training_data"]
    
    def test_different_languages(self, detector):
        """Test analysis of different programming languages"""
        python_code = "def test(): pass"
        js_code = "function test() { return true; }"
        
        python_signal = detector.analyze_code(python_code, "python")
        js_signal = detector.analyze_code(js_code, "javascript")
        
        assert python_signal.layer_type == DetectionLayerType.ML
        assert js_signal.layer_type == DetectionLayerType.ML
