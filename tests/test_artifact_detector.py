"""
Tests for Artifact Detector
"""

import tempfile
from pathlib import Path

import git
import pytest
from vibemetric.detectors.artifact_detector import ARTIFACT_PATTERNS, ArtifactDetector
from vibemetric.models import DetectionLayerType


class TestArtifactDetector:
    """Test artifact detection functionality"""

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

    def test_detect_cursor(self, temp_repo):
        """Test detection of Cursor artifact"""
        repo_path, repo = temp_repo

        # Create .cursorrules file
        cursorrules = repo_path / ".cursorrules"
        cursorrules.write_text("# Cursor rules\n")

        # Commit the file
        repo.index.add([".cursorrules"])
        repo.index.commit("Add Cursor configuration")

        # Detect artifacts
        detector = ArtifactDetector(str(repo_path))
        artifacts = detector.detect()

        # Verify
        assert len(artifacts) == 1
        assert artifacts[0].tool_name == "Cursor"
        assert artifacts[0].file_path == ".cursorrules"
        assert artifacts[0].confidence == 0.9
        assert artifacts[0].adoption_date is not None
        assert "Test User" in artifacts[0].authors

    def test_detect_claude(self, temp_repo):
        """Test detection of Claude artifacts"""
        repo_path, repo = temp_repo

        # Create claude.md file
        claude_md = repo_path / "claude.md"
        claude_md.write_text("# Claude instructions\n")

        # Commit the file
        repo.index.add(["claude.md"])
        repo.index.commit("Add Claude configuration")

        # Detect artifacts
        detector = ArtifactDetector(str(repo_path))
        artifacts = detector.detect()

        # Verify
        assert len(artifacts) == 1
        assert artifacts[0].tool_name == "Claude"
        assert artifacts[0].file_path == "claude.md"

    def test_detect_kiro(self, temp_repo):
        """Test detection of Kiro artifact"""
        repo_path, repo = temp_repo

        # Create .kiro directory
        kiro_dir = repo_path / ".kiro"
        kiro_dir.mkdir()
        (kiro_dir / "config.yml").write_text("# Kiro config\n")

        # Commit the directory
        repo.index.add([".kiro/config.yml"])
        repo.index.commit("Add Kiro configuration")

        # Detect artifacts
        detector = ArtifactDetector(str(repo_path))
        artifacts = detector.detect()

        # Verify
        assert len(artifacts) == 1
        assert artifacts[0].tool_name == "Kiro"
        assert ".kiro" in artifacts[0].file_path

    def test_detect_multiple_tools(self, temp_repo):
        """Test detection of multiple AI tools"""
        repo_path, repo = temp_repo

        # Create multiple artifacts
        (repo_path / ".cursorrules").write_text("# Cursor\n")
        (repo_path / "claude.md").write_text("# Claude\n")

        kiro_dir = repo_path / ".kiro"
        kiro_dir.mkdir()
        (kiro_dir / "config.yml").write_text("# Kiro\n")

        # Commit all files
        repo.index.add([".cursorrules", "claude.md", ".kiro/config.yml"])
        repo.index.commit("Add multiple AI tool configurations")

        # Detect artifacts
        detector = ArtifactDetector(str(repo_path))
        artifacts = detector.detect()

        # Verify
        assert len(artifacts) == 3
        tool_names = [a.tool_name for a in artifacts]
        assert "Cursor" in tool_names
        assert "Claude" in tool_names
        assert "Kiro" in tool_names

    def test_no_artifacts(self, temp_repo):
        """Test repository with no AI tool artifacts"""
        repo_path, repo = temp_repo

        # Create regular files
        (repo_path / "README.md").write_text("# Project\n")
        (repo_path / "main.py").write_text("print('hello')\n")

        # Commit files
        repo.index.add(["README.md", "main.py"])
        repo.index.commit("Add regular files")

        # Detect artifacts
        detector = ArtifactDetector(str(repo_path))
        artifacts = detector.detect()

        # Verify
        assert len(artifacts) == 0

    def test_detection_signal_single_tool(self, temp_repo):
        """Test detection signal for single tool"""
        repo_path, repo = temp_repo

        # Create artifact
        (repo_path / ".cursorrules").write_text("# Cursor\n")
        repo.index.add([".cursorrules"])
        repo.index.commit("Add Cursor")

        # Detect and get signal
        detector = ArtifactDetector(str(repo_path))
        artifacts = detector.detect()
        signal = detector.get_detection_signal(artifacts)

        # Verify signal
        assert signal.layer_type == DetectionLayerType.ARTIFACT
        assert signal.score == 50.0  # 1 tool = 50
        assert signal.confidence == 0.9
        assert len(signal.evidence) == 1
        assert "Cursor" in signal.evidence[0]
        assert signal.metadata["num_tools"] == 1

    def test_detection_signal_multiple_tools(self, temp_repo):
        """Test detection signal for multiple tools"""
        repo_path, repo = temp_repo

        # Create multiple artifacts
        (repo_path / ".cursorrules").write_text("# Cursor\n")
        (repo_path / "claude.md").write_text("# Claude\n")
        (repo_path / ".kiro").mkdir()
        (repo_path / ".kiro" / "config.yml").write_text("# Kiro\n")

        repo.index.add([".cursorrules", "claude.md", ".kiro/config.yml"])
        repo.index.commit("Add multiple tools")

        # Detect and get signal
        detector = ArtifactDetector(str(repo_path))
        artifacts = detector.detect()
        signal = detector.get_detection_signal(artifacts)

        # Verify signal
        assert signal.score == 90.0  # 3+ tools = 90
        assert signal.confidence == 0.9
        assert len(signal.evidence) == 3
        assert signal.metadata["num_tools"] == 3

    def test_detection_signal_no_artifacts(self):
        """Test detection signal when no artifacts found"""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = ArtifactDetector(tmpdir)
            artifacts = detector.detect()
            signal = detector.get_detection_signal(artifacts)

            # Verify signal
            assert signal.score == 0.0
            assert signal.confidence == 0.0
            assert len(signal.evidence) == 0

    def test_non_git_repository(self):
        """Test detection in non-git directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Create artifact without git
            (repo_path / ".cursorrules").write_text("# Cursor\n")

            # Detect artifacts
            detector = ArtifactDetector(str(repo_path))
            artifacts = detector.detect()

            # Verify - should still detect artifact
            assert len(artifacts) == 1
            assert artifacts[0].tool_name == "Cursor"
            # But no git metadata
            assert artifacts[0].adoption_date is None
            assert artifacts[0].authors == []

    def test_artifact_patterns_coverage(self):
        """Test that all defined patterns are valid"""
        # Verify all tools have patterns
        assert len(ARTIFACT_PATTERNS) >= 10

        # Verify pattern format
        for tool_name, patterns in ARTIFACT_PATTERNS.items():
            assert isinstance(tool_name, str)
            assert isinstance(patterns, list)
            assert len(patterns) > 0
            for pattern in patterns:
                assert isinstance(pattern, str)
                assert len(pattern) > 0

    def test_skip_git_directory(self, temp_repo):
        """Test that .git directory is skipped during scan"""
        repo_path, repo = temp_repo

        # Create artifact in .git directory (should be ignored)
        git_dir = repo_path / ".git"
        (git_dir / ".cursorrules").write_text("# Should be ignored\n")

        # Create real artifact
        (repo_path / "claude.md").write_text("# Claude\n")
        repo.index.add(["claude.md"])
        repo.index.commit("Add Claude")

        # Detect artifacts
        detector = ArtifactDetector(str(repo_path))
        artifacts = detector.detect()

        # Verify - should only find claude.md, not .cursorrules in .git
        assert len(artifacts) == 1
        assert artifacts[0].tool_name == "Claude"
