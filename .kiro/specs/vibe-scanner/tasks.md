# Implementation Plan: vibe-scanner

## Overview

This plan implements the vibe-scanner MVP - an open-source CLI tool and Python library for detecting AI-generated code. The implementation follows a bottom-up approach: data models → core detection algorithms → orchestration → CLI interface → testing. The MVP focuses on local repository scanning with pattern, statistical, style, and git-based detection methods, producing terminal, JSON, and markdown reports.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python package structure with `src/vibe_scanner/` directory
  - Set up `pyproject.toml` with dependencies: tree-sitter, gitpython, click, rich, pyyaml
  - Configure development tools: pytest, hypothesis, black, mypy, ruff
  - Create basic `__init__.py` files for package structure
  - Set up `.gitignore` for Python projects
  - _Requirements: Design dependencies section_

- [x] 2. Implement core data models
  - [x] 2.1 Create data model classes
    - Implement `ScanConfig` with validation rules
    - Implement `VibeScore` with score bounds validation (0-100, confidence 0-1)
    - Implement `FileAnalysisResult` with file metrics
    - Implement `ScanResult` with aggregate metrics
    - Implement `DetectionSignal` with signal types enum
    - Add supporting models: `PatternMatch`, `StatisticalMetrics`, `StyleMetrics`, `GitMetrics`
    - _Requirements: Design data models section, Properties 1, 2, 3_
  
  - [ ]* 2.2 Write property test for data model validation
    - **Property 1: Score Bounds** - All vibe scores must be 0-100, confidence 0-1
    - **Property 2: File Count Consistency** - total_files_scanned equals length of file_results
    - **Property 3: Line Classification Completeness** - ai_generated_lines + human_written_lines = total_lines_analyzed
    - **Validates: Design Properties 1, 2, 3**

- [ ] 3. Implement file discovery and repository scanner foundation
  - [x] 3.1 Create file discovery module
    - Implement `discoverFiles()` function with include/exclude pattern matching
    - Add glob pattern support for file filtering
    - Implement file type detection by extension
    - Add file size validation and filtering
    - _Requirements: Design Component 2, Properties 6, 9, 15_
  
  - [ ]* 3.2 Write property tests for file discovery
    - **Property 6: File Path Uniqueness** - No duplicate file paths in results
    - **Property 9: File Discovery Completeness** - All matching files discovered
    - **Property 15: Pattern Filtering Correctness** - Files match include patterns, not exclude patterns
    - **Validates: Design Properties 6, 9, 15**

- [ ] 4. Implement Pattern Detector
  - [x] 4.1 Create pattern detection module
    - Implement `PatternDetector` class with `detect()` method
    - Add AI comment pattern detection (overly verbose, generic comments)
    - Implement complexity uniformity detection using AST analysis
    - Add hallucination pattern detection (non-existent APIs, unusual patterns)
    - Implement AI-specific code pattern matching (boilerplate, repetitive structures)
    - Calculate pattern scores and generate evidence
    - _Requirements: Design Component 4, Pattern Detection Algorithm_
  
  - [ ]* 4.2 Write unit tests for pattern detection
    - Test AI comment pattern detection with known examples
    - Test complexity uniformity with synthetic code samples
    - Test hallucination detection with fake API calls
    - Test edge cases: empty files, single-line files
    - _Requirements: Design Component 4_

- [ ] 5. Implement Statistical Analyzer
  - [x] 5.1 Create statistical analysis module
    - Implement `StatisticalAnalyzer` class with `analyze()` method
    - Add code tokenization for target languages
    - Implement perplexity calculation using token probabilities
    - Add predictability scoring based on code patterns
    - Implement token distribution analysis
    - Add statistical anomaly detection
    - Normalize all metrics to 0-100 range
    - _Requirements: Design Component 5, Statistical Analysis Algorithm, Property 21_
  
  - [ ]* 5.2 Write property test for statistical metrics
    - **Property 21: Statistical Metrics Normalization** - All metrics normalized to 0-100
    - **Validates: Design Property 21**

- [ ] 6. Checkpoint - Ensure core detection modules work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement Style Analyzer
  - [x] 7.1 Create style analysis module
    - Implement `StyleAnalyzer` class with `analyze()` method
    - Add style feature extraction: indentation, naming conventions, line length
    - Implement developer baseline building from git history
    - Add style deviation detection comparing current vs baseline
    - Implement style consistency scoring across files
    - _Requirements: Design Component 6, Property 22_
  
  - [ ]* 7.2 Write property test for style features
    - **Property 22: Style Feature Extraction Completeness** - All required features extracted
    - **Validates: Design Property 22**

- [ ] 8. Implement Git Metadata Analyzer
  - [x] 8.1 Create git analysis module
    - Implement `GitMetadataAnalyzer` class with `analyze()` method
    - Add git commit history extraction using gitpython
    - Implement authoring speed calculation (lines per minute)
    - Add commit pattern analysis (sizes, timing, intervals)
    - Implement code churn metrics calculation
    - Handle repositories without git history gracefully
    - Ensure read-only git operations
    - _Requirements: Design Component 7, Git Metadata Analysis Algorithm, Properties 20, 23_
  
  - [ ]* 8.2 Write property test for git operations
    - **Property 20: Git Read-Only Operations** - No repository modifications
    - **Property 23: Authoring Speed Calculation** - Correct lines per minute calculation
    - **Validates: Design Properties 20, 23**

- [ ] 9. Implement Vibe Score Calculator
  - [x] 9.1 Create score calculation module
    - Implement `VibeScoreCalculator` class with `calculate_file_score()` and `calculate_repo_score()`
    - Add signal weighting and aggregation logic
    - Implement confidence calculation based on signal agreement
    - Add risk level determination (LOW < 30, MEDIUM 30-70, HIGH > 70)
    - Generate score explanations from contributing signals
    - Handle missing or incomplete signals gracefully
    - _Requirements: Design Component 8, Vibe Score Calculation Algorithm, Properties 4, 5, 7_
  
  - [ ]* 9.2 Write property tests for score calculation
    - **Property 4: Risk Level Consistency** - Risk levels correctly assigned based on thresholds
    - **Property 5: Signal Weight Conservation** - Total weight is positive when signals present
    - **Property 7: Monotonic Confidence** - Confidence increases with more signals
    - **Validates: Design Properties 4, 5, 7**

- [ ] 10. Implement Code File Analyzer orchestration
  - [x] 10.1 Create file analyzer module
    - Implement `CodeFileAnalyzer` class with `analyze_file()` method
    - Add language detection from file extension and content
    - Integrate all detection modules (pattern, statistical, style)
    - Add AST parsing with tree-sitter for supported languages
    - Implement signal collection and aggregation
    - Add error handling for parse failures and unsupported languages
    - Calculate per-file vibe scores
    - _Requirements: Design Component 3, File Analysis Algorithm, Property 18_
  
  - [ ]* 10.2 Write property test for language detection
    - **Property 18: Language Detection Consistency** - Same file always gets same language
    - **Validates: Design Property 18**

- [ ] 11. Checkpoint - Ensure analysis pipeline works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement Repository Scanner orchestration
  - [x] 12.1 Create repository scanner module
    - Implement `RepositoryScanner` class with `scan()` method
    - Add parallel processing support using multiprocessing
    - Implement file discovery and filtering
    - Coordinate analysis across all files
    - Aggregate file results into repository-level metrics
    - Add progress tracking and reporting
    - Implement error handling and recovery for file failures
    - Calculate aggregate statistics (total lines, AI vs human lines)
    - _Requirements: Design Component 2, Main Scanning Algorithm, Properties 8, 16, 19, 25_
  
  - [ ]* 12.2 Write property tests for repository scanning
    - **Property 8: Performance Constraint** - 10K lines scanned in under 10 seconds
    - **Property 16: Parallel Processing Safety** - Parallel results match sequential
    - **Property 19: Offline Operation** - No external network calls
    - **Property 25: Scan Result Completeness** - All non-skipped files analyzed
    - **Validates: Design Properties 8, 16, 19, 25**

- [ ] 13. Implement Report Generator
  - [x] 13.1 Create report generation module
    - Implement `ReportGenerator` class with `generate()` method
    - Add terminal output formatter with rich library (colors, tables, progress bars)
    - Implement JSON output formatter with proper serialization
    - Add markdown output formatter with tables and formatting
    - Implement file sorting by vibe score (descending)
    - Add risk summary generation
    - Include detection signal breakdown in all formats
    - _Requirements: Design Component 9, Output Format Specifications, Properties 11, 12, 13_
  
  - [ ]* 13.2 Write property tests for report generation
    - **Property 11: JSON Serialization Round Trip** - Serialize then deserialize produces equivalent result
    - **Property 12: Report Content Completeness** - All required fields present in reports
    - **Property 13: File Sorting Invariant** - Files sorted by vibe score descending
    - **Validates: Design Properties 11, 12, 13**

- [ ] 14. Implement CLI interface
  - [x] 14.1 Create CLI module with click
    - Implement main `vibe-scanner` command with click
    - Add `scan` subcommand with all options (output format, workers, threshold, etc.)
    - Implement argument parsing and validation
    - Add configuration file loading support (YAML)
    - Implement progress indicators and status messages
    - Add verbose and quiet modes
    - Implement exit code logic based on threshold
    - Display formatted output to terminal
    - _Requirements: Design Component 1, CLI Command Structure, Property 14_
  
  - [ ]* 14.2 Write property test for CLI exit codes
    - **Property 14: Threshold Exit Code Consistency** - Non-zero exit when score exceeds threshold
    - **Validates: Design Property 14**

- [ ] 15. Implement Python library API
  - [ ] 15.1 Create public library interface
    - Expose `scan_repository()` convenience function
    - Export main classes: `RepositoryScanner`, `ScanConfig`, `ScanResult`
    - Add type hints to all public APIs
    - Create `__all__` exports in `__init__.py`
    - Document library usage patterns
    - _Requirements: Design Example Usage section_
  
  - [ ]* 15.2 Write integration tests for library API
    - Test programmatic scanning via library
    - Test custom configuration options
    - Verify results match CLI output for same repository
    - _Requirements: Design Example Usage section_

- [ ] 16. Checkpoint - Ensure CLI and library interfaces work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Implement error handling and edge cases
  - [ ] 17.1 Add comprehensive error handling
    - Handle file read errors (permissions, encoding)
    - Handle invalid git repositories gracefully
    - Handle unsupported languages with fallback analysis
    - Handle parse errors with text-based fallback
    - Handle memory limits for large files
    - Add error reporting in scan results
    - Implement graceful degradation for missing features
    - _Requirements: Design Error Handling section, Property 24_
  
  - [ ]* 17.2 Write tests for error scenarios
    - Test all error scenarios from design document
    - Verify graceful degradation
    - Test error reporting completeness
    - **Property 24: Error Reporting Completeness** - Errors included in final report
    - **Validates: Design Property 24**

- [ ] 18. Implement configuration and defaults
  - [ ] 18.1 Create configuration system
    - Implement default configuration values
    - Add YAML configuration file support (`.vibe-scanner.yml`)
    - Implement configuration merging (file + CLI args)
    - Add configuration validation
    - Create default include/exclude patterns for common projects
    - _Requirements: Design CLI Command Structure, Configuration File section_

- [ ] 19. Add tree-sitter language support
  - [ ] 19.1 Set up tree-sitter parsers
    - Install tree-sitter grammars for Python, JavaScript, TypeScript, Java, Go, Rust
    - Create language parser registry
    - Implement AST parsing wrapper for each language
    - Add language-specific feature extraction
    - Handle parser initialization and caching
    - _Requirements: Design Dependencies section_

- [ ] 20. Implement line-level scoring (optional enhancement)
  - [ ] 20.1 Add line-level analysis
    - Implement line-by-line vibe scoring
    - Add line score aggregation to file scores
    - Include line scores in detailed reports
    - _Requirements: Design Model 2 (VibeScore.line_scores), Property 26_
  
  - [ ]* 20.2 Write property test for line scores
    - **Property 26: Line Score Bounds** - All line scores between 0-100
    - **Validates: Design Property 26**

- [ ] 21. Create documentation and examples
  - [ ] 21.1 Write user documentation
    - Create README.md with installation instructions
    - Document CLI usage with examples
    - Document Python library API with code examples
    - Add configuration file documentation
    - Create CONTRIBUTING.md for open-source contributors
    - Document supported languages and detection methods
    - _Requirements: MVP scope - good documentation for contributors_

- [ ] 22. Create test repositories and validation
  - [ ] 22.1 Set up test fixtures
    - Create synthetic test repositories with known AI/human code ratios
    - Add test cases for each supported language
    - Create edge case test files (empty, very large, malformed)
    - Set up integration test suite with real repositories
    - _Requirements: Design Testing Strategy section_
  
  - [ ]* 22.2 Write end-to-end integration tests
    - Test full scan workflow on test repositories
    - Test all output formats (terminal, JSON, markdown)
    - Test parallel processing with multiple workers
    - Test performance with 10K line repository
    - Verify accuracy against known test cases
    - _Requirements: Design Testing Strategy, Integration Testing section_

- [ ] 23. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 24. Package and distribution setup
  - [ ] 24.1 Prepare for distribution
    - Finalize `pyproject.toml` with package metadata
    - Create entry point for CLI command
    - Add LICENSE file (choose open-source license)
    - Create CHANGELOG.md
    - Set up package build configuration
    - Test installation from source
    - _Requirements: MVP scope - free, open-source CLI tool_

## Notes

- Tasks marked with `*` are optional testing tasks that can be skipped for faster MVP delivery
- The implementation uses Python 3.9+ as specified in the design document
- All core detection algorithms are implemented based on the formal specifications in the design
- The MVP focuses on local repository scanning; remote GitHub scanning can be added later
- Plugin system architecture is designed but plugin loading can be implemented post-MVP
- Performance target: 10K lines in <10 seconds (Property 8)
- All operations must be offline (no external API calls for basic detection)
- The architecture supports future SaaS extensions without core changes
