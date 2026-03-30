# Vibemetric Scoring Guide

Complete guide to understanding Vibemetric's AI detection scoring system.

---

## Table of Contents

1. [Overview](#overview)
2. [4-Layer Detection System](#4-layer-detection-system)
3. [Score Calculation](#score-calculation)
4. [AI Assistance Levels](#ai-assistance-levels)
5. [Confidence Calculation](#confidence-calculation)
6. [Commit Message Scoring](#commit-message-scoring)
7. [Team Metrics](#team-metrics)
8. [Examples](#examples)

---

## Overview

Vibemetric uses a **4-layer detection system** to calculate an overall AI likelihood score (0-100) for code, commits, and repositories.

**Final Score Formula**:
```
Overall Score = (Artifact × 40%) + (Velocity × 25%) + (Pattern × 20%) + (ML × 15%)
```

**AI Assistance Levels**:
- **MINIMAL** (0-40): Low AI usage
- **PARTIAL** (40-70): Mixed human-AI collaboration
- **SUBSTANTIAL** (70-100): Heavy AI assistance

---

## 4-Layer Detection System

### Layer 1: Artifact Detection (40% weight, 90% accuracy)

**What it detects**: AI tool configuration files

**Scoring**:
- 1 tool detected = **50/100**
- 2 tools detected = **70/100**
- 3+ tools detected = **90/100**

**Detected tools**:
- Cursor (`.cursorrules`)
- Claude (`.claude/`, `claude.md`, `.anthropic/`)
- Kiro (`.kiro/`)
- GitHub Copilot (`.copilot/`, `.github/copilot/`)
- Aider (`.aider/`)
- Windsurf (`.windsurf/`)
- Tabnine (`.tabnine/`)
- Codeium (`.codeium/`)
- Amazon CodeWhisperer (`.aws/codewhisperer/`)
- Replit Ghostwriter (`.replit`)
- Sourcegraph Cody (`.cody/`)
- JetBrains AI (`.idea/ai/`)

**Confidence**: 0.90 (high - file existence is definitive)

**Example**:
```
Repository has .cursorrules and .kiro/
→ 2 tools detected
→ Artifact Score: 70/100
```

---

### Layer 2: Velocity Analysis (25% weight, 80% accuracy)

**What it detects**: Sudden increases in coding speed (lines/day)

**Scoring**:
- 1.8x velocity increase = **60/100** (confidence: 0.78)
- 2.7x velocity increase = **80/100** (confidence: 0.82)
- 3.5x+ velocity increase = **90/100** (confidence: 0.85)
- No spike = **0/100**

**Calculation**:
1. Split commit history into two halves
2. Calculate baseline velocity (first half)
3. Calculate current velocity (second half)
4. Compare: `current / baseline`

**Example**:
```
Baseline: 100 lines/day
Current: 270 lines/day
Increase: 2.7x
→ Velocity Score: 80/100
```

**Known Limitations**:
- Squash merge workflows may produce inaccurate results
- Requires 40+ commits for reliable analysis

---

### Layer 3: Pattern Detection (20% weight, 70% accuracy)

**What it detects**: AI-style code and commit patterns

#### Code Patterns

**Detected patterns**:
1. AI-style comments (verbose, generic)
2. Comprehensive docstrings (Args, Returns, Examples)
3. Extensive type hints
4. Heavy dataclass usage
5. Hallucination patterns (non-existent APIs)
6. AI-specific code patterns

**Scoring**: 0-100 based on pattern density

**Example**:
```python
def calculate_total(items: List[Item]) -> float:
    """
    Calculate the total price of items.
    
    Args:
        items: List of items to calculate
        
    Returns:
        Total price as float
        
    Example:
        >>> calculate_total([Item(price=10), Item(price=20)])
        30.0
    """
    return sum(item.price for item in items)
```
→ High pattern score (comprehensive docstring, type hints)

#### Commit Message Patterns

**List-style commits** (70-80 score - STRONG AI indicator):
```
Implement user authentication

- Add JWT token generation
- Implement login endpoint
- Add logout functionality
- Update user model
```

**Conventional commits** (60 score):
```
feat: add user authentication system
```

**Human-style commits** (0-20 score):
```
fixed auth bug
```

---

### Layer 4: ML Detection (15% weight, 85% accuracy)

**What it detects**: Statistical patterns using trained Random Forest model

**Model**: Trained on DROID dataset (846k samples)

**Features analyzed**:
- Whitespace consistency
- Token entropy
- Style uniformity
- Linguistic patterns

**Scoring**: 0-100 (ML probability)

**Confidence**: 0.85 when model available, 0.0 when unavailable

---

## Score Calculation

### Weighted Average Formula

```
Overall Score = (A × 0.40) + (V × 0.25) + (P × 0.20) + (M × 0.15)

Where:
A = Artifact Detection Score (0-100)
V = Velocity Analysis Score (0-100)
P = Pattern Detection Score (0-100)
M = ML Detection Score (0-100)
```

### Example Calculation

**Repository scan results**:
- Artifact: 50/100 (1 tool detected)
- Velocity: 80/100 (2.7x increase)
- Pattern: 65/100 (moderate AI patterns)
- ML: 70/100 (AI probability)

**Calculation**:
```
Overall = (50 × 0.40) + (80 × 0.25) + (65 × 0.20) + (70 × 0.15)
        = 20 + 20 + 13 + 10.5
        = 63.5/100
```

**Result**: PARTIAL AI assistance (63.5/100)

---

## AI Assistance Levels

### MINIMAL (0-40)

**Interpretation**: Low AI usage, primarily human-written

**Characteristics**:
- Few or no AI tool configs
- No velocity spikes
- Minimal AI patterns in code/commits
- Low ML probability

**Example**:
```
Artifact: 0/100 (no tools)
Velocity: 0/100 (no spike)
Pattern: 20/100 (few patterns)
ML: 15/100 (human-like)
→ Overall: 7/100 (MINIMAL)
```

### PARTIAL (40-70)

**Interpretation**: Mixed human-AI collaboration

**Characteristics**:
- Some AI tool usage
- Moderate velocity increase
- Mixed AI/human patterns
- Moderate ML probability

**Example**:
```
Artifact: 50/100 (1 tool)
Velocity: 60/100 (1.8x increase)
Pattern: 50/100 (moderate patterns)
ML: 55/100 (mixed)
→ Overall: 53.5/100 (PARTIAL)
```

### SUBSTANTIAL (70-100)

**Interpretation**: Heavy AI assistance

**Characteristics**:
- Multiple AI tools
- Significant velocity spike
- Strong AI patterns
- High ML probability

**Example**:
```
Artifact: 90/100 (3+ tools)
Velocity: 90/100 (3.5x+ increase)
Pattern: 80/100 (strong patterns)
ML: 85/100 (AI-like)
→ Overall: 87.5/100 (SUBSTANTIAL)
```

---

## Confidence Calculation

**Base confidence** from number of detection layers:
- 4 layers: 0.75
- 3 layers: 0.70
- 2 layers: 0.65
- 1 layer: 0.60

**Variance penalty**: Lower variance = higher confidence
```
variance = sum((score - mean)² for each score) / count
penalty = min(variance / 2000, 0.10)
final_confidence = base_confidence - penalty
```

**Multi-layer boost**: When multiple layers agree (scores within 20 points), confidence increases by 0.05

**Example**:
```
Scores: [50, 60, 55, 58]
Mean: 55.75
Variance: 16.19
Penalty: 0.008
Base: 0.75 (4 layers)
Final: 0.75 - 0.008 = 0.742
```

---

## Commit Message Scoring

### Individual Commit Analysis

**Threshold**: Score > 40 = AI-assisted

**Scoring breakdown**:

1. **Conventional commit format** (+60):
   ```
   feat: add new feature
   fix: resolve bug
   ```

2. **List-style commits** (+70-80):
   ```
   Update authentication
   
   - Add JWT support
   - Implement refresh tokens
   - Update tests
   ```

3. **Verbose descriptions** (+40):
   - Message length > 200 characters

4. **Structured bullet points** (+50-70):
   - 3+ bullet points = +70
   - 1-2 bullet points = +50

### Developer Profile Metrics

**AI-Assisted Commit Percentage**:
```
AI-Assisted % = (commits with score > 40) / total commits × 100
```

**Average AI Score**:
```
Average = sum(all commit scores) / total commits
```

**Example**:
```
Developer: 10 commits
- 6 commits with score > 40 (AI-assisted)
- 4 commits with score < 40 (human-style)
- Scores: [70, 65, 80, 20, 15, 75, 10, 60, 25, 55]

AI-Assisted %: 6/10 = 60%
Average Score: 475/10 = 47.5/100
```

---

## Team Metrics

### AI Adoption Rate

**Formula**:
```
AI Adoption Rate = (AI Tool Users + Shadow AI Users) / Total Developers × 100
```

**Definitions**:
- **AI Tool Users**: Developers who committed AI config files
- **Shadow AI Users**: Developers with >50% AI-assisted commits but no config files
- **Human-Only**: Developers with ≤50% AI-assisted commits and no config files

**Example**:
```
Total: 66 developers
AI Tool Users: 1 (committed .cursorrules)
Shadow AI Users: 42 (>50% AI commits, no config)
Human-Only: 23 (≤50% AI commits)

AI Adoption Rate: (1 + 42) / 66 = 65.2%
```

### Team Average AI Score

**Formula**:
```
Team Average = sum(all developer average scores) / total developers
```

**Interpretation**:
- 0-40: Team has minimal AI usage
- 40-70: Team has partial AI usage
- 70-100: Team has substantial AI usage

**Example**:
```
66 developers
Sum of all average scores: 2,145
Team Average: 2,145 / 66 = 32.5/100 (MINIMAL)
```

### Velocity Improvement

**Formula**:
```
Improvement % = (velocity_after / velocity_before - 1) × 100
```

**Team Average**:
```
Team Avg = sum(all improvements) / developers_with_velocity_data
```

**Example**:
```
Developer A: 100 → 180 lines/day (+80%)
Developer B: 150 → 150 lines/day (0%)
Developer C: 120 → 200 lines/day (+66.7%)

Team Average: (80 + 0 + 66.7) / 3 = +48.9%
```

---

## Examples

### Example 1: Open Source Project (Flask)

**Scan Results**:
```
Artifact: 0/100 (no AI tools)
Velocity: 0/100 (velocity decreased)
Pattern: 17.3/100 (minimal patterns)
ML: 0/100 (model unavailable)

Overall: 5.2/100
AI Assistance Level: MINIMAL
Confidence: 0.65
```

**Interpretation**: Flask is primarily human-written with minimal AI assistance.

---

### Example 2: AI-Assisted Project (awesome-cursorrules)

**Scan Results**:
```
Artifact: 50/100 (1 tool: Cursor)
Velocity: 90/100 (15x velocity spike!)
Pattern: 0/100 (no code files analyzed)
ML: 0/100 (no code files analyzed)

Overall: 64.8/100
AI Assistance Level: PARTIAL
Confidence: 0.92
```

**Team Report**:
```
Total Developers: 66
AI Tool Users: 1 (1.5%)
Shadow AI Users: 42 (63.6%)
AI Adoption Rate: 65.2%
Average AI Score: 32.5/100
AI-Assisted Commits: 62.6%
```

**Interpretation**: Repository shows PARTIAL AI assistance with high shadow AI usage (developers using AI without committing configs).

---

### Example 3: Individual Developer

**Developer Profile**:
```
Total Commits: 27
AI-Assisted Commits: 16 (59.3%)
Average AI Score: 26.7/100
AI Tools: Cursor
Adoption Date: 2024-09-17
Days Using AI: 548
Velocity Before: 2.0 lines/day
Velocity After: 2.0 lines/day
Improvement: 0%
```

**Interpretation**: Developer uses Cursor but velocity unchanged. Moderate AI usage (59.3% of commits show AI patterns).

---

## Summary

**Key Takeaways**:

1. **4-layer system** provides comprehensive detection
2. **Weighted scoring** prioritizes most reliable signals (Artifact 40%)
3. **Confidence scores** indicate reliability of detection
4. **Multiple thresholds** classify AI assistance levels
5. **Team metrics** aggregate individual developer data
6. **Shadow AI detection** identifies untracked AI usage

**Scoring is transparent**: All calculations are documented and reproducible.

---

**Last Updated**: March 20, 2026  
**Version**: 1.0.0
