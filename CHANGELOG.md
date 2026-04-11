# Changelog

All notable changes to Vibemetric will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-30

### Added
- Initial release of Vibemetric
- 4-layer AI code detection system:
  - Artifact Detector (90% accuracy) - Detects 12 AI tool config files
  - Velocity Analyzer (80% accuracy) - Detects 1.8x+ velocity spikes
  - Pattern Detector (70% accuracy) - AI code patterns and commit messages
  - ML Detector (85% accuracy) - Random Forest trained on DROID dataset
- CLI commands:
  - `vibemetric scan` - Scan repository for AI-generated code
  - `vibemetric developer-profile` - Individual developer AI usage tracking
  - `vibemetric team-report` - Team-wide AI analytics with shadow AI detection
  - `vibemetric scan-pr` - Pull request analysis (unique differentiator)
- Output formats:
  - Terminal (Rich formatting)
  - JSON
  - SARIF (for GitHub Code Scanning)
- Comprehensive documentation:
  - README with quick start guide
  - USAGE_GUIDE with detailed examples
  - SCORING_GUIDE with transparent scoring explanations
  - CONTRIBUTING guide for contributors
- 98 passing tests with 85%+ code coverage
- Support for Python 3.9, 3.10, 3.11, 3.12
- GitHub Actions CI/CD pipeline
- Branch protection with required PR reviews

### Supported AI Tools
- Cursor (.cursorrules)
- Claude (.claude/, claude.md, .anthropic/)
- Kiro (.kiro/)
- GitHub Copilot (.copilot/, .github/copilot/)
- Aider (.aider/)
- Windsurf (.windsurf/)
- Tabnine (.tabnine/)
- Codeium (.codeium/)
- Amazon CodeWhisperer (.aws/codewhisperer/)
- Replit Ghostwriter (.replit)
- Sourcegraph Cody (.cody/)
- JetBrains AI (.idea/ai/)

[0.1.0]: https://github.com/salim8898/vibemetric/releases/tag/v0.1.0
