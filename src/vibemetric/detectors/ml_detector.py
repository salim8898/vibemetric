"""
ML Detector - Layer 4 (85% Accuracy)

Uses trained Random Forest model to detect AI-generated code.
Trained on DROID dataset (846k samples) covering GPT-4, Copilot, and other models.

This is a fallback layer that works when other detectors don't have strong signals.
Particularly effective for GPT-4 and GitHub Copilot detection.
"""

from pathlib import Path

from ..models import DetectionLayerType, DetectionSignal


class MLDetector:
    """
    ML-based detector using trained Random Forest model.

    Detects AI code from GPT-4, Copilot, and other models included in DROID training data.
    Falls back gracefully if model not available.
    """

    def __init__(self, model_path: str = "models/ai_detector.pkl"):
        """
        Initialize ML detector and load model if available.

        Args:
            model_path: Path to trained model file
        """
        self.model = None
        self.feature_extractor = None
        self.model_available = False

        # Try to load model
        try:
            import joblib

            from ..ml.feature_extractor import FeatureExtractor

            # Check if model exists
            model_file = Path(model_path)
            if not model_file.exists():
                # Try relative to project root
                model_file = Path(__file__).parent.parent.parent.parent / model_path

            if model_file.exists():
                self.model = joblib.load(str(model_file))
                self.feature_extractor = FeatureExtractor()
                self.model_available = True
        except Exception:
            # Model not available - will return null signals
            pass

    def analyze_code(self, code: str, language: str = "python") -> DetectionSignal:
        """
        Detect AI-generated code using ML model.

        Args:
            code: Source code to analyze
            language: Programming language (default: python)

        Returns:
            Detection signal with ML prediction
        """
        if not self.model_available or not code or not code.strip():
            return self._create_null_signal()

        try:
            import pandas as pd

            # Extract features
            features = self.feature_extractor.extract_features(code, language)

            # Predict
            X = pd.DataFrame([features])
            probability = self.model.predict_proba(X)[0][1]  # P(AI)

            score = probability * 100
            confidence = 0.85  # ML is reliable for models it was trained on

            evidence = [
                f"ML model prediction: {probability:.2%} AI likelihood",
                "Trained on DROID dataset (GPT-4, Copilot, etc.)",
            ]

            return DetectionSignal(
                layer_type=DetectionLayerType.ML,
                score=score,
                confidence=confidence,
                evidence=evidence,
                metadata={
                    "probability": probability,
                    "model_available": True,
                    "model_type": "RandomForest",
                    "training_data": "DROID (846k samples)",
                },
            )
        except Exception as e:
            return self._create_null_signal(f"ML prediction failed: {str(e)}")

    def analyze_file(self, file_path: str) -> DetectionSignal:
        """
        Analyze a file using ML model.

        Args:
            file_path: Path to file to analyze

        Returns:
            Detection signal with ML prediction
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                code = f.read()
        except Exception:
            return self._create_null_signal("Could not read file")

        # Detect language from extension
        language = Path(file_path).suffix.lstrip(".")

        return self.analyze_code(code, language)

    def _create_null_signal(self, reason: str = "Model not available") -> DetectionSignal:
        """Create null signal when ML unavailable."""
        return DetectionSignal(
            layer_type=DetectionLayerType.ML,
            score=0.0,
            confidence=0.0,
            evidence=[f"ML unavailable: {reason}"],
            metadata={"model_available": False},
        )
