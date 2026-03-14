# DevMetric MVP - Technical Specification

## Project Overview

**Name:** vibe-scanner (open source CLI) → DevMetric (future SaaS)

**Mission:** Measure AI's impact on developer productivity by detecting AI-generated code, tracking metrics, and calculating ROI.

**Target Users:** 
- Developers (free CLI)
- Engineering Managers (future paid dashboard)
- CTOs/CFOs (future ROI reports)

---

## MVP Scope (Weeks 1-2)

### Core Features

1. **Vibe Score Calculator**
   - Analyzes a Git repository
   - Detects AI-generated code patterns
   - Outputs percentage of AI-generated lines
   - Provides risk assessment

2. **Detection Methods**
   - Statistical analysis (code perplexity)
   - Commit velocity analysis
   - Code style consistency checks
   - Pattern matching for common AI signatures

3. **CLI Interface**
   - Simple commands
   - JSON and human-readable output
   - Configurable thresholds

---

## Technical Architecture

### Technology Stack

**Language:** Python 3.10+
- Reason: Easy to install, great for data analysis, large community

**Key Dependencies:**
- `gitpython` - Git repository analysis
- `tree-sitter` - AST parsing for multiple languages
- `click` - CLI framework
- `rich` - Beautiful terminal output
- `pandas` - Data analysis
- `numpy` - Statistical calculations

**Supported Languages (MVP):**
- Python
- JavaScript/TypeScript
- Go
- Java

---

## Detection Algorithm

### Method 1: Commit Velocity Analysis

**Concept:** AI-generated code appears in large chunks with minimal typing time.

**Implementation:**
```
For each commit:
  - Calculate lines added per minute
  - If > 500 lines/minute → Flag as "High AI Probability"
  - If commit message contains AI tool mentions → Flag
  - Track time between commits
```

**Scoring:**
- 0-100 lines/min: Human (0 points)
- 100-500 lines/min: Assisted (50 points)
- 500+ lines/min: AI-generated (100 points)

### Method 2: Code Perplexity Scoring

**Concept:** AI-generated code has lower perplexity (more predictable patterns).

**Implementation:**
```
For each file:
  - Parse AST
  - Calculate token frequency distribution
  - Compare against "typical" human patterns
  - Low variance = High AI probability
```

**Indicators:**
- Uniform indentation (no style drift)
- Consistent naming conventions throughout
- No typos or corrections in comments
- Perfect syntax on first commit

### Method 3: Stylometric Analysis

**Concept:** Every developer has a unique coding "fingerprint."

**Implementation:**
```
Build developer profile:
  - Historical commit patterns
  - Naming conventions (camelCase vs snake_case)
  - Comment style and frequency
  - Function length preferences

Compare new code:
  - If style drastically different → AI probability increases
```

### Method 4: AI Signature Detection

**Concept:** AI tools leave specific patterns.

**Common Signatures:**
- Overly verbose comments explaining obvious code
- Unused imports or variables
- Defensive programming patterns (excessive error handling)
- Generic variable names (data, result, response, output)
- Perfect formatting with no human "quirks"

---

## Vibe Score Calculation

### Formula

```
Vibe Score = (
  commit_velocity_score * 0.30 +
  perplexity_score * 0.25 +
  style_deviation_score * 0.25 +
  signature_detection_score * 0.20
)
```

### Score Interpretation

- **0-20%:** Human-led with minimal AI assistance
- **20-40%:** AI-assisted (copilot style)
- **40-60%:** Collaborative (significant AI contribution)
- **60-80%:** AI-dominant (vibe coding)
- **80-100%:** Fully generated (high risk)

---

## CLI Interface Design

### Commands

```bash
# Basic scan
vibe-scanner scan ./path/to/repo

# Scan with detailed output
vibe-scanner scan ./repo --detailed

# Scan specific time range
vibe-scanner scan ./repo --since="2024-01-01" --until="2024-12-31"

# Output as JSON
vibe-scanner scan ./repo --format=json

# Scan and save report
vibe-scanner scan ./repo --output=report.json

# Analyze specific author
vibe-scanner scan ./repo --author="john@example.com"

# Show version
vibe-scanner --version
```

### Output Format

**Human-Readable:**
```
🔍 Vibe Scanner v0.1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Repository: my-awesome-app
Commits analyzed: 247
Date range: 2024-01-01 to 2024-12-31

📊 Vibe Score: 42%
   Classification: Collaborative (AI-assisted)

📈 Breakdown:
   ├─ Human-written:     58% (12,450 lines)
   ├─ AI-assisted:       28% (6,020 lines)
   └─ AI-generated:      14% (3,010 lines)

⚠️  Risk Assessment:
   ├─ High-risk files: 3
   │  └─ src/auth/login.py (87% AI)
   ├─ Medium-risk files: 12
   └─ Low-risk files: 45

💡 Insights:
   • Peak AI usage: March 2024 (68% of commits)
   • Most AI-assisted author: john@example.com
   • Fastest commit: 1,247 lines in 3 minutes

🔗 Top AI-Generated Files:
   1. src/auth/login.py (87%)
   2. src/api/handlers.py (76%)
   3. tests/test_integration.py (71%)
```

**JSON Output:**
```json
{
  "version": "0.1.0",
  "repository": "my-awesome-app",
  "scan_date": "2024-12-31T10:30:00Z",
  "commits_analyzed": 247,
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "vibe_score": 42,
  "classification": "collaborative",
  "breakdown": {
    "human_written": {
      "percentage": 58,
      "lines": 12450
    },
    "ai_assisted": {
      "percentage": 28,
      "lines": 6020
    },
    "ai_generated": {
      "percentage": 14,
      "lines": 3010
    }
  },
  "risk_assessment": {
    "high_risk_files": 3,
    "medium_risk_files": 12,
    "low_risk_files": 45
  },
  "top_ai_files": [
    {
      "path": "src/auth/login.py",
      "vibe_score": 87,
      "lines": 234,
      "risk": "high"
    }
  ],
  "insights": {
    "peak_ai_month": "2024-03",
    "most_ai_assisted_author": "john@example.com",
    "fastest_commit": {
      "hash": "abc123",
      "lines": 1247,
      "duration_minutes": 3
    }
  }
}
```

---

## Project Structure

```
vibe-scanner/
├── README.md
├── LICENSE (MIT)
├── setup.py
├── requirements.txt
├── .gitignore
├── pyproject.toml
│
├── vibe_scanner/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py                 # CLI interface
│   ├── scanner.py             # Main scanning logic
│   ├── detectors/
│   │   ├── __init__.py
│   │   ├── velocity.py        # Commit velocity analysis
│   │   ├── perplexity.py      # Code perplexity scoring
│   │   ├── stylometry.py      # Style analysis
│   │   └── signatures.py      # AI signature detection
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── git_analyzer.py    # Git history analysis
│   │   └── code_analyzer.py   # AST parsing
│   ├── models/
│   │   ├── __init__.py
│   │   ├── scan_result.py     # Data models
│   │   └── file_result.py
│   └── utils/
│       ├── __init__.py
│       ├── output.py          # Formatting
│       └── config.py          # Configuration
│
├── tests/
│   ├── __init__.py
│   ├── test_scanner.py
│   ├── test_detectors.py
│   └── fixtures/
│       └── sample_repo/
│
└── docs/
    ├── ALGORITHM.md           # Detection algorithm details
    ├── CONTRIBUTING.md
    └── EXAMPLES.md
```

---

## Data Models

### ScanResult

```python
@dataclass
class ScanResult:
    repository_path: str
    scan_date: datetime
    commits_analyzed: int
    date_range: DateRange
    vibe_score: float
    classification: str
    breakdown: CodeBreakdown
    risk_assessment: RiskAssessment
    top_ai_files: List[FileResult]
    insights: Insights
```

### FileResult

```python
@dataclass
class FileResult:
    path: str
    vibe_score: float
    lines: int
    risk_level: str  # high, medium, low
    detection_methods: Dict[str, float]
    commits: List[str]
```

---

## Configuration

### .vibe-scanner.yml (Optional)

```yaml
# Detection thresholds
thresholds:
  velocity:
    human_max: 100        # lines/minute
    assisted_max: 500
  
  perplexity:
    ai_threshold: 0.3
  
  style_deviation:
    threshold: 0.6

# Risk levels
risk:
  high: 70              # vibe score > 70%
  medium: 40            # vibe score 40-70%
  low: 40               # vibe score < 40%

# Exclusions
exclude:
  - "node_modules/**"
  - "vendor/**"
  - "*.min.js"
  - "dist/**"
  - "build/**"

# Languages to analyze
languages:
  - python
  - javascript
  - typescript
  - go
  - java
```

---

## Installation & Distribution

### PyPI Package

```bash
pip install vibe-scanner
```

### From Source

```bash
git clone https://github.com/yourusername/vibe-scanner.git
cd vibe-scanner
pip install -e .
```

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install .
ENTRYPOINT ["vibe-scanner"]
```

---

## Testing Strategy

### Unit Tests
- Test each detector independently
- Mock Git repositories
- Test edge cases (empty repos, single commit, etc.)

### Integration Tests
- Test on real open-source repos
- Validate against known AI-generated projects
- Compare results with manual analysis

### Test Repos
- 100% human-written (pre-2020 projects)
- 100% AI-generated (create test cases)
- Mixed (real-world scenarios)

---

## Launch Strategy

### Week 3: Pre-Launch

1. **Create compelling README**
   - Show example output
   - Include "Try it now" section
   - Add badges (build status, version, license)

2. **Prepare launch post**
   - Title: "I analyzed 10,000 repos to measure 'vibe coding' - here's what I found"
   - Include real data and insights
   - Share methodology

3. **Set up analytics**
   - GitHub stars tracking
   - PyPI download stats
   - Email collection for interested companies

### Week 3: Launch Day

**Hacker News:**
- Post between 8-10 AM EST (best visibility)
- Engage with comments immediately
- Be transparent about limitations

**Reddit:**
- r/programming
- r/Python
- r/devops
- r/MachineLearning

**Twitter/X:**
- Tag: @github, @OpenAI, @AnthropicAI
- Use hashtags: #AI #DevTools #OpenSource

### Week 4: Validation Metrics

**Success Signals:**
- ✅ 500+ GitHub stars
- ✅ 1,000+ PyPI downloads
- ✅ 5+ companies email about enterprise version
- ✅ 10+ community contributions (issues/PRs)
- ✅ Mentioned in tech newsletters/blogs

**Pivot Signals:**
- ❌ <100 stars after 2 weeks
- ❌ No enterprise inquiries
- ❌ Negative feedback on accuracy
- ❌ No community engagement

---

## Future Roadmap (Post-Validation)

### Phase 2: GitHub Action (Week 5-6)
- Runs on every PR
- Comments with Vibe Score
- Blocks merge if score > threshold

### Phase 3: Web Dashboard (Week 7-10)
- Multi-repo view
- Historical trends
- Team analytics

### Phase 4: SaaS Platform (Week 11+)
- Token-to-Value ROI calculator
- Jira/Linear integration
- Slack alerts
- SSO/SAML
- API access

---

## Success Criteria

### MVP Success (End of Week 2)
- [ ] CLI tool works on 5+ test repos
- [ ] Accuracy > 70% on known AI-generated code
- [ ] Installation takes < 2 minutes
- [ ] Output is clear and actionable
- [ ] Documentation is complete

### Launch Success (End of Week 4)
- [ ] 500+ GitHub stars
- [ ] 5+ enterprise inquiries
- [ ] Featured on Hacker News front page
- [ ] 10+ community contributions
- [ ] Clear demand for paid features

---

## Risk Mitigation

### Technical Risks

**Risk:** Detection accuracy too low
**Mitigation:** Start with conservative estimates, clearly communicate confidence levels

**Risk:** Performance issues on large repos
**Mitigation:** Implement sampling, add progress bars, optimize algorithms

**Risk:** False positives
**Mitigation:** Use multiple detection methods, allow manual overrides

### Business Risks

**Risk:** No demand for paid version
**Mitigation:** Validate with free version first, pivot based on feedback

**Risk:** Competitors copy the idea
**Mitigation:** Move fast, build community, establish brand

**Risk:** AI tools evolve to evade detection
**Mitigation:** Keep algorithms updated, crowdsource detection patterns

---

## Budget (MVP Phase)

**Total: ~$50**

- Domain (hold off): $0
- Hosting (GitHub): $0
- Development tools: $0
- PyPI publishing: $0
- Marketing: $0
- Time investment: 40-60 hours

**Post-Validation Budget:**
- Domain: $160
- Hosting (Vercel/Railway): $20/month
- Database (Supabase): $25/month
- Email (Postmark): $15/month
- Analytics (PostHog): $0 (free tier)

---

## Next Steps

1. **Set up project structure** (Day 1)
2. **Implement commit velocity detector** (Day 2-3)
3. **Add basic CLI interface** (Day 4)
4. **Test on sample repos** (Day 5-6)
5. **Add remaining detectors** (Day 7-10)
6. **Polish output and docs** (Day 11-12)
7. **Create launch materials** (Day 13-14)
8. **Launch!** (Day 15)

---

## Questions to Answer During Development

- [ ] What's the minimum accuracy threshold for launch?
- [ ] Should we support private repos in MVP?
- [ ] How do we handle monorepos?
- [ ] What's the performance target (max scan time)?
- [ ] Should we collect anonymous usage data?

---

## Contact & Support

**GitHub:** github.com/yourusername/vibe-scanner
**Email:** [your-email]
**Twitter:** @yourusername

---

*Last Updated: March 13, 2026*
