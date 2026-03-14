"""
Repository scanner orchestration.

This module provides file discovery and repository scanning functionality.
"""

import os
from pathlib import Path
from typing import List, Set
from pathlib import PurePath


def discover_files(
    repo_path: str,
    include_patterns: List[str],
    exclude_patterns: List[str],
    file_extensions: List[str],
    max_file_size_kb: int
) -> List[str]:
    """
    Discover code files in a repository with pattern matching and filtering.
    
    This function walks through the repository directory tree and discovers files
    that match the include patterns, don't match exclude patterns, have valid
    extensions, and are within the size limit.
    
    Args:
        repo_path: Path to the repository root directory
        include_patterns: List of glob patterns for files to include (e.g., "**/*.py")
        exclude_patterns: List of glob patterns for files to exclude (e.g., "**/node_modules/**")
        file_extensions: List of valid file extensions (e.g., [".py", ".js"])
        max_file_size_kb: Maximum file size in kilobytes
        
    Returns:
        Sorted list of relative file paths (relative to repo_path) with no duplicates
        
    Preconditions:
        - repo_path is a valid directory path
        - repo_path is readable by current user
        - include_patterns and exclude_patterns are valid glob patterns
        
    Postconditions:
        - Returns list of file paths matching include patterns
        - All returned paths exclude files matching exclude_patterns
        - All returned paths are relative to repo_path
        - List is sorted alphabetically
        - No duplicate paths in result
        
    Loop Invariants:
        - All discovered files match at least one include pattern
        - No discovered file matches any exclude pattern
        - All paths are valid and readable
    """
    # Validate inputs
    if not os.path.exists(repo_path):
        raise ValueError(f"Repository path does not exist: {repo_path}")
    if not os.path.isdir(repo_path):
        raise ValueError(f"Repository path is not a directory: {repo_path}")
    if not os.access(repo_path, os.R_OK):
        raise ValueError(f"Repository path is not readable: {repo_path}")
    
    # Convert to absolute path for consistent handling
    repo_path_abs = os.path.abspath(repo_path)
    
    # Use a set to ensure uniqueness during collection
    discovered_files: Set[str] = set()
    
    # Walk through the directory tree
    for root, dirs, files in os.walk(repo_path_abs):
        # Get relative path from repo root
        rel_root = os.path.relpath(root, repo_path_abs)
        if rel_root == ".":
            rel_root = ""
        
        # Check if current directory should be excluded
        if rel_root and _matches_any_pattern(rel_root, exclude_patterns):
            # Skip this directory and all subdirectories
            dirs.clear()
            continue
        
        # Filter directories to skip excluded ones
        dirs_to_remove = []
        for dir_name in dirs:
            if rel_root:
                dir_rel_path = os.path.join(rel_root, dir_name)
            else:
                dir_rel_path = dir_name
            
            if _matches_any_pattern(dir_rel_path, exclude_patterns):
                dirs_to_remove.append(dir_name)
        
        # Remove excluded directories from traversal
        for dir_name in dirs_to_remove:
            dirs.remove(dir_name)
        
        # Process files in current directory
        for file_name in files:
            # Construct relative file path
            if rel_root:
                file_rel_path = os.path.join(rel_root, file_name)
            else:
                file_rel_path = file_name
            
            # Normalize path separators for consistent pattern matching
            file_rel_path_normalized = file_rel_path.replace(os.sep, "/")
            
            # Check if file should be excluded
            if _matches_any_pattern(file_rel_path_normalized, exclude_patterns):
                continue
            
            # Check if file matches include patterns
            if not _matches_any_pattern(file_rel_path_normalized, include_patterns):
                continue
            
            # Check file extension
            if not _has_valid_extension(file_name, file_extensions):
                continue
            
            # Check file size
            file_abs_path = os.path.join(root, file_name)
            if not _is_within_size_limit(file_abs_path, max_file_size_kb):
                continue
            
            # Add to discovered files (using normalized path)
            discovered_files.add(file_rel_path_normalized)
    
    # Convert to sorted list for consistent output
    result = sorted(list(discovered_files))
    
    return result


def _matches_any_pattern(path: str, patterns: List[str]) -> bool:
    """
    Check if a path matches any of the given glob patterns.
    
    Supports glob patterns including:
    - * matches any characters except /
    - ** matches any characters including /
    - ? matches a single character
    
    Args:
        path: File or directory path to check (with forward slashes)
        patterns: List of glob patterns
        
    Returns:
        True if path matches at least one pattern, False otherwise
    """
    # Normalize path to use forward slashes
    path_normalized = path.replace(os.sep, "/")
    
    for pattern in patterns:
        # Normalize pattern to use forward slashes
        pattern_normalized = pattern.replace(os.sep, "/")
        
        # Use PurePath.match for glob pattern matching (supports **)
        # PurePath.match matches from the right, so we need to handle this carefully
        path_obj = PurePath(path_normalized)
        
        # Try direct match
        if path_obj.match(pattern_normalized):
            return True
        
        # For patterns starting with **, also try matching without the **
        if pattern_normalized.startswith("**/"):
            pattern_without_prefix = pattern_normalized[3:]
            if path_obj.match(pattern_without_prefix):
                return True
    
    return False


def _has_valid_extension(file_name: str, valid_extensions: List[str]) -> bool:
    """
    Check if a file has a valid extension.
    
    Args:
        file_name: Name of the file
        valid_extensions: List of valid extensions (e.g., [".py", ".js"])
        
    Returns:
        True if file has a valid extension, False otherwise
    """
    if not valid_extensions:
        # If no extensions specified, accept all files
        return True
    
    # Get file extension (including the dot)
    _, ext = os.path.splitext(file_name)
    
    # Check if extension is in the valid list
    return ext.lower() in [e.lower() for e in valid_extensions]


def _is_within_size_limit(file_path: str, max_size_kb: int) -> bool:
    """
    Check if a file is within the size limit.
    
    Args:
        file_path: Absolute path to the file
        max_size_kb: Maximum file size in kilobytes
        
    Returns:
        True if file is within size limit, False otherwise
    """
    try:
        # Get file size in bytes
        file_size_bytes = os.path.getsize(file_path)
        
        # Convert to kilobytes
        file_size_kb = file_size_bytes / 1024
        
        # Check against limit
        return file_size_kb <= max_size_kb
    except (OSError, IOError):
        # If we can't get file size, skip the file
        return False


# RepositoryScanner class will be implemented in Task 12



from datetime import datetime
from typing import Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

from .models import ScanConfig, ScanResult, RiskLevel, RiskSummary
from .file_analyzer import CodeFileAnalyzer
from .scorer import VibeScoreCalculator


class RepositoryScanner:
    """
    Orchestrates the scanning process across all files in a repository.
    
    Coordinates file discovery, parallel analysis, and result aggregation
    to produce comprehensive repository-level scan results.
    """
    
    def __init__(self, config: ScanConfig):
        """
        Initialize the repository scanner.
        
        Args:
            config: Scan configuration
        """
        self.config = config
        self.scorer = VibeScoreCalculator()
    
    def scan(self, repo_path: str) -> ScanResult:
        """
        Scan a repository for AI-generated code.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            ScanResult with complete analysis
        """
        start_time = datetime.now()
        
        # Discover files
        files = discover_files(
            repo_path,
            self.config.include_patterns,
            self.config.exclude_patterns,
            self.config.file_extensions,
            self.config.max_file_size
        )
        
        if not files:
            return self._create_empty_result(repo_path, start_time)
        
        # Analyze files (with optional parallel processing)
        if self.config.parallel_workers > 1:
            file_results = self._analyze_files_parallel(files, repo_path)
        else:
            file_results = self._analyze_files_sequential(files, repo_path)
        
        # Calculate repository-level vibe score
        repo_score = self.scorer.calculate_repo_score(file_results)
        
        # Calculate aggregate statistics
        total_lines = sum(f.code_lines for f in file_results)
        
        # Estimate AI vs human lines based on scores
        ai_generated_lines = sum(
            int(f.code_lines * (f.vibe_score.overall_score / 100.0))
            for f in file_results
        )
        human_written_lines = total_lines - ai_generated_lines
        
        # Generate risk summary
        risk_summary = self._generate_risk_summary(file_results, repo_score)
        
        # Calculate scan duration
        end_time = datetime.now()
        scan_duration = (end_time - start_time).total_seconds()
        
        return ScanResult(
            repo_path=repo_path,
            scan_timestamp=start_time,
            total_files_scanned=len(file_results),
            total_lines_analyzed=total_lines,
            overall_vibe_score=repo_score,
            file_results=file_results,
            ai_generated_lines=ai_generated_lines,
            human_written_lines=human_written_lines,
            risk_summary=risk_summary,
            scan_duration=scan_duration
        )
    
    def _analyze_files_sequential(self, files: List[str], repo_path: str) -> list:
        """Analyze files sequentially."""
        analyzer = CodeFileAnalyzer(enable_git=self.config.enable_git_analysis)
        results = []
        
        for i, file_path in enumerate(files, 1):
            if self.config.verbosity > 0:
                print(f"Analyzing {i}/{len(files)}: {file_path}")
            
            try:
                result = analyzer.analyze_file(file_path, repo_path)
                results.append(result)
            except Exception as e:
                if self.config.verbosity > 0:
                    print(f"Error analyzing {file_path}: {e}")
        
        return results
    
    def _analyze_files_parallel(self, files: List[str], repo_path: str) -> list:
        """Analyze files in parallel using multiprocessing."""
        results = []
        
        # Use ProcessPoolExecutor for parallel processing
        with ProcessPoolExecutor(max_workers=self.config.parallel_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._analyze_single_file, file_path, repo_path): file_path
                for file_path in files
            }
            
            # Collect results as they complete
            for i, future in enumerate(as_completed(future_to_file), 1):
                file_path = future_to_file[future]
                
                if self.config.verbosity > 0:
                    print(f"Completed {i}/{len(files)}: {file_path}")
                
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    if self.config.verbosity > 0:
                        print(f"Error analyzing {file_path}: {e}")
        
        return results
    
    def _analyze_single_file(self, file_path: str, repo_path: str):
        """Analyze a single file (for parallel processing)."""
        analyzer = CodeFileAnalyzer(enable_git=self.config.enable_git_analysis)
        return analyzer.analyze_file(file_path, repo_path)
    
    def _generate_risk_summary(self, file_results: list, repo_score) -> RiskSummary:
        """Generate risk summary from file results."""
        high_risk = sum(1 for f in file_results if f.vibe_score.risk_level == RiskLevel.HIGH)
        medium_risk = sum(1 for f in file_results if f.vibe_score.risk_level == RiskLevel.MEDIUM)
        low_risk = sum(1 for f in file_results if f.vibe_score.risk_level == RiskLevel.LOW)
        
        # Identify critical files (high risk)
        critical_files = [
            f.file_path for f in file_results 
            if f.vibe_score.risk_level == RiskLevel.HIGH
        ][:10]  # Limit to top 10
        
        return RiskSummary(
            high_risk_files=high_risk,
            medium_risk_files=medium_risk,
            low_risk_files=low_risk,
            critical_files_affected=critical_files
        )
    
    def _create_empty_result(self, repo_path: str, start_time: datetime) -> ScanResult:
        """Create an empty result when no files are found."""
        from .models import VibeScore
        
        return ScanResult(
            repo_path=repo_path,
            scan_timestamp=start_time,
            total_files_scanned=0,
            total_lines_analyzed=0,
            overall_vibe_score=VibeScore(
                overall_score=0.0,
                confidence=0.0,
                contributing_signals={},
                risk_level=RiskLevel.LOW,
                explanation="No files to analyze",
                line_scores=None
            ),
            file_results=[],
            ai_generated_lines=0,
            human_written_lines=0,
            risk_summary=RiskSummary(
                high_risk_files=0,
                medium_risk_files=0,
                low_risk_files=0,
                critical_files_affected=[]
            ),
            scan_duration=0.0
        )
