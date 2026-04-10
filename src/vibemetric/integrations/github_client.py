"""
GitHub API Client

Fetches pull request data from GitHub repositories.
"""

import os
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

try:
    from github import Github, GithubException

    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False


class GitHubClient:
    """Client for fetching PR data from GitHub"""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.

        Args:
            token: GitHub personal access token (optional, uses GITHUB_TOKEN env var if not provided)
        """
        if not GITHUB_AVAILABLE:
            raise ImportError("PyGithub is not installed. Install with: pip install PyGithub")

        self.token = token or os.getenv("GITHUB_TOKEN")
        self.client = Github(self.token) if self.token else Github()

    def parse_pr_url(self, url: str) -> tuple[str, str, int]:
        """
        Parse GitHub PR URL to extract owner, repo, and PR number.

        Args:
            url: GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)

        Returns:
            Tuple of (owner, repo, pr_number)
        """
        pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
        match = re.search(pattern, url)

        if not match:
            raise ValueError(f"Invalid GitHub PR URL: {url}")

        owner, repo, pr_number = match.groups()
        return owner, repo, int(pr_number)

    def get_repo_from_path(self, repo_path: str) -> tuple[str, str]:
        """
        Extract GitHub owner/repo from local git repository.

        Args:
            repo_path: Path to local git repository

        Returns:
            Tuple of (owner, repo)
        """
        import subprocess

        try:
            # Get remote URL
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            remote_url = result.stdout.strip()

            # Parse GitHub URL
            # Supports: https://github.com/owner/repo.git or git@github.com:owner/repo.git
            patterns = [
                r"github\.com[:/]([^/]+)/([^/\.]+)",
            ]

            for pattern in patterns:
                match = re.search(pattern, remote_url)
                if match:
                    owner, repo = match.groups()
                    return owner, repo

            raise ValueError(f"Could not parse GitHub URL from: {remote_url}")

        except subprocess.CalledProcessError:
            raise ValueError(f"Not a git repository: {repo_path}")

    def fetch_pr(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Fetch pull request data from GitHub.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Dictionary with PR data including files and commits
        """
        try:
            # Get repository
            repository = self.client.get_repo(f"{owner}/{repo}")

            # Get pull request
            pr = repository.get_pull(pr_number)

            # Fetch files
            files_data = []
            for file in pr.get_files():
                file_data = {
                    "filename": file.filename,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch,
                    "content": None,
                }

                # Try to fetch file content (for analysis)
                try:
                    if file.status != "removed":
                        content_file = repository.get_contents(file.filename, ref=pr.head.sha)
                        if hasattr(content_file, "decoded_content"):
                            file_data["content"] = content_file.decoded_content.decode("utf-8")
                except Exception:
                    # File might be too large or binary
                    pass

                files_data.append(file_data)

            # Fetch commits
            commits_data = []
            for commit in pr.get_commits():
                commits_data.append(
                    {
                        "sha": commit.sha,
                        "message": commit.commit.message,
                        "author": commit.commit.author.name,
                        "timestamp": commit.commit.author.date,
                    }
                )

            # Build result
            return {
                "pr_number": pr.number,
                "title": pr.title,
                "author": pr.user.login,
                "description": pr.body or "",
                "created_at": pr.created_at,
                "merged_at": pr.merged_at,
                "state": pr.state,
                "files": files_data,
                "commits": commits_data,
            }

        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"PR #{pr_number} not found in {owner}/{repo}")
            elif e.status == 401:
                raise ValueError(
                    "GitHub authentication failed. Set GITHUB_TOKEN environment variable."
                )
            else:
                raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")

    def fetch_pr_by_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch pull request data from GitHub URL.

        Args:
            url: GitHub PR URL

        Returns:
            Dictionary with PR data
        """
        owner, repo, pr_number = self.parse_pr_url(url)
        return self.fetch_pr(owner, repo, pr_number)

    def fetch_pr_from_repo(self, repo_path: str, pr_number: int) -> Dict[str, Any]:
        """
        Fetch pull request data from local repository.

        Args:
            repo_path: Path to local git repository
            pr_number: Pull request number

        Returns:
            Dictionary with PR data
        """
        owner, repo = self.get_repo_from_path(repo_path)
        return self.fetch_pr(owner, repo, pr_number)
