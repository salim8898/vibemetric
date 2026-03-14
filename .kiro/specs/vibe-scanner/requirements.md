# Requirements Document: vibe-scanner

## Introduction

vibe-scanner is an open-source CLI tool and Python library that detects AI-generated code in repositories. The system analyzes code files using multiple detection methods including pattern detection, statistical analysis, stylometric analysis, and git metadata mining to produce a Vibe Score (0-100%) indicating the likelihood that code was AI-generated. The tool supports file-level, line-level, and repository-level analysis with multiple output formats while maintaining offline operation and extensibility for future detection methods.

## Glossary

- **Vibe_Score**: A numerical value between 0 and 100 representing the likelihood that code was AI-generated
- **Detection_Signal**: An individual analysis result from a specific detection method (pattern, statistical, style, or git)
- **Risk_Level**: A categorical assessment (LOW, MEDIUM, HIGH) derived from the Vibe Score
- **Repository_Scanner**: The core orchestration component that coordinates file discovery and analysis
- **Code_Analyzer**: Component that applies multiple detection methods to individual code files
- **Pattern_Detector**: Component that identifies AI-specific code patterns and signatures
- **Statistical_Analyzer**: Component that performs perplexity and predictability analysis
- **Style_Analyzer**: Component that analyzes coding style consistency and deviations
- **Git_Analyzer**: Component that analyzes commit patterns and authoring metadata
- **Score_Calculator**: Component that aggregates detection signals into final Vibe Scores
- **Report_Generator**: Component that formats scan results into various output formats
- **CLI_Interface**: Command-line interface for user interaction
- **Hallucination**: Non-existent or incorrect API references commonly produced by AI code generators
- **Perplexity**: A statistical measure of code predictability (lower values indicate more AI-like code)
- **Style_Baseline**: A profile of a developer's typical coding style extracted from git history
- **Authoring_Speed**: Lines of code per minute calculated from git commit metadata
- **Confidence**: A value between 0 and 1 indicating the reliability of a Vibe Score

## Requirements

### Requirement 1: Repository Scanning

**User Story:** As a developer, I want to scan my local repository for AI-generated code, so that I can understand what portions of my codebase may have been AI-assisted.

#### Acceptance Criteria

1. WHEN a user provides a valid repository path, THE Repository_Scanner SHALL discover all code files in the repository
2. WHEN discovering files, THE Repository_Scanner SHALL apply include patterns to select files for analysis
3. WHEN discovering files, THE Repository_Scanner SHALL apply exclude patterns to filter out unwanted files
4. WHEN files are discovered, THE Repository_Scanner SHALL ensure no duplicate file paths exist in the results
5. WHEN scanning completes, THE Repository_Scanner SHALL return a complete ScanResult with all analyzed files
6. WHEN scanning a repository with 10,000 lines of code, THE Repository_Scanner SHALL complete analysis in under 10 seconds

### Requirement 2: File Analysis

**User Story:** As a developer, I want each code file analyzed using multiple detection methods, so that I can get accurate AI-likelihood assessments.

#### Acceptance Criteria

1. WHEN analyzing a file, THE Code_Analyzer SHALL apply all registered detection methods
2. WHEN a file is analyzed, THE Code_Analyzer SHALL produce a FileAnalysisResult with a valid Vibe Score
3. WHEN a file cannot be parsed, THE Code_Analyzer SHALL fall back to text-based analysis
4. WHEN a file exceeds the maximum size limit, THE Code_Analyzer SHALL skip the file and log a warning
5. WHEN analysis completes, THE Code_Analyzer SHALL ensure the Vibe Score is between 0 and 100



### Requirement 3: Pattern Detection

**User Story:** As a security engineer, I want to detect AI-specific code patterns, so that I can identify code that exhibits common AI generation signatures.

#### Acceptance Criteria

1. WHEN analyzing code, THE Pattern_Detector SHALL identify AI-style comment patterns
2. WHEN analyzing code, THE Pattern_Detector SHALL detect uniform complexity across functions
3. WHEN analyzing code, THE Pattern_Detector SHALL identify hallucination patterns (non-existent APIs)
4. WHEN patterns are detected, THE Pattern_Detector SHALL return a DetectionSignal with score between 0 and 100
5. WHEN multiple patterns are found, THE Pattern_Detector SHALL aggregate pattern scores into an overall pattern signal

### Requirement 4: Statistical Analysis

**User Story:** As a data scientist, I want statistical analysis of code characteristics, so that I can quantify code predictability and perplexity.

#### Acceptance Criteria

1. WHEN analyzing code, THE Statistical_Analyzer SHALL calculate perplexity scores for the token sequence
2. WHEN analyzing code, THE Statistical_Analyzer SHALL calculate code predictability metrics
3. WHEN analyzing code, THE Statistical_Analyzer SHALL analyze token distribution patterns
4. WHEN statistical metrics are calculated, THE Statistical_Analyzer SHALL normalize all values to 0-100 range
5. WHEN analysis completes, THE Statistical_Analyzer SHALL return a DetectionSignal with confidence between 0 and 1

### Requirement 5: Style Analysis

**User Story:** As an engineering manager, I want to detect coding style inconsistencies, so that I can identify code that deviates from team conventions.

#### Acceptance Criteria

1. WHEN analyzing code, THE Style_Analyzer SHALL extract style features including indentation, naming conventions, and line length patterns
2. WHEN a style baseline exists, THE Style_Analyzer SHALL compare current code against the baseline
3. WHEN analyzing multiple files, THE Style_Analyzer SHALL detect style shifts across the codebase
4. WHEN style deviations are found, THE Style_Analyzer SHALL include them in the detection signal evidence
5. WHEN no baseline exists, THE Style_Analyzer SHALL operate with reduced confidence

### Requirement 6: Git Metadata Analysis

**User Story:** As a CTO, I want to analyze git commit patterns, so that I can identify unusually rapid code generation that may indicate AI assistance.

#### Acceptance Criteria

1. WHEN git analysis is enabled, THE Git_Analyzer SHALL extract commit history for analyzed files
2. WHEN commits are available, THE Git_Analyzer SHALL calculate authoring speed in lines per minute
3. WHEN commits are available, THE Git_Analyzer SHALL detect unusual commit sizes and timing patterns
4. WHEN authoring speed exceeds normal thresholds, THE Git_Analyzer SHALL increase the AI-likelihood score
5. WHEN no git history is available, THE Git_Analyzer SHALL return a null signal without failing the scan

### Requirement 7: Vibe Score Calculation

**User Story:** As a developer, I want a single comprehensive score, so that I can quickly assess AI-likelihood without analyzing multiple metrics.

#### Acceptance Criteria

1. WHEN detection signals are collected, THE Score_Calculator SHALL aggregate them using weighted averaging
2. WHEN calculating scores, THE Score_Calculator SHALL ensure the overall score is between 0 and 100
3. WHEN calculating scores, THE Score_Calculator SHALL ensure confidence values are between 0 and 1
4. WHEN the overall score is below 30, THE Score_Calculator SHALL assign risk level LOW
5. WHEN the overall score is between 30 and 70, THE Score_Calculator SHALL assign risk level MEDIUM
6. WHEN the overall score is 70 or above, THE Score_Calculator SHALL assign risk level HIGH
7. WHEN multiple signals are present, THE Score_Calculator SHALL calculate confidence based on signal agreement

### Requirement 8: Report Generation

**User Story:** As a developer, I want scan results in multiple formats, so that I can view them in the terminal or integrate them into CI/CD pipelines.

#### Acceptance Criteria

1. WHEN terminal format is requested, THE Report_Generator SHALL produce formatted output with colors and progress bars
2. WHEN JSON format is requested, THE Report_Generator SHALL produce valid, parseable JSON
3. WHEN markdown format is requested, THE Report_Generator SHALL produce properly formatted markdown with tables
4. WHEN generating reports, THE Report_Generator SHALL include overall vibe score, risk level, and confidence
5. WHEN generating reports, THE Report_Generator SHALL include per-file results sorted by vibe score
6. WHEN generating reports, THE Report_Generator SHALL include detection signal breakdown

### Requirement 9: CLI Interface

**User Story:** As a developer, I want a command-line interface, so that I can easily scan repositories from my terminal.

#### Acceptance Criteria

1. WHEN the scan command is invoked with a repository path, THE CLI_Interface SHALL initialize the scanner and display results
2. WHEN invalid arguments are provided, THE CLI_Interface SHALL display helpful error messages and usage information
3. WHEN the --output option is specified, THE CLI_Interface SHALL generate reports in the requested format
4. WHEN the --threshold option is specified, THE CLI_Interface SHALL exit with error code if the score exceeds the threshold
5. WHEN the --verbose option is specified, THE CLI_Interface SHALL display detailed progress and metrics
6. WHEN a configuration file exists, THE CLI_Interface SHALL load settings from the file

### Requirement 10: Parallel Processing

**User Story:** As a developer, I want fast scanning of large repositories, so that I can analyze codebases efficiently.

#### Acceptance Criteria

1. WHEN scanning multiple files, THE Repository_Scanner SHALL process files in parallel using multiple workers
2. WHEN parallel workers are not specified, THE Repository_Scanner SHALL default to CPU count minus 1
3. WHEN the user specifies worker count, THE Repository_Scanner SHALL use the specified number of workers
4. WHEN parallel processing is active, THE Repository_Scanner SHALL maintain thread safety for result aggregation
5. WHEN scanning completes, THE Repository_Scanner SHALL ensure all files are processed exactly once

### Requirement 11: Error Handling

**User Story:** As a developer, I want graceful error handling, so that scanning continues even when individual files fail.

#### Acceptance Criteria

1. WHEN a file cannot be read, THE Repository_Scanner SHALL log a warning and continue with remaining files
2. WHEN a file cannot be parsed, THE Code_Analyzer SHALL attempt text-based analysis without AST
3. WHEN git analysis fails, THE Repository_Scanner SHALL disable git analysis and continue with other detection methods
4. WHEN an unsupported language is encountered, THE Code_Analyzer SHALL apply language-agnostic detection methods
5. WHEN memory limits are exceeded, THE Repository_Scanner SHALL skip the file and log an error
6. WHEN errors occur, THE Report_Generator SHALL include a summary of skipped files and errors in the final report

### Requirement 12: Configuration Management

**User Story:** As a team lead, I want to configure scanning behavior, so that I can customize analysis for my team's workflow.

#### Acceptance Criteria

1. WHEN a configuration file exists in the repository, THE CLI_Interface SHALL load settings from the file
2. WHEN command-line options are provided, THE CLI_Interface SHALL override configuration file settings
3. WHEN include patterns are specified, THE Repository_Scanner SHALL only analyze matching files
4. WHEN exclude patterns are specified, THE Repository_Scanner SHALL skip matching files
5. WHEN max file size is configured, THE Repository_Scanner SHALL skip files exceeding the limit

### Requirement 13: Language Support

**User Story:** As a polyglot developer, I want support for multiple programming languages, so that I can analyze diverse codebases.

#### Acceptance Criteria

1. WHEN a file is analyzed, THE Code_Analyzer SHALL detect the programming language from file extension and content
2. WHEN a supported language is detected, THE Code_Analyzer SHALL apply language-specific analysis including AST parsing
3. WHEN an unsupported language is detected, THE Code_Analyzer SHALL apply generic text-based analysis
4. WHEN language-specific features are unavailable, THE Code_Analyzer SHALL reduce confidence scores accordingly
5. THE Code_Analyzer SHALL support at minimum: Python, JavaScript, TypeScript, Java, Go, Rust, C, C++, Ruby, and PHP

### Requirement 14: Data Model Validation

**User Story:** As a developer, I want validated data structures, so that I can trust the integrity of scan results.

#### Acceptance Criteria

1. WHEN a ScanResult is created, THE Repository_Scanner SHALL ensure total_files_scanned equals the length of file_results
2. WHEN a ScanResult is created, THE Repository_Scanner SHALL ensure total_lines_analyzed equals the sum of all file code_lines
3. WHEN a ScanResult is created, THE Repository_Scanner SHALL ensure ai_generated_lines plus human_written_lines equals total_lines_analyzed
4. WHEN a VibeScore is created, THE Score_Calculator SHALL ensure overall_score is between 0 and 100
5. WHEN a VibeScore is created, THE Score_Calculator SHALL ensure confidence is between 0 and 1
6. WHEN DetectionSignals are created, THE Code_Analyzer SHALL ensure all scores are between 0 and 100 and all weights are between 0 and 1

### Requirement 15: Security and Privacy

**User Story:** As a security-conscious developer, I want offline operation, so that my code never leaves my machine.

#### Acceptance Criteria

1. THE Repository_Scanner SHALL perform all analysis locally without external API calls
2. WHEN parsing code, THE Code_Analyzer SHALL use sandboxed parsing without executing code
3. WHEN validating file paths, THE Repository_Scanner SHALL prevent path traversal attacks
4. WHEN handling git operations, THE Git_Analyzer SHALL use read-only operations
5. WHEN processing large files, THE Repository_Scanner SHALL implement resource limits to prevent denial of service

### Requirement 16: Extensibility

**User Story:** As a researcher, I want to add custom detection methods, so that I can experiment with new AI detection algorithms.

#### Acceptance Criteria

1. THE Code_Analyzer SHALL support registration of custom detection plugins
2. WHEN a custom plugin is registered, THE Code_Analyzer SHALL automatically integrate it into the analysis pipeline
3. WHEN a plugin is invoked, THE Code_Analyzer SHALL pass the code, language, and analysis context
4. WHEN a plugin returns a signal, THE Score_Calculator SHALL include it in score aggregation
5. WHEN a plugin fails, THE Code_Analyzer SHALL log the error and continue with remaining detection methods

### Requirement 17: Performance Monitoring

**User Story:** As a performance engineer, I want visibility into scan performance, so that I can optimize analysis speed.

#### Acceptance Criteria

1. WHEN verbose mode is enabled, THE Repository_Scanner SHALL log scan duration for each phase
2. WHEN verbose mode is enabled, THE Code_Analyzer SHALL track per-file analysis time
3. WHEN scanning completes, THE Report_Generator SHALL include total scan duration in the results
4. WHEN performance issues occur, THE Repository_Scanner SHALL log warnings about slow operations
5. WHEN memory usage is high, THE Repository_Scanner SHALL log memory consumption metrics

### Requirement 18: Output File Support

**User Story:** As a CI/CD engineer, I want to save scan results to files, so that I can archive and process them in automated pipelines.

#### Acceptance Criteria

1. WHEN the --output-file option is specified, THE CLI_Interface SHALL write results to the specified file
2. WHEN writing to a file, THE CLI_Interface SHALL create parent directories if they do not exist
3. WHEN a file write fails, THE CLI_Interface SHALL display an error message and exit with non-zero status
4. WHEN writing JSON output, THE CLI_Interface SHALL ensure the file contains valid JSON
5. WHEN writing completes successfully, THE CLI_Interface SHALL display a confirmation message

### Requirement 19: Threshold-Based Validation

**User Story:** As a CI/CD engineer, I want to fail builds when AI-generated code exceeds a threshold, so that I can enforce code quality policies.

#### Acceptance Criteria

1. WHEN the --threshold option is specified, THE CLI_Interface SHALL compare the overall vibe score against the threshold
2. WHEN the vibe score exceeds the threshold, THE CLI_Interface SHALL exit with non-zero status code
3. WHEN the vibe score is below the threshold, THE CLI_Interface SHALL exit with zero status code
4. WHEN threshold validation fails, THE CLI_Interface SHALL display a clear warning message
5. WHEN threshold validation fails, THE Report_Generator SHALL highlight files that contributed to exceeding the threshold

### Requirement 20: Line-Level Analysis

**User Story:** As a code reviewer, I want line-level AI-likelihood scores, so that I can identify specific code sections that may need review.

#### Acceptance Criteria

1. WHEN detailed analysis is requested, THE Code_Analyzer SHALL calculate vibe scores for individual lines
2. WHEN line scores are calculated, THE Code_Analyzer SHALL ensure each score is between 0 and 100
3. WHEN line scores are available, THE Report_Generator SHALL include them in detailed output formats
4. WHEN aggregating line scores, THE Score_Calculator SHALL ensure the sum of AI-generated and human-written lines equals total lines
5. WHEN line-level analysis is disabled, THE Code_Analyzer SHALL only calculate file-level scores for better performance
