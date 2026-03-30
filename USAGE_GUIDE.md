# Vibemetric Usage Guide

Complete guide to using Vibemetric for AI code detection and team analytics.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [CLI Commands](#cli-commands)
4. [Understanding Results](#understanding-results)
5. [Python Library API](#python-library-api)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.9 or higher
- Git installed and accessible from command line
- pip package manager

### Install Vibemetric

```bash
# Clone repository
git clone https://github.com/vibemetric/vibemetric.git
cd vibemetric

# Install with ML support (recommended)
pip install -e ".[ml]"

# Verify installation
vibemetric --help
```

### Optional: Add to PATH

If `vibemetric` command is not found, add Python bin directory to PATH:

```bash
# Find Python bin directory
python -c "import sys; print(sys.prefix + '/bin')"

# Add to ~/.zshrc or ~/.bashrc
export PATH="/path/to/python/bin:$PATH"

# Reload shell
source ~/.zshrc  # or source ~/.bashrc
```

## Basic Usage

### Scan Current Directory

```bash
vibemetric scan .
```

### Scan Specific Repository

```bash
vibemetric scan /path/to/repository
```

### Scan with JSON Output

```bash
vibemetric scan . --format json
```

### Analyze More Files

```bash
# Analyze 20 files instead of default 10
vibemetric scan . --sample-size 20

# Analyze 50 files for comprehensive scan
vibemetric scan . --sample-size 50
```

### Verbose Output

```bash
vibemetric scan . --verbose
```

## CLI Commands

### `vibemetric scan`

Scan repository for AI-generated code.

**Syntax:**
```bash
vibemetric scan PATH [OPTIONS]
```

**Arguments:**
- `PATH` - Path to repository (required)

**Options:**
- `--format [terminal|json]` - Output format (default: terminal)
- `--sample-size INTEGER` - Number of files to analyze (default: 10)
- `--verbose` - Show detailed progress

**Examples:**

```bash
# Basic scan
vibemetric scan .

# JSON output for CI/CD
vibemetric scan . --format json > results.json

# Comprehensive scan
vibemetric scan . --sample-size 100 --verbose

# Scan remote repository (clone first)
git clone https://github.com/user/repo.git
vibemetric scan ./repo
```

## Understanding Results

### Detection Summary Table

```
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Layer              ┃ Score    ┃ Status            ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ Artifact Detection │ 50.0/100 │ ✓ 1 tools         │
│ Velocity Detection │ 80.0/100 │ ✓ Spike           │
│ Pattern Detection  │ 70.0/100 │ ✓ 5 high-AI files │
│ ML Detection       │ 65.0/100 │ ✓ 8 AI files      │
└────────────────────┴──────────┴───────────────────┘
```

**Layer Scores:**
- **0-40**: Low confidence in AI usage
- **40-70**: Moderate AI indicators
- **70-100**: Strong AI indicators

**Status Indicators:**
- `✓ X tools` - Number of AI tools detected
- `✓ Spike` - Velocity spike detected
- `✗ No spike` - No velocity change
- `✓ X high-AI files` - Files with >60 AI score
- `✗ None` - No detection

### AI Assistance Levels

**MINIMAL (0-40)**
- Primarily human-authored code
- Little to no AI tool usage detected
- Traditional development patterns
- **Action**: Continue monitoring

**PARTIAL (40-70)**
- Mixed human-AI collaboration
- Some AI assistance detected
- Selective AI tool usage
- **Action**: Establish AI usage guidelines

**SUBSTANTIAL (70-100)**
- Significant AI contribution
- Multiple AI indicators detected
- Heavy AI tool usage
- **Action**: Review AI policies and code quality

### Confidence Score

Confidence indicates how reliable the detection is:

- **0.0-0.5**: Low confidence (conflicting signals)
- **0.5-0.7**: Moderate confidence
- **0.7-0.85**: High confidence (multiple layers agree)
- **0.85-1.0**: Very high confidence (all layers agree)

### Recommendations

Vibemetric provides actionable recommendations based on detection results:

**For SUBSTANTIAL AI Assistance:**
- Review AI tool usage policies with team
- Ensure AI-generated code is properly reviewed
- Consider code quality audits
- Document approved AI tools
- Monitor velocity changes for quality impact

**For PARTIAL AI Assistance:**
- Establish clear AI usage guidelines
- Track AI adoption across team members
- Review code patterns for consistency

**For MINIMAL AI Assistance:**
- No immediate action needed
- Continue monitoring for AI adoption

## Python Library API

### Basic Usage

```python
from vibemetric.detectors import (
    ArtifactDetector,
    VelocityAnalyzer,
    PatternDetector,
    MLDetector
)
from vibemetric.scorer import Scorer

# Initialize detectors
repo_path = "/path/to/repo"

artifact_detector = ArtifactDetector(repo_path)
velocity_analyzer = VelocityAnalyzer(repo_path)
pattern_detector = PatternDetector()
ml_detector = MLDetector()

# Run artifact detection
artifacts = artifact_detector.detect()
artifact_signal = artifact_detector.get_detection_signal(artifacts)

print(f"Tools found: {len(artifacts)}")
for artifact in artifacts:
    print(f"  - {artifact.tool_name}: {artifact.file_path}")

# Run velocity analysis
velocity_metrics = velocity_analyzer.analyze()
velocity_signal = velocity_analyzer.get_detection_signal(velocity_metrics)

print(f"Velocity spike: {velocity_metrics['spike_detected']}")
print(f"Baseline: {velocity_metrics['baseline_velocity']:.1f} lines/day")
print(f"Current: {velocity_metrics['current_velocity']:.1f} lines/day")

# Run pattern detection on file
pattern_signal = pattern_detector.analyze_file("path/to/file.py")

print(f"Pattern score: {pattern_signal.score:.1f}/100")
print(f"Patterns detected: {pattern_signal.metadata.get('pattern_count', 0)}")

# Run ML detection
ml_signal = ml_detector.analyze_file("path/to/file.py")

print(f"ML score: {ml_signal.score:.1f}/100")
print(f"Prediction: {'AI' if ml_signal.score > 50 else 'Human'}")

# Combine all signals
scorer = Scorer()
vibe_score = scorer.calculate_vibe_score([
    artifact_signal,
    velocity_signal,
    pattern_signal,
    ml_signal
])

print(f"\nCombined Results:")
print(f"Overall Score: {vibe_score.overall_score:.1f}/100")
print(f"AI Assistance Level: {vibe_score.ai_assistance_level.value}")
print(f"Confidence: {vibe_score.confidence:.2f}")

# Get interpretation and recommendations
interpretation = scorer.get_interpretation(vibe_score)
recommendations = scorer.get_recommendations(vibe_score)

print(f"\nInterpretation: {interpretation}")
print("\nRecommendations:")
for rec in recommendations:
    print(f"  - {rec}")
```

### Analyze Commit Messages

```python
from vibemetric.detectors import PatternDetector

detector = PatternDetector()

commit_message = """
feat(api): Add user authentication endpoint

- Implement JWT token generation
- Add password hashing with bcrypt
- Create user login endpoint
- Add input validation
"""

signal = detector.analyze_commit_message(commit_message)

print(f"AI Score: {signal.score:.1f}/100")
print(f"Evidence: {signal.evidence}")
```

### Analyze PR Descriptions

```python
from vibemetric.detectors import PatternDetector

detector = PatternDetector()

pr_description = """
## Summary
This PR implements user authentication using JWT tokens.

## Changes
- Added authentication middleware
- Implemented token generation
- Created login/logout endpoints

## Testing
- Unit tests for auth service
- Integration tests for endpoints
- Manual testing completed

Related to #123
"""

signal = detector.analyze_pr_description(pr_description)

print(f"AI Score: {signal.score:.1f}/100")
print(f"Confidence: {signal.confidence:.2f}")
```

## Best Practices

### 1. Choose Appropriate Sample Size

- **Small repos (<50 files)**: Use default `--sample-size 10`
- **Medium repos (50-200 files)**: Use `--sample-size 20-30`
- **Large repos (>200 files)**: Use `--sample-size 50-100`

### 2. Interpret Results in Context

- Consider team size and development practices
- Account for code review processes
- Factor in project maturity and complexity

### 3. Use JSON Output for Automation

```bash
# Save results for tracking
vibemetric scan . --format json > scan-$(date +%Y%m%d).json

# Parse with jq
vibemetric scan . --format json | jq '.overall_score'
```

### 4. Regular Monitoring

```bash
# Weekly scans
0 0 * * 0 cd /path/to/repo && vibemetric scan . --format json > weekly-scan.json

# Track changes over time
vibemetric scan . --format json | jq '{date: now, score: .overall_score}' >> history.jsonl
```

### 5. Combine with Code Review

- Use Vibemetric as one signal, not the only signal
- Review high-scoring files manually
- Discuss AI usage policies with team

## Troubleshooting

### Command Not Found

**Problem**: `vibemetric: command not found`

**Solution**:
```bash
# Use Python module syntax
python -m vibemetric.cli scan .

# Or add Python bin to PATH
export PATH="$(python -c 'import sys; print(sys.prefix + "/bin")'):$PATH"
```

### ML Model Not Available

**Problem**: `ML model not available - skipping ML detection`

**Solution**:
```bash
# Ensure ML dependencies are installed
pip install -e ".[ml]"

# Check if model file exists
ls models/ai_detector.pkl
```

### Git Repository Not Found

**Problem**: `Not a git repository`

**Solution**:
```bash
# Initialize git if needed
git init

# Or scan a different directory
vibemetric scan /path/to/git/repo
```

### Velocity Analysis Shows 0

**Problem**: Velocity metrics all show 0.0

**Possible Causes**:
- Repository has <40 commits (minimum required)
- No velocity spike detected (this is normal for stable repos)
- Recent repository with limited history

**Solution**: This is expected behavior for new or stable repositories.

### High False Positive Rate

**Problem**: Clean human code flagged as AI-generated

**Possible Causes**:
- Very consistent coding style
- Comprehensive documentation
- Heavy use of type hints

**Solution**:
- Check artifact detection (most reliable)
- Review velocity analysis
- Consider team coding standards
- Use larger sample size for better accuracy

## Advanced Usage

### CI/CD Integration

```yaml
# .github/workflows/vibemetric.yml
name: AI Code Detection

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0  # Full history for velocity analysis
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install Vibemetric
        run: |
          pip install vibemetric[ml]
      
      - name: Scan Repository
        run: |
          vibemetric scan . --format json > results.json
      
      - name: Check Threshold
        run: |
          score=$(jq '.overall_score' results.json)
          if (( $(echo "$score > 80" | bc -l) )); then
            echo "High AI assistance detected: $score"
            exit 1
          fi
```

### Batch Processing

```python
import os
from pathlib import Path
from vibemetric.cli import scan_repository

repos = [
    "/path/to/repo1",
    "/path/to/repo2",
    "/path/to/repo3"
]

results = []
for repo_path in repos:
    print(f"Scanning {repo_path}...")
    result = scan_repository(repo_path, sample_size=20)
    results.append({
        "repo": os.path.basename(repo_path),
        "score": result["vibe_score"]["overall_score"],
        "level": result["vibe_score"]["ai_assistance_level"]
    })

# Generate report
for r in sorted(results, key=lambda x: x["score"], reverse=True):
    print(f"{r['repo']}: {r['score']:.1f}/100 ({r['level']})")
```

## Getting Help

- 📖 Read the [README](README.md)
- 🐛 Report issues on [GitHub](https://github.com/vibemetric/vibemetric/issues)
- 💬 Ask questions in [Discussions](https://github.com/vibemetric/vibemetric/discussions)
- 📧 Email: support@vibemetric.ai

---

Last updated: March 2026
