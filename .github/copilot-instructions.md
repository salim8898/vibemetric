# GitHub Copilot Instructions for Vibemetric

## Project Type
Python library for AI code detection with CLI interface

## Code Style
- Python 3.9+ with type hints
- Black formatting (100 char line length)
- Google-style docstrings
- PEP 8 compliance

## Testing Requirements
- All new code needs pytest tests
- Use fixtures from `tests/conftest.py`
- Mock external dependencies (git, GitHub API)
- Aim for 80%+ coverage

## Common Patterns

### Detection Layer Pattern
```python
from typing import Dict, Any
from vibemetric.models import DetectionSignal

class NewDetector:
    def detect(self) -> Dict[str, Any]:
        """Run detection and return raw results."""
        pass
    
    def get_detection_signal(self, results: Dict[str, Any]) -> DetectionSignal:
        """Convert results to DetectionSignal."""
        return DetectionSignal(
            score=calculated_score,
            confidence=calculated_confidence,
            details={"key": "value"}
        )
```

### Test Pattern
```python
import pytest
from vibemetric.module import Class

class TestClass:
    def test_method_success(self):
        obj = Class()
        result = obj.method()
        assert result == expected
```

## Key Modules
- `detectors/` - 4 detection layers
- `scorer.py` - Score combination
- `cli.py` - CLI commands
- `models.py` - Data models

## Dependencies
- GitPython for git operations
- Rich for terminal output
- scikit-learn for ML
- pytest for testing

## Workflow
1. Write test first
2. Implement feature
3. Run `pytest`
4. Format with `black`
5. Lint with `ruff`
