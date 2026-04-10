"""
Tests for Velocity Analyzer
"""

import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import git
import pytest

from vibemetric.detectors.velocity_analyzer import VelocityAnalyzer
from vibemetric.models import DetectionLayerType


class TestVelocityAnalyzer:
    """Test velocity analysis functionality"""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary git repository for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
            repo = git.Repo.init(repo_path)

            # Configure git
            with repo.config_writer() as config:
                config.set_value("user", "name", "Test User")
                config.set_value("user", "email", "test@example.com")

            yield repo_path, repo

    def _create_commit(self, repo, filename: str, lines: int, days_ago: int = 0):
        """Helper to create a commit with specified lines"""
        repo_path = Path(repo.working_dir)
        file_path = repo_path / filename

        # Create file with specified number of lines
        content = "\n".join([f"line {i}" for i in range(lines)])
        file_path.write_text(content)

        # Add and commit
        repo.index.add([filename])

        # Set commit date using environment variables
        commit_date = datetime.now() - timedelta(days=days_ago)
        date_str = commit_date.strftime("%Y-%m-%d %H:%M:%S")

        # Use git environment variables to set commit date
        import os

        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_DATE"] = date_str

        with repo.config_writer() as config:
            config.set_value("user", "name", "Test User")
            config.set_value("user", "email", "test@example.com")

        commit = repo.index.commit(f"Add {filename}", author_date=date_str, commit_date=date_str)

        return commit

    def test_no_velocity_spike(self, temp_repo):
        """Test repository with consistent velocity"""
        repo_path, repo = temp_repo

        # Create commits with consistent velocity (10 lines per day)
        for i in range(40):
            self._create_commit(repo, f"file_{i}.txt", 10, days_ago=40 - i)

        # Analyze velocity
        analyzer = VelocityAnalyzer(str(repo_path))
        metrics = analyzer.analyze()

        # Verify no spike detected
        assert metrics["spike_detected"] is False
        assert metrics["spike_date"] is None
        assert metrics["velocity_increase"] == 0.0

    def test_velocity_spike_2x(self, temp_repo):
        """Test detection of 2x velocity spike"""
        repo_path, repo = temp_repo

        # Create baseline commits (10 lines per day for 30 days)
        for i in range(30):
            self._create_commit(repo, f"baseline_{i}.txt", 10, days_ago=60 - i)

        # Create spike commits (20 lines per day for 30 days)
        for i in range(30):
            self._create_commit(repo, f"spike_{i}.txt", 20, days_ago=30 - i)

        # Analyze velocity
        analyzer = VelocityAnalyzer(str(repo_path))
        metrics = analyzer.analyze()

        # Verify spike detected
        assert metrics["spike_detected"] is True
        assert metrics["spike_date"] is not None
        assert metrics["baseline_velocity"] > 0
        assert metrics["current_velocity"] > metrics["baseline_velocity"]

    def test_velocity_spike_3x(self, temp_repo):
        """Test detection of 3x velocity spike"""
        repo_path, repo = temp_repo

        # Create baseline commits (10 lines per day)
        for i in range(30):
            self._create_commit(repo, f"baseline_{i}.txt", 10, days_ago=60 - i)

        # Create spike commits (30 lines per day)
        for i in range(30):
            self._create_commit(repo, f"spike_{i}.txt", 30, days_ago=30 - i)

        # Analyze velocity
        analyzer = VelocityAnalyzer(str(repo_path))
        metrics = analyzer.analyze()

        # Verify spike detected
        assert metrics["spike_detected"] is True
        assert metrics["current_velocity"] >= metrics["baseline_velocity"] * 2.5

    def test_detection_signal_no_spike(self, temp_repo):
        """Test detection signal when no spike detected"""
        repo_path, repo = temp_repo

        # Create consistent commits
        for i in range(20):
            self._create_commit(repo, f"file_{i}.txt", 10, days_ago=20 - i)

        # Analyze and get signal
        analyzer = VelocityAnalyzer(str(repo_path))
        metrics = analyzer.analyze()
        signal = analyzer.get_detection_signal(metrics)

        # Verify signal
        assert signal.layer_type == DetectionLayerType.VELOCITY
        assert signal.score == 0.0
        assert signal.confidence == 0.0
        assert len(signal.evidence) == 0

    def test_detection_signal_2x_spike(self, temp_repo):
        """Test detection signal for 2x velocity spike"""
        repo_path, repo = temp_repo

        # Create baseline and spike
        for i in range(30):
            self._create_commit(repo, f"baseline_{i}.txt", 10, days_ago=60 - i)
        for i in range(30):
            self._create_commit(repo, f"spike_{i}.txt", 20, days_ago=30 - i)

        # Analyze and get signal
        analyzer = VelocityAnalyzer(str(repo_path))
        metrics = analyzer.analyze()
        signal = analyzer.get_detection_signal(metrics)

        # Verify signal (2x = 60 score)
        assert signal.score >= 60.0
        assert signal.confidence >= 0.78
        assert len(signal.evidence) > 0
        assert "Velocity increased" in signal.evidence[0]

    def test_detection_signal_3x_spike(self, temp_repo):
        """Test detection signal for 3x velocity spike"""
        repo_path, repo = temp_repo

        # Create baseline and spike
        for i in range(30):
            self._create_commit(repo, f"baseline_{i}.txt", 10, days_ago=60 - i)
        for i in range(30):
            self._create_commit(repo, f"spike_{i}.txt", 30, days_ago=30 - i)

        # Analyze and get signal
        analyzer = VelocityAnalyzer(str(repo_path))
        metrics = analyzer.analyze()
        signal = analyzer.get_detection_signal(metrics)

        # Verify signal (3x = 80 score)
        assert signal.score >= 80.0
        assert signal.confidence >= 0.82

    def test_detection_signal_4x_spike(self, temp_repo):
        """Test detection signal for 4x+ velocity spike"""
        repo_path, repo = temp_repo

        # Create baseline and spike
        for i in range(30):
            self._create_commit(repo, f"baseline_{i}.txt", 10, days_ago=60 - i)
        for i in range(30):
            self._create_commit(repo, f"spike_{i}.txt", 40, days_ago=30 - i)

        # Analyze and get signal
        analyzer = VelocityAnalyzer(str(repo_path))
        metrics = analyzer.analyze()
        signal = analyzer.get_detection_signal(metrics)

        # Verify signal (4x+ = 90 score)
        assert signal.score >= 90.0
        assert signal.confidence >= 0.85

    def test_author_filter(self, temp_repo):
        """Test velocity analysis for specific author"""
        repo_path, repo = temp_repo

        # Create commits from Test User
        for i in range(20):
            self._create_commit(repo, f"file_{i}.txt", 10, days_ago=20 - i)

        # Analyze for specific author
        analyzer = VelocityAnalyzer(str(repo_path))
        metrics = analyzer.analyze(author="Test User")

        # Should have velocity data
        assert metrics["baseline_velocity"] > 0

    def test_insufficient_data(self, temp_repo):
        """Test with insufficient commit history"""
        repo_path, repo = temp_repo

        # Create only 5 commits (not enough)
        for i in range(5):
            self._create_commit(repo, f"file_{i}.txt", 10, days_ago=5 - i)

        # Analyze velocity
        analyzer = VelocityAnalyzer(str(repo_path))
        metrics = analyzer.analyze()

        # Should return zero metrics
        assert metrics["baseline_velocity"] == 0.0
        assert metrics["current_velocity"] == 0.0
        assert metrics["spike_detected"] is False

    def test_non_git_repository(self):
        """Test velocity analysis on non-git directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = VelocityAnalyzer(tmpdir)
            metrics = analyzer.analyze()

            # Should return zero metrics
            assert metrics["baseline_velocity"] == 0.0
            assert metrics["current_velocity"] == 0.0
            assert metrics["spike_detected"] is False
