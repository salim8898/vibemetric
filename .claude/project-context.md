# Vibemetric Project Context for Claude

## What is Vibemetric?

An enterprise-grade AI code detection platform that helps engineering managers track AI tool adoption and measure productivity impact. Built with Python 3.9+, it uses a 4-layer detection system with 152 tests and 85%+ coverage.

## Project Status

- **Phase 1**: Complete (4-layer detection, CLI, 152 tests)
- **Phase 1.5**: 67% complete (SARIF, profiles, team reports, PR analysis)
- **Phase 2**: Planned (model detection, dashboard, advanced analytics)

## Architecture Overview

### Detection Layers
1. **Artifact Detector** - Scans for AI tool config files (90% accuracy)
2. **Velocity Analyzer** - Detects coding speed changes (80% accuracy)
3. **Pattern Detector** - Identifies AI code patterns (70% accuracy)
4. **ML Detector** - Statistical analysis with Random Forest (85% accuracy)

### Score Combination
```
Combined = (Artifact × 0.40) + (Velocity × 0.25) + 
           (Pattern × 0.20) + (ML × 0.15)
```

Weights based on layer reliability and accuracy.

## Development Guidelines

### Code Style
- Python 3.9+ with type hints
- Black formatting (100 char lines)
- Google-style docstrings
- PEP 8 compliance
- Ruff linting

### Testing Requirements
- Write tests FIRST (TDD)
- Use pytest with fixtures
- Mock external dependencies
- Aim for 80%+ coverage
- Test success and failure cases

### Workflow
1. Create feature branch
2. Write tests
3. Implement feature
4. Run `pytest`
5. Format with `black`
6. Lint with `ruff`
7. Open PR (never push to main)

## Key Files to Know

### Core Detection
- `src/vibemetric/detectors/artifact_detector.py` - Config file detection
- `src/vibemetric/detectors/velocity_analyzer.py` - Velocity analysis
- `src/vibemetric/detectors/pattern_detector.py` - Pattern matching
- `src/vibemetric/detectors/ml_detector.py` - ML-based detection

### Scoring & Models
- `src/vibemetric/scorer.py` - Score combination logic
- `src/vibemetric/models.py` - Data models and enums
- `src/vibemetric/ml/feature_extractor.py` - ML features

### CLI & Integrations
- `src/vibemetric/cli.py` - CLI commands
- `src/vibemetric/integrations/pr_analyzer.py` - PR analysis
- `src/vibemetric/integrations/github_client.py` - GitHub API
- `src/vibemetric/profiles/developer_profile.py` - Developer profiles
- `src/vibemetric/reports/team_report.py` - Team analytics

### Tests
- `tests/conftest.py` - Shared fixtures
- `tests/test_*.py` - 152 unit tests

### Documentation
- `README.md` - Project overview
- `USAGE_GUIDE.md` - Detailed usage
- `SCORING_GUIDE.md` - Scoring explanations
- `CONTRIBUTING.md` - Contribution guidelines

## Common Patterns

### Detection Layer Pattern
```python
from typing import Dict, Any
from vibemetric.models import DetectionSignal

class NewDetector:
    """Detector for specific AI signals."""
    
    def detect(self) -> Dict[str, Any]:
        """Run detection and return raw results."""
        results = {}
        # Detection logic
        return results
    
    def get_detection_signal(
        self, 
        results: Dict[str, Any]
    ) -> DetectionSignal:
        """Convert results to DetectionSignal."""
        score = self._calculate_score(results)
        confidence = self._calculate_confidence(results)
        
        return DetectionSignal(
            score=score,
            confidence=confidence,
            details=results
        )
```

### Test Pattern
```python
import pytest
from vibemetric.module import Class

class TestFeature:
    """Test suite for feature."""
    
    def test_success_case(self):
        """Test normal operation."""
        obj = Class()
        result = obj.method()
        assert result == expected
    
    def test_error_case(self):
        """Test error handling."""
        obj = Class()
        with pytest.raises(ValueError):
            obj.method(invalid_input)
```

## Dependencies

### Core
- gitpython>=3.1.0 - Git operations
- click>=8.0.0 - CLI framework
- rich>=13.0.0 - Terminal formatting
- pyyaml>=6.0.0 - Config parsing
- requests>=2.31.0 - HTTP requests
- pygithub>=2.1.0 - GitHub API

### ML
- numpy>=1.24.0 - Numerical operations
- scikit-learn>=1.3.0 - ML models

### Dev
- pytest>=7.0.0 - Testing
- black>=23.0.0 - Formatting
- ruff>=0.1.0 - Linting
- mypy>=1.0.0 - Type checking

## Terminology

- **Vibe Score**: Overall AI likelihood score (0-100)
- **Detection Signal**: Output from a detection layer
- **AI Assistance Level**: MINIMAL, PARTIAL, or SUBSTANTIAL
- **Artifact**: AI tool configuration file
- **Velocity Spike**: 1.8x+ increase in coding speed
- **Pattern**: AI-specific code characteristic

## Testing Strategy

### Unit Tests (Current)
- 152 tests in `tests/` directory
- Mock git repos and GitHub API
- Test each layer independently
- 85%+ coverage

### Integration Tests (Minimal)
- Test full scan workflow
- Test CLI commands end-to-end
- Use real git repos for validation

### Manual Testing
- Test on real repositories (Flask, Django, etc.)
- Validate accuracy on known AI/human code
- Check performance on large repos

## Known Issues

- Velocity analysis inaccurate for squash merge workflows
- ML model may flag very clean human code
- Small sample sizes (default 10 files) may miss patterns
- See KNOWN_ISSUES.md for full list

## Roadmap

### Phase 1.5 (Current)
- ✅ SARIF output format
- ✅ Developer profile command
- ✅ Team report command
- ✅ Scan PR command
- ⏳ MCP server integration
- ⏳ PyPI package

### Phase 2 (Planned)
- Model detection (GPT-4 vs Claude vs Copilot)
- Team analytics dashboard
- PR-based velocity analysis
- Custom detection rules

## Contributing

1. Fork repository
2. Create feature branch
3. Write tests first
4. Implement feature
5. Run test suite
6. Open PR (CI will run automatically)
7. Address review feedback
8. Maintainer merges

## Branch Protection

- Main branch is protected
- All changes require PR
- CI must pass (tests, lint, type check)
- 1 approval required
- No direct pushes allowed

## Quick Commands

```bash
# Run tests
pytest

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/vibemetric/

# Coverage report
pytest --cov=vibemetric --cov-report=html

# Install dev dependencies
pip install -e ".[dev,ml]"
```

## Need Help?

- Read CONTRIBUTING.md for detailed guidelines
- Check existing tests for patterns
- Review USAGE_GUIDE.md for feature details
- Open GitHub issue or discussion
- All PRs welcome!
