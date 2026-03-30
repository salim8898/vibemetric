"""
Tests for developer profile generation.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import git

from src.vibemetric.profiles import DeveloperProfiler, DeveloperProfile


class TestDeveloperProfile:
    """Test DeveloperProfile data class."""
    
    def test_profile_creation(self):
        """Test creating a developer profile."""
        profile = DeveloperProfile(
            author="John Doe",
            email="john@example.com",
            ai_tools=["Cursor", "GitHub Copilot"],
            adoption_date=datetime(2024, 3, 15),
            days_using_ai=45,
            velocity_before_ai=120.0,
            velocity_after_ai=215.0,
            velocity_improvement=79.2,
            total_commits=156,
            ai_assisted_commits=89,
            ai_commit_percentage=57.1,
            average_ai_score=62.3
        )
        
        assert profile.author == "John Doe"
        assert profile.email == "john@example.com"
        assert len(profile.ai_tools) == 2
        assert profile.velocity_improvement == 79.2
    
    def test_profile_to_dict(self):
        """Test converting profile to dictionary."""
        profile = DeveloperProfile(
            author="Jane Smith",
            email="jane@example.com",
            ai_tools=["Claude"],
            adoption_date=datetime(2024, 1, 1),
            days_using_ai=30,
            velocity_before_ai=100.0,
            velocity_after_ai=180.0,
            velocity_improvement=80.0,
            total_commits=50,
            ai_assisted_commits=25,
            ai_commit_percentage=50.0,
            average_ai_score=55.0
        )
        
        data = profile.to_dict()
        
        assert data["author"] == "Jane Smith"
        assert data["email"] == "jane@example.com"
        assert data["ai_tools"] == ["Claude"]
        assert data["adoption_date"] == "2024-01-01T00:00:00"
        assert data["velocity_improvement"] == 80.0
    
    def test_profile_to_json(self):
        """Test converting profile to JSON."""
        profile = DeveloperProfile(
            author="Bob Wilson",
            email="bob@example.com",
            ai_tools=[],
            adoption_date=None,
            days_using_ai=0,
            velocity_before_ai=150.0,
            velocity_after_ai=150.0,
            velocity_improvement=0.0,
            total_commits=100,
            ai_assisted_commits=0,
            ai_commit_percentage=0.0,
            average_ai_score=10.0
        )
        
        json_str = profile.to_json()
        
        assert "Bob Wilson" in json_str
        assert "bob@example.com" in json_str
        assert json_str.startswith("{")
        assert json_str.endswith("}")
    
    def test_profile_format_terminal(self):
        """Test formatting profile for terminal display."""
        profile = DeveloperProfile(
            author="Alice Johnson",
            email="alice@example.com",
            ai_tools=["Cursor", "Kiro"],
            adoption_date=datetime(2024, 2, 1),
            days_using_ai=60,
            velocity_before_ai=90.0,
            velocity_after_ai=170.0,
            velocity_improvement=88.9,
            total_commits=200,
            ai_assisted_commits=120,
            ai_commit_percentage=60.0,
            average_ai_score=65.5
        )
        
        output = profile.format_terminal()
        
        assert "Alice Johnson" in output
        assert "alice@example.com" in output
        assert "Cursor" in output
        assert "Kiro" in output
        assert "2024-02-01" in output
        assert "60" in output  # days using AI
        assert "90.0" in output  # velocity before
        assert "170.0" in output  # velocity after
        assert "88.9" in output  # improvement
        assert "200" in output  # total commits
        assert "120" in output  # AI commits
        assert "60.0" in output  # percentage
        assert "65.5" in output  # average score
    
    def test_profile_format_no_ai_tools(self):
        """Test formatting profile with no AI tools."""
        profile = DeveloperProfile(
            author="Charlie Brown",
            email="charlie@example.com",
            ai_tools=[],
            adoption_date=None,
            days_using_ai=0,
            velocity_before_ai=100.0,
            velocity_after_ai=100.0,
            velocity_improvement=0.0,
            total_commits=50,
            ai_assisted_commits=0,
            ai_commit_percentage=0.0,
            average_ai_score=5.0
        )
        
        output = profile.format_terminal()
        
        assert "Charlie Brown" in output
        assert "No AI tools detected" in output


class TestDeveloperProfiler:
    """Test DeveloperProfiler class."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary git repository for testing."""
        temp_dir = tempfile.mkdtemp()
        repo = git.Repo.init(temp_dir)
        
        # Configure git
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test User")
            config.set_value("user", "email", "test@example.com")
        
        yield temp_dir, repo
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_profiler_initialization(self, temp_repo):
        """Test initializing profiler."""
        temp_dir, _ = temp_repo
        profiler = DeveloperProfiler(temp_dir)
        
        assert profiler.repo_path == Path(temp_dir)
        assert profiler.artifact_detector is not None
        assert profiler.velocity_analyzer is not None
        assert profiler.pattern_detector is not None
    
    def test_generate_profile_no_commits(self, temp_repo):
        """Test generating profile with no commits."""
        temp_dir, _ = temp_repo
        profiler = DeveloperProfiler(temp_dir)
        
        profile = profiler.generate_profile(author="Test User")
        
        assert profile is not None
        assert profile.author == "Test User"
        assert profile.total_commits == 0
    
    def test_generate_profile_with_commits(self, temp_repo):
        """Test generating profile with commits."""
        temp_dir, repo = temp_repo
        
        # Create some commits
        test_file = Path(temp_dir) / "test.py"
        
        # Commit 1
        test_file.write_text("print('hello')\n")
        repo.index.add([str(test_file)])
        repo.index.commit("Initial commit")
        
        # Commit 2
        test_file.write_text("print('hello')\nprint('world')\n")
        repo.index.add([str(test_file)])
        repo.index.commit("Add world")
        
        # Commit 3 with AI-style message
        test_file.write_text("print('hello')\nprint('world')\nprint('!')\n")
        repo.index.add([str(test_file)])
        repo.index.commit("feat: Add exclamation\n\n- Add exclamation mark\n- Improve output")
        
        profiler = DeveloperProfiler(temp_dir)
        profile = profiler.generate_profile(author="Test User")
        
        assert profile is not None
        assert profile.author == "Test User"
        assert profile.email == "test@example.com"
        assert profile.total_commits == 3
        assert profile.ai_assisted_commits >= 1  # At least the AI-style commit
    
    def test_generate_profile_with_ai_artifact(self, temp_repo):
        """Test generating profile with AI tool artifact."""
        temp_dir, repo = temp_repo
        
        # Create Cursor artifact
        cursor_file = Path(temp_dir) / ".cursorrules"
        cursor_file.write_text("# Cursor rules\n")
        repo.index.add([str(cursor_file)])
        repo.index.commit("Add Cursor configuration")
        
        # Add more commits
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("print('test')\n")
        repo.index.add([str(test_file)])
        repo.index.commit("Add test file")
        
        profiler = DeveloperProfiler(temp_dir)
        profile = profiler.generate_profile(author="Test User")
        
        assert profile is not None
        assert "Cursor" in profile.ai_tools
        assert profile.adoption_date is not None
        assert profile.days_using_ai >= 0
    
    def test_generate_all_profiles(self, temp_repo):
        """Test generating profiles for all developers."""
        temp_dir, repo = temp_repo
        
        # Create commits from different authors
        test_file = Path(temp_dir) / "test.py"
        
        # Commit from Test User
        test_file.write_text("print('hello')\n")
        repo.index.add([str(test_file)])
        repo.index.commit("Initial commit")
        
        # Change author and commit
        with repo.config_writer() as config:
            config.set_value("user", "name", "Another User")
            config.set_value("user", "email", "another@example.com")
        
        test_file.write_text("print('hello')\nprint('world')\n")
        repo.index.add([str(test_file)])
        repo.index.commit("Add world")
        
        profiler = DeveloperProfiler(temp_dir)
        profiles = profiler.generate_all_profiles()
        
        assert len(profiles) == 2
        assert profiles[0].total_commits >= profiles[1].total_commits  # Sorted by commits
    
    def test_generate_profile_by_email(self, temp_repo):
        """Test generating profile by email."""
        temp_dir, repo = temp_repo
        
        # Create commit
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("print('test')\n")
        repo.index.add([str(test_file)])
        repo.index.commit("Test commit")
        
        profiler = DeveloperProfiler(temp_dir)
        profile = profiler.generate_profile(email="test@example.com")
        
        assert profile is not None
        assert profile.email == "test@example.com"
        assert profile.total_commits == 1
    
    def test_generate_profile_no_author_or_email(self, temp_repo):
        """Test generating profile without author or email."""
        temp_dir, _ = temp_repo
        profiler = DeveloperProfiler(temp_dir)
        
        profile = profiler.generate_profile()
        
        assert profile is None
    
    def test_velocity_metrics_in_profile(self, temp_repo):
        """Test that velocity metrics are included in profile."""
        temp_dir, repo = temp_repo
        
        # Create multiple commits to generate velocity data
        test_file = Path(temp_dir) / "test.py"
        
        for i in range(5):
            test_file.write_text(f"print('line {i}')\n" * (i + 1))
            repo.index.add([str(test_file)])
            repo.index.commit(f"Commit {i}")
        
        profiler = DeveloperProfiler(temp_dir)
        profile = profiler.generate_profile(author="Test User")
        
        assert profile is not None
        assert profile.velocity_before_ai >= 0
        assert profile.velocity_after_ai >= 0
        assert isinstance(profile.velocity_improvement, float)
    
    def test_ai_commit_percentage_calculation(self, temp_repo):
        """Test AI commit percentage calculation."""
        temp_dir, repo = temp_repo
        
        test_file = Path(temp_dir) / "test.py"
        
        # Regular commit
        test_file.write_text("print('hello')\n")
        repo.index.add([str(test_file)])
        repo.index.commit("Add hello")
        
        # AI-style commit
        test_file.write_text("print('hello')\nprint('world')\n")
        repo.index.add([str(test_file)])
        repo.index.commit("feat: Add world\n\n- Add world print\n- Improve output\n- Update formatting")
        
        profiler = DeveloperProfiler(temp_dir)
        profile = profiler.generate_profile(author="Test User")
        
        assert profile is not None
        assert profile.total_commits == 2
        assert profile.ai_assisted_commits >= 1
        assert 0 <= profile.ai_commit_percentage <= 100
        assert profile.average_ai_score > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
