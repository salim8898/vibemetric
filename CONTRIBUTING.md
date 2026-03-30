# Contributing to Vibemetric

Thank you for your interest in contributing to Vibemetric! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Submitting Changes](#submitting-changes)
7. [Coding Standards](#coding-standards)
8. [Project Structure](#project-structure)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, gender identity, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting comments, or personal attacks
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of AI code detection concepts
- Familiarity with pytest for testing

### Find an Issue

1. Browse [open issues](https://github.com/salim8898/vibemetric/issues)
2. Look for issues labeled `good first issue` or `help wanted`
3. Comment on the issue to let others know you're working on it
4. Wait for maintainer approval before starting work

### Ask Questions

- Open a [GitHub Discussion](https://github.com/salim8898/vibemetric/discussions) for questions
- Create an issue for specific questions about the codebase

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/vibemetric.git
cd vibemetric

# Add upstream remote
git remote add upstream https://github.com/vibemetric/vibemetric.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
# Install in development mode with all dependencies
pip install -e ".[dev,ml]"

# Verify installation
pytest
```

### 4. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

## Making Changes

### Development Workflow

1. **Write Code** - Make your changes in the feature branch
2. **Add Tests** - Write tests for new functionality
3. **Run Tests** - Ensure all tests pass
4. **Update Docs** - Update documentation if needed
5. **Commit Changes** - Use clear, descriptive commit messages
6. **Push Branch** - Push to your fork
7. **Open PR** - Create pull request to main repository

### Commit Message Guidelines

Use conventional commit format:

```
type(scope): brief description

Detailed explanation of changes (optional)

Fixes #issue_number (if applicable)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Examples:**

```
feat(detector): Add support for Windsurf AI tool

Added Windsurf configuration file detection to artifact detector.
Includes tests and documentation updates.

Fixes #123
```

```
fix(velocity): Handle repositories with <40 commits

Velocity analyzer now returns graceful error message for repos
with insufficient commit history instead of crashing.

Fixes #456
```

## Testing

### Run All Tests

```bash
# Run full test suite
pytest

# Run with coverage
pytest --cov=vibemetric --cov-report=html

# Run specific test file
pytest tests/test_scorer.py

# Run specific test
pytest tests/test_scorer.py::TestScorer::test_null_score_with_empty_signals
```

### Write Tests

All new features must include tests:

```python
# tests/test_your_feature.py
import pytest
from vibemetric.your_module import YourClass

class TestYourFeature:
    """Test suite for your feature"""
    
    def test_basic_functionality(self):
        """Test basic functionality works"""
        obj = YourClass()
        result = obj.do_something()
        assert result == expected_value
    
    def test_edge_case(self):
        """Test edge case handling"""
        obj = YourClass()
        with pytest.raises(ValueError):
            obj.do_something_invalid()
```

### Test Coverage

- Aim for 80%+ coverage on new code
- All public APIs must have tests
- Edge cases should be tested
- Error handling should be tested

## Submitting Changes

### Before Submitting

1. **Run Tests**: `pytest`
2. **Check Coverage**: `pytest --cov=vibemetric`
3. **Format Code**: `black src/ tests/`
4. **Lint Code**: `ruff check src/ tests/`
5. **Type Check**: `mypy src/`
6. **Update Docs**: Update README or USAGE_GUIDE if needed

### Create Pull Request

1. Push your branch to your fork
2. Go to [Vibemetric repository](https://github.com/salim8898/vibemetric)
3. Click "New Pull Request"
4. Select your fork and branch
5. Fill out PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Updated documentation

## Related Issues
Fixes #issue_number

## Screenshots (if applicable)
```

### PR Review Process

1. Maintainer reviews your PR
2. Address any feedback or requested changes
3. Once approved, maintainer will merge
4. Your contribution will be in the next release!

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Use type hints for all functions

### Code Organization

```python
"""
Module docstring explaining purpose.

Detailed description if needed.
"""

from typing import List, Optional
import external_library

from vibemetric.models import Model


class MyClass:
    """
    Class docstring.
    
    Attributes:
        attr1: Description of attr1
        attr2: Description of attr2
    """
    
    def __init__(self, param: str):
        """
        Initialize MyClass.
        
        Args:
            param: Description of parameter
        """
        self.attr1 = param
    
    def public_method(self, arg: int) -> str:
        """
        Public method docstring.
        
        Args:
            arg: Description of argument
            
        Returns:
            Description of return value
            
        Raises:
            ValueError: When arg is invalid
        """
        if arg < 0:
            raise ValueError("arg must be positive")
        return str(arg)
    
    def _private_method(self) -> None:
        """Private method docstring."""
        pass
```

### Documentation

- All public APIs must have docstrings
- Use Google-style docstrings
- Include examples for complex functions
- Update README.md for user-facing changes
- Update USAGE_GUIDE.md for new features

### Testing Standards

- One test file per module: `test_module.py`
- Group related tests in classes
- Use descriptive test names
- Include docstrings for test classes
- Test both success and failure cases

## Project Structure

```
vibemetric/
├── src/vibemetric/          # Source code
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── models.py           # Data models
│   ├── scorer.py           # Score combination
│   ├── detectors/          # Detection layers
│   │   ├── artifact_detector.py
│   │   ├── velocity_analyzer.py
│   │   ├── pattern_detector.py
│   │   └── ml_detector.py
│   └── ml/                 # ML components
│       └── feature_extractor.py
├── tests/                  # Test suite
│   ├── test_scorer.py
│   ├── test_artifact_detector.py
│   └── ...
├── models/                 # Trained ML models
├── docs/                   # Documentation
├── README.md              # Project overview
├── USAGE_GUIDE.md         # Usage instructions
├── CONTRIBUTING.md        # This file
└── pyproject.toml         # Project configuration
```

### Key Modules

**Detectors** (`src/vibemetric/detectors/`):
- `artifact_detector.py` - AI tool config detection
- `velocity_analyzer.py` - Coding velocity analysis
- `pattern_detector.py` - AI pattern recognition
- `ml_detector.py` - ML-based detection

**Core** (`src/vibemetric/`):
- `models.py` - Data models and enums
- `scorer.py` - Score combination engine
- `cli.py` - Command-line interface

**ML** (`src/vibemetric/ml/`):
- `feature_extractor.py` - Feature extraction for ML

## Areas for Contribution

### High Priority

- [ ] Additional AI tool detection (Tabnine, Codeium, etc.)
- [ ] PR-based velocity analysis
- [ ] GitHub/GitLab API integration
- [ ] Additional CLI commands
- [ ] Performance optimizations

### Medium Priority

- [ ] Support for more programming languages
- [ ] Custom detection rules
- [ ] Configuration file support
- [ ] Export formats (CSV, PDF)
- [ ] Visualization improvements

### Documentation

- [ ] API reference documentation
- [ ] Architecture diagrams
- [ ] Video tutorials
- [ ] Blog posts and examples
- [ ] Translation to other languages

### Testing

- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] Test on more repositories
- [ ] Improve test coverage
- [ ] Add property-based tests

## Getting Help

### Resources

- 📖 [README](README.md) - Project overview
- 📚 [Usage Guide](USAGE_GUIDE.md) - Detailed usage
- 🐛 [Issues](https://github.com/salim8898/vibemetric/issues) - Bug reports
- 💬 [Discussions](https://github.com/salim8898/vibemetric/discussions) - Questions

### Maintainers

- Primary maintainer: @salim8898
- Response time: Usually within 48-72 hours
- Best way to reach: GitHub issues or discussions

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation
- Invited to contributor meetings (coming soon)

## License

By contributing to Vibemetric, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Vibemetric! Your efforts help make AI code detection accessible to everyone. 🎉
