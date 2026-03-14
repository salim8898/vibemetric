"""
Unit tests for file discovery module.

Tests the discover_files() function and its helper functions.
"""

import os
import tempfile
import pytest
from pathlib import Path

from src.vibe_scanner.scanner import (
    discover_files,
    _matches_any_pattern,
    _has_valid_extension,
    _is_within_size_limit
)


class TestMatchesAnyPattern:
    """Tests for _matches_any_pattern helper function."""
    
    def test_simple_wildcard_match(self):
        """Test simple wildcard pattern matching."""
        assert _matches_any_pattern("file.py", ["*.py"])
        assert not _matches_any_pattern("file.js", ["*.py"])
    
    def test_double_star_pattern(self):
        """Test ** pattern for recursive matching."""
        assert _matches_any_pattern("src/utils/helper.py", ["**/*.py"])
        assert _matches_any_pattern("helper.py", ["**/*.py"])
        assert not _matches_any_pattern("helper.js", ["**/*.py"])
    
    def test_directory_exclusion(self):
        """Test directory exclusion patterns."""
        assert _matches_any_pattern("node_modules/package.js", ["**/node_modules/**"])
        assert _matches_any_pattern("src/node_modules/file.js", ["**/node_modules/**"])
        assert not _matches_any_pattern("src/file.js", ["**/node_modules/**"])
    
    def test_multiple_patterns(self):
        """Test matching against multiple patterns."""
        patterns = ["*.py", "*.js", "*.ts"]
        assert _matches_any_pattern("file.py", patterns)
        assert _matches_any_pattern("file.js", patterns)
        assert _matches_any_pattern("file.ts", patterns)
        assert not _matches_any_pattern("file.txt", patterns)
    
    def test_empty_patterns(self):
        """Test with empty pattern list."""
        assert not _matches_any_pattern("file.py", [])


class TestHasValidExtension:
    """Tests for _has_valid_extension helper function."""
    
    def test_valid_extension(self):
        """Test file with valid extension."""
        assert _has_valid_extension("file.py", [".py", ".js"])
        assert _has_valid_extension("file.js", [".py", ".js"])
    
    def test_invalid_extension(self):
        """Test file with invalid extension."""
        assert not _has_valid_extension("file.txt", [".py", ".js"])
        assert not _has_valid_extension("file", [".py", ".js"])
    
    def test_case_insensitive(self):
        """Test extension matching is case-insensitive."""
        assert _has_valid_extension("file.PY", [".py"])
        assert _has_valid_extension("file.Js", [".js"])
    
    def test_empty_extensions_list(self):
        """Test with empty extensions list accepts all files."""
        assert _has_valid_extension("file.py", [])
        assert _has_valid_extension("file.txt", [])
        assert _has_valid_extension("file", [])


class TestIsWithinSizeLimit:
    """Tests for _is_within_size_limit helper function."""
    
    def test_file_within_limit(self, tmp_path):
        """Test file within size limit."""
        # Create a small file (< 1KB)
        test_file = tmp_path / "small.txt"
        test_file.write_text("Hello, world!")
        
        assert _is_within_size_limit(str(test_file), 1)
    
    def test_file_exceeds_limit(self, tmp_path):
        """Test file exceeding size limit."""
        # Create a file larger than 1KB
        test_file = tmp_path / "large.txt"
        test_file.write_text("x" * 2000)  # 2KB
        
        assert not _is_within_size_limit(str(test_file), 1)
    
    def test_file_exactly_at_limit(self, tmp_path):
        """Test file exactly at size limit."""
        # Create a file exactly 1KB
        test_file = tmp_path / "exact.txt"
        test_file.write_text("x" * 1024)  # Exactly 1KB
        
        assert _is_within_size_limit(str(test_file), 1)
    
    def test_nonexistent_file(self):
        """Test with nonexistent file returns False."""
        assert not _is_within_size_limit("/nonexistent/file.txt", 1024)


class TestDiscoverFiles:
    """Tests for discover_files main function."""
    
    @pytest.fixture
    def test_repo(self, tmp_path):
        """Create a test repository structure."""
        # Create directory structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "utils").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "package").mkdir()
        
        # Create Python files
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "src" / "app.py").write_text("def main(): pass")
        (tmp_path / "src" / "utils" / "helper.py").write_text("def helper(): pass")
        (tmp_path / "tests" / "test_app.py").write_text("def test(): pass")
        
        # Create JavaScript files
        (tmp_path / "src" / "app.js").write_text("console.log('hello');")
        (tmp_path / "node_modules" / "package" / "index.js").write_text("module.exports = {};")
        
        # Create other files
        (tmp_path / "README.md").write_text("# README")
        (tmp_path / "config.txt").write_text("config")
        
        return tmp_path
    
    def test_discover_all_python_files(self, test_repo):
        """Test discovering all Python files."""
        files = discover_files(
            str(test_repo),
            include_patterns=["**/*.py"],
            exclude_patterns=[],
            file_extensions=[".py"],
            max_file_size_kb=1024
        )
        
        assert len(files) == 4
        assert "main.py" in files
        assert "src/app.py" in files
        assert "src/utils/helper.py" in files
        assert "tests/test_app.py" in files
    
    def test_exclude_node_modules(self, test_repo):
        """Test excluding node_modules directory."""
        files = discover_files(
            str(test_repo),
            include_patterns=["**/*.js"],
            exclude_patterns=["**/node_modules/**"],
            file_extensions=[".js"],
            max_file_size_kb=1024
        )
        
        assert len(files) == 1
        assert "src/app.js" in files
        assert "node_modules/package/index.js" not in files
    
    def test_multiple_extensions(self, test_repo):
        """Test discovering files with multiple extensions."""
        files = discover_files(
            str(test_repo),
            include_patterns=["**/*"],
            exclude_patterns=["**/node_modules/**"],
            file_extensions=[".py", ".js"],
            max_file_size_kb=1024
        )
        
        assert len(files) == 5
        assert "main.py" in files
        assert "src/app.py" in files
        assert "src/app.js" in files
        assert "README.md" not in files
        assert "config.txt" not in files
    
    def test_no_duplicates(self, test_repo):
        """Test that no duplicate file paths are returned."""
        files = discover_files(
            str(test_repo),
            include_patterns=["**/*.py", "**/*.py"],  # Duplicate pattern
            exclude_patterns=[],
            file_extensions=[".py"],
            max_file_size_kb=1024
        )
        
        # Check uniqueness
        assert len(files) == len(set(files))
    
    def test_sorted_output(self, test_repo):
        """Test that output is sorted alphabetically."""
        files = discover_files(
            str(test_repo),
            include_patterns=["**/*.py"],
            exclude_patterns=[],
            file_extensions=[".py"],
            max_file_size_kb=1024
        )
        
        assert files == sorted(files)
    
    def test_file_size_filtering(self, tmp_path):
        """Test file size filtering."""
        # Create small and large files
        small_file = tmp_path / "small.py"
        small_file.write_text("x" * 500)  # < 1KB
        
        large_file = tmp_path / "large.py"
        large_file.write_text("x" * 2000)  # > 1KB
        
        files = discover_files(
            str(tmp_path),
            include_patterns=["**/*.py"],
            exclude_patterns=[],
            file_extensions=[".py"],
            max_file_size_kb=1  # 1KB limit
        )
        
        assert "small.py" in files
        assert "large.py" not in files
    
    def test_relative_paths(self, test_repo):
        """Test that returned paths are relative to repo root."""
        files = discover_files(
            str(test_repo),
            include_patterns=["**/*.py"],
            exclude_patterns=[],
            file_extensions=[".py"],
            max_file_size_kb=1024
        )
        
        # All paths should be relative (not absolute)
        for file_path in files:
            assert not os.path.isabs(file_path)
            assert not file_path.startswith("/")
            assert not file_path.startswith("\\")
    
    def test_empty_repository(self, tmp_path):
        """Test with empty repository."""
        files = discover_files(
            str(tmp_path),
            include_patterns=["**/*.py"],
            exclude_patterns=[],
            file_extensions=[".py"],
            max_file_size_kb=1024
        )
        
        assert files == []
    
    def test_invalid_repo_path(self):
        """Test with invalid repository path."""
        with pytest.raises(ValueError, match="does not exist"):
            discover_files(
                "/nonexistent/path",
                include_patterns=["**/*.py"],
                exclude_patterns=[],
                file_extensions=[".py"],
                max_file_size_kb=1024
            )
    
    def test_file_as_repo_path(self, tmp_path):
        """Test with file instead of directory as repo path."""
        test_file = tmp_path / "file.txt"
        test_file.write_text("content")
        
        with pytest.raises(ValueError, match="not a directory"):
            discover_files(
                str(test_file),
                include_patterns=["**/*.py"],
                exclude_patterns=[],
                file_extensions=[".py"],
                max_file_size_kb=1024
            )
    
    def test_multiple_exclude_patterns(self, test_repo):
        """Test with multiple exclude patterns."""
        files = discover_files(
            str(test_repo),
            include_patterns=["**/*"],
            exclude_patterns=["**/node_modules/**", "**/tests/**"],
            file_extensions=[".py", ".js"],
            max_file_size_kb=1024
        )
        
        assert "tests/test_app.py" not in files
        assert "node_modules/package/index.js" not in files
        assert "main.py" in files
        assert "src/app.py" in files
    
    def test_specific_directory_include(self, test_repo):
        """Test including only specific directory."""
        files = discover_files(
            str(test_repo),
            include_patterns=["src/**/*.py"],
            exclude_patterns=[],
            file_extensions=[".py"],
            max_file_size_kb=1024
        )
        
        assert "src/app.py" in files
        assert "src/utils/helper.py" in files
        assert "main.py" not in files
        assert "tests/test_app.py" not in files
    
    def test_normalized_path_separators(self, test_repo):
        """Test that path separators are normalized to forward slashes."""
        files = discover_files(
            str(test_repo),
            include_patterns=["**/*.py"],
            exclude_patterns=[],
            file_extensions=[".py"],
            max_file_size_kb=1024
        )
        
        # All paths should use forward slashes
        for file_path in files:
            assert "\\" not in file_path or os.sep == "\\"
