# Vibemetric Development Guidelines for Kiro

## Project Context

You're working on **Vibemetric**, an AI code detection platform that helps engineering teams measure AI tool adoption and productivity impact. The project has 152 passing tests with 85%+ coverage.

## Architecture

### 4-Layer Detection System
1. **Artifact Detector** (90% accuracy) - Detects AI tool config files
2. **Velocity Analyzer** (80% accuracy) - Detects coding speed changes
3. **Pattern Detector** (70% accuracy) - Detects AI code patterns
4. **ML Detector** (85% accuracy) - Statistical pattern detection

### Key Components
- `src/vibemetric/detectors/` - Detection layers
- `src/vibemetric/scorer.py` - Score combination engine
- `src/vibemetric/cli.py` - CLI interface
- `src/vibemetric/integrations/` - GitHub/GitLab/PR analysis
- `tests/` - 152 unit tests

## Development Rules

### Test-First Development
Always write tests before implementing features:

```python
# 1. Write test first
def test_new_feature():
    detector = NewDetector()
    result = detector.detect()
    assert result.score > 0

# 2. Then implement
class NewDetector:
    def detect(self) -> DetectionSignal:
        # Implementation
        pass
```

### Code Quality Standards
- Type hints on all functions
- Google-style docstrings
- Black formatting (100 chars)
- Ruff linting
- 80%+ test coverage

### Before Committing
Run these checks:
```bash
pytest                          # All tests pass
black src/ tests/               # Format
ruff check src/ tests/          # Lint
pytest --cov=vibemetric         # Coverage
```

## Common Tasks

### Adding New AI Tool Detection
1. Update `SUPPORTED_ARTIFACTS` in `artifact_detector.py`
2. Add test case with mock git repo
3. Update README.md supported tools list
4. Update SCORING_GUIDE.md

### Adding New Pattern
1. Add pattern method to `PatternDetector`
2. Add test with sample code
3. Document in SCORING_GUIDE.md
4. Update pattern weights if needed

### Adding CLI Command
1. Add command to `cli.py` using Click
2. Add integration test
3. Update USAGE_GUIDE.md
4. Add example to README.md

## Testing Patterns

### Mock Git Repository
```python
@pytest.fixture
def mock_repo(tmp_path):
    repo = git.Repo.init(tmp_path)
    # Add commits, files, etc.
    return repo
```

### Mock GitHub API
```python
@pytest.fixture
def mock_github():
    with patch('vibemetric.integrations.github_client.Github') as mock:
        yield mock
```

## Commit Message Format

Use conventional commits:
```
feat(detector): Add Windsurf AI tool support
fix(velocity): Handle repos with <40 commits
test(pattern): Add docstring detection tests
docs(guide): Update scoring explanation
refactor(scorer): Simplify weight calculation
```

## PR Workflow

1. Create feature branch: `git checkout -b feature/name`
2. Make changes with tests
3. Run full test suite
4. Push to fork
5. Open PR with template
6. Wait for CI checks
7. Address review feedback

## Important Notes

- **Never push to main** - All changes via PR
- **Tests are required** - No exceptions
- **Type hints are mandatory** - For all functions
- **Mock external calls** - Git, GitHub API, file system
- **Update docs** - README, USAGE_GUIDE, SCORING_GUIDE

## File Patterns to Know

### Source Files
- `src/vibemetric/**/*.py` - All source code
- `tests/**/*.py` - All unit tests
- `*.md` - Documentation

### Excluded Files
- `/test_*.py` - Root test scripts (not unit tests)
- `/debug_*.py` - Debug scripts
- `data/` - Training data
- `archive/` - Old code
- `PROGRESS_LOG.md` - Internal planning

## Dependencies

### Core
- gitpython - Git operations
- click - CLI framework
- rich - Terminal formatting
- pyyaml - Config parsing

### ML
- numpy - Numerical operations
- scikit-learn - ML models

### Dev
- pytest - Testing
- black - Formatting
- ruff - Linting
- mypy - Type checking

## Questions?

- Read CONTRIBUTING.md for full guidelines
- Check USAGE_GUIDE.md for feature details
- Review SCORING_GUIDE.md for scoring logic
- Look at existing tests for patterns
- Open GitHub issue if stuck
