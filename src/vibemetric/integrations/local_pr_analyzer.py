"""
Local PR Analyzer

Analyzes pull requests using local git commands (no API required).
Works for both public and private repositories.
"""

import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class LocalPRAnalyzer:
    """
    Analyzes PRs using local git commands.

    This is a fallback when GitHub API is unavailable or rate-limited.
    Works by fetching the PR branch locally and analyzing it.
    """

    def __init__(self, repo_path: str):
        """
        Initialize local PR analyzer.

        Args:
            repo_path: Path to local git repository
        """
        self.repo_path = Path(repo_path)

    def fetch_pr_locally(self, pr_number: int) -> Dict[str, Any]:
        """
        Fetch PR data using local git commands.

        Args:
            pr_number: Pull request number

        Returns:
            Dictionary with PR data (files, commits, etc.)
        """
        # Fetch PR branch
        pr_branch = f"pr-{pr_number}"

        try:
            # Fetch PR from remote
            subprocess.run(
                ["git", "fetch", "origin", f"pull/{pr_number}/head:{pr_branch}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Get PR base branch (usually main/master)
            base_branch = self._get_default_branch()

            # Get changed files
            files_data = self._get_changed_files(base_branch, pr_branch)

            # Get commits
            commits_data = self._get_commits(base_branch, pr_branch)

            # Get PR metadata from first commit
            pr_metadata = self._get_pr_metadata(pr_branch)

            return {
                "pr_number": pr_number,
                "title": pr_metadata.get("title", f"PR #{pr_number}"),
                "author": pr_metadata.get("author", "Unknown"),
                "description": pr_metadata.get("description", ""),
                "created_at": pr_metadata.get("created_at", datetime.now()),
                "merged_at": None,  # Can't determine from local git
                "state": "unknown",
                "files": files_data,
                "commits": commits_data,
            }

        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to fetch PR #{pr_number}: {e.stderr}")
        finally:
            # Cleanup: delete temporary branch
            try:
                subprocess.run(
                    ["git", "branch", "-D", pr_branch],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=False,
                )
            except Exception:
                pass

    def _get_default_branch(self) -> str:
        """Get the default branch name (main/master)"""
        try:
            result = subprocess.run(
                ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            # Output: refs/remotes/origin/main
            return result.stdout.strip().split("/")[-1]
        except subprocess.CalledProcessError:
            # Fallback to common names
            for branch in ["main", "master", "develop"]:
                result = subprocess.run(
                    ["git", "rev-parse", "--verify", branch],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=False,
                )
                if result.returncode == 0:
                    return branch
            return "main"

    def _get_changed_files(self, base_branch: str, pr_branch: str) -> List[Dict[str, Any]]:
        """Get list of changed files with content"""
        files_data = []

        # Get list of changed files
        result = subprocess.run(
            ["git", "diff", "--name-status", f"{base_branch}...{pr_branch}"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True,
        )

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) < 2:
                continue

            status, filename = parts[0], parts[1]

            # Get file stats
            stats = self._get_file_stats(base_branch, pr_branch, filename)

            # Get file content
            content = None
            if status != "D":  # Not deleted
                content = self._get_file_content(pr_branch, filename)

            files_data.append(
                {
                    "filename": filename,
                    "additions": stats["additions"],
                    "deletions": stats["deletions"],
                    "changes": stats["additions"] + stats["deletions"],
                    "patch": None,
                    "content": content,
                }
            )

        return files_data

    def _get_file_stats(self, base_branch: str, pr_branch: str, filename: str) -> Dict[str, int]:
        """Get additions/deletions for a file"""
        try:
            result = subprocess.run(
                ["git", "diff", "--numstat", f"{base_branch}...{pr_branch}", "--", filename],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout.strip():
                parts = result.stdout.strip().split("\t")
                additions = int(parts[0]) if parts[0] != "-" else 0
                deletions = int(parts[1]) if parts[1] != "-" else 0
                return {"additions": additions, "deletions": deletions}
        except Exception:
            pass

        return {"additions": 0, "deletions": 0}

    def _get_file_content(self, branch: str, filename: str) -> Optional[str]:
        """Get file content from branch"""
        try:
            result = subprocess.run(
                ["git", "show", f"{branch}:{filename}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except Exception:
            return None

    def _get_commits(self, base_branch: str, pr_branch: str) -> List[Dict[str, Any]]:
        """Get list of commits in PR"""
        commits_data = []

        try:
            # Get commit log
            result = subprocess.run(
                ["git", "log", f"{base_branch}..{pr_branch}", "--format=%H|%an|%ae|%at|%s"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) < 5:
                    continue

                sha, author, email, timestamp, subject = parts

                # Get full commit message
                msg_result = subprocess.run(
                    ["git", "log", "-1", "--format=%B", sha],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                commits_data.append(
                    {
                        "sha": sha,
                        "message": msg_result.stdout.strip(),
                        "author": author,
                        "timestamp": datetime.fromtimestamp(int(timestamp)),
                    }
                )
        except Exception:
            pass

        return commits_data

    def _get_pr_metadata(self, pr_branch: str) -> Dict[str, Any]:
        """Get PR metadata from branch"""
        try:
            # Get first commit info
            result = subprocess.run(
                ["git", "log", "-1", "--format=%an|%ae|%at|%s", pr_branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            parts = result.stdout.strip().split("|")
            if len(parts) >= 4:
                author, email, timestamp, subject = parts
                return {
                    "title": subject,
                    "author": email,
                    "created_at": datetime.fromtimestamp(int(timestamp)),
                    "description": "",
                }
        except Exception:
            pass

        return {}
