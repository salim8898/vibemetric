# vibe-scanner

AI-generated code detection tool and Python library.

## Overview

vibe-scanner is an open-source CLI tool and Python library that detects AI-generated code in repositories. The system analyzes code files using multiple detection methods including:

- **Pattern Detection**: Identifies common AI code generation patterns
- **Statistical Analysis**: Analyzes code perplexity and predictability
- **Style Analysis**: Detects deviations from developer coding style
- **Git Metadata Analysis**: Examines commit patterns and authoring speed

## Features

- 🔍 Multi-method detection for accurate results
- 📊 File-level and repository-level analysis
- 🎨 Multiple output formats (terminal, JSON, markdown)
- ⚡ Fast parallel processing
- 🔌 Extensible plugin architecture
- 🔒 Offline operation (no external API calls)
- 🐍 Python library API for programmatic use

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/vibe-scanner/vibe-scanner.git
cd vibe-scanner

# Install in development mode
pip install -e ".[dev]"
```

### From PyPI (coming soon)

```bash
pip install vibe-scanner
```

## Quick Start

### CLI Usage

```bash
# Scan a local repository
vibe-scanner scan ./my-project

# Scan with JSON output
vibe-scanner scan ./my-project --output json

# Scan with custom threshold
vibe-scanner scan ./my-project --threshold 70
```

### Python Library Usage

```python
from vibe_scanner import scan_repository

# Scan a repository
result = scan_repository("./my-project")

print(f"Overall Vibe Score: {result.overall_vibe_score.overall_score}%")
print(f"Risk Level: {result.overall_vibe_score.risk_level}")
```

## Development Status

🚧 **This project is currently under active development.**

The implementation is following a structured task-based approach. See `.kiro/specs/vibe-scanner/tasks.md` for the detailed implementation plan.

## Requirements

- Python 3.9 or higher
- Git (for git metadata analysis)

## Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/vibe_scanner

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vibe_scanner --cov-report=html

# Run specific test file
pytest tests/test_models.py
```

## Project Structure

```
vibe-scanner/
├── src/
│   └── vibe_scanner/
│       ├── __init__.py
│       ├── cli.py              # CLI interface
│       ├── models.py           # Data models
│       ├── scanner.py          # Repository scanner
│       ├── file_analyzer.py   # File analyzer
│       ├── scorer.py           # Score calculator
│       ├── reporter.py         # Report generator
│       ├── utils.py            # Utilities
│       └── detectors/          # Detection modules
│           ├── pattern_detector.py
│           ├── statistical_analyzer.py
│           ├── style_analyzer.py
│           └── git_analyzer.py
├── tests/                      # Test suite
├── pyproject.toml             # Project configuration
└── README.md
```

## Contributing

Contributions are welcome! This is an open-source project designed to help the developer community.

See `CONTRIBUTING.md` (coming soon) for guidelines.

## License

MIT License - See LICENSE file for details.

## Roadmap

- [x] Project structure and dependencies
- [ ] Core data models
- [ ] Detection algorithms
- [ ] CLI interface
- [ ] Comprehensive testing
- [ ] Documentation
- [ ] PyPI release

## Support

- 📖 Documentation: Coming soon
- 🐛 Issues: [GitHub Issues](https://github.com/vibe-scanner/vibe-scanner/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/vibe-scanner/vibe-scanner/discussions)

## Acknowledgments

Built with:
- [tree-sitter](https://tree-sitter.github.io/) - Multi-language parsing
- [GitPython](https://gitpython.readthedocs.io/) - Git repository analysis
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
