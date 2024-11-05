"""
Repository analyzer module for extracting Git repository metrics and data.
"""

from git import Repo, InvalidGitRepositoryError
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

class RepoAnalyzer:
    """Analyzes Git repositories and extracts various metrics."""

    def __init__(self, repo_path: str):
        """Initialize the repository analyzer.

        Args:
            repo_path: Path to the Git repository
        
        Raises:
            ValueError: If the path is not a valid Git repository
        """
        self.repo_path = Path(repo_path)
        try:
            self.repo = Repo(repo_path)
            if not self.repo.git_dir:
                raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        except InvalidGitRepositoryError:
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")

    def analyze(self, since: Optional[str] = None, until: Optional[str] = None) -> Dict[str, Any]:
        """Analyze the repository and collect metrics.

        Args:
            since: Start date for analysis (YYYY-MM-DD)
            until: End date for analysis (YYYY-MM-DD)

        Returns:
            Dictionary containing various repository metrics
        """
        # Convert date strings to datetime objects with timezone
        since_date = datetime.strptime(since, "%Y-%m-%d").replace(tzinfo=timezone.utc) if since else None
        until_date = datetime.strptime(until, "%Y-%m-%d").replace(tzinfo=timezone.utc) if until else None

        return {
            "commit_stats": self._analyze_commits(since_date, until_date),
            "contributor_stats": self._analyze_contributors(since_date, until_date),
            "code_stats": self._analyze_code(),
            "branch_stats": self._analyze_branches()
        }

    def _analyze_commits(self, since: Optional[datetime], until: Optional[datetime]) -> Dict[str, Any]:
        """Analyze commit history and patterns.

        Returns:
            Dictionary containing commit-related metrics
        """
        try:
            commits = list(self.repo.iter_commits())
        except ValueError:  # Handle empty repositories
            commits = []

        commit_data = []

        for commit in commits:
            if since and commit.committed_datetime < since:
                continue
            if until and commit.committed_datetime > until:
                continue

            # Convert timezone-aware datetime to UTC
            commit_date = commit.committed_datetime.astimezone(timezone.utc)

            commit_data.append({
                "hash": commit.hexsha,
                "author": commit.author.name,
                "date": commit_date,
                "message": commit.message.strip(),
                "files_changed": list(commit.stats.files.keys()),
                "insertions": sum(f["insertions"] for f in commit.stats.files.values()),
                "deletions": sum(f["deletions"] for f in commit.stats.files.values())
            })

        df = pd.DataFrame(commit_data) if commit_data else pd.DataFrame(columns=["hash", "author", "date", "message", "files_changed", "insertions", "deletions"])
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"], utc=True)  # Convert to UTC datetime
        
        return {
            "total_commits": len(commit_data),
            "commit_frequency": self._calculate_commit_frequency(df),
            "top_contributors": self._get_top_contributors(df),
            "commit_activity": self._get_commit_activity(df)
        }

    def _analyze_contributors(self, since: Optional[datetime], until: Optional[datetime]) -> Dict[str, Any]:
        """Analyze contributor statistics and patterns.

        Returns:
            Dictionary containing contributor-related metrics
        """
        contributors = {}
        try:
            for commit in self.repo.iter_commits():
                if since and commit.committed_datetime < since:
                    continue
                if until and commit.committed_datetime > until:
                    continue

                author = commit.author.name
                if author not in contributors:
                    contributors[author] = {
                        "commits": 0,
                        "insertions": 0,
                        "deletions": 0,
                        "files_touched": set()
                    }

                contributors[author]["commits"] += 1
                for fname, stats in commit.stats.files.items():
                    contributors[author]["insertions"] += stats["insertions"]
                    contributors[author]["deletions"] += stats["deletions"]
                    contributors[author]["files_touched"].add(fname)
        except ValueError:  # Handle empty repositories
            pass

        return {
            "total_contributors": len(contributors),
            "contributor_details": contributors
        }

    def _analyze_code(self) -> Dict[str, Any]:
        """Analyze code statistics and complexity.

        Returns:
            Dictionary containing code-related metrics
        """
        file_stats = {}
        try:
            for blob in self.repo.head.commit.tree.traverse():
                if blob.type == "blob":
                    file_stats[blob.path] = {
                        "size": blob.size,
                        "lines": len(blob.data_stream.read().decode().splitlines()),
                        "extension": Path(blob.path).suffix
                    }
        except (ValueError, AttributeError):  # Handle empty repositories
            pass

        return {
            "total_files": len(file_stats),
            "file_stats": file_stats,
            "language_distribution": self._get_language_distribution(file_stats)
        }

    def _analyze_branches(self) -> Dict[str, Any]:
        """Analyze branch statistics and patterns.

        Returns:
            Dictionary containing branch-related metrics
        """
        try:
            branches = list(self.repo.heads)
            return {
                "total_branches": len(branches),
                "active_branch": self.repo.active_branch.name,
                "branch_details": {
                    branch.name: {
                        "commit_count": sum(1 for _ in self.repo.iter_commits(branch)),
                        "last_commit": self.repo.commit(branch).committed_datetime
                    }
                    for branch in branches
                }
            }
        except (ValueError, AttributeError):  # Handle empty repositories
            return {
                "total_branches": 0,
                "active_branch": "",
                "branch_details": {}
            }

    def _calculate_commit_frequency(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate commit frequency metrics."""
        if df.empty:
            return {"daily": 0, "weekly": 0, "monthly": 0}

        date_range = (df["date"].max() - df["date"].min()).days + 1
        if date_range == 0:  # Handle single day
            return {
                "daily": len(df),
                "weekly": len(df) * 7,
                "monthly": len(df) * 30
            }

        return {
            "daily": len(df) / date_range,
            "weekly": len(df) / (date_range / 7),
            "monthly": len(df) / (date_range / 30)
        }

    def _get_top_contributors(self, df: pd.DataFrame, limit: int = 5) -> Dict[str, int]:
        """Get the top contributors by commit count."""
        if df.empty:
            return {}

        return (df.groupby("author")
                .size()
                .sort_values(ascending=False)
                .head(limit)
                .to_dict())

    def _get_commit_activity(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get commit activity patterns."""
        if df.empty:
            return {}

        return (df.groupby(df["date"].dt.strftime("%Y-%m"))
                .size()
                .to_dict())

    def _get_language_distribution(self, file_stats: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
        """Calculate language distribution based on file extensions."""
        extensions = {}
        for stats in file_stats.values():
            ext = stats["extension"]
            if ext:
                extensions[ext] = extensions.get(ext, 0) + 1
        return extensions

    def watch(self, metrics: Optional[List[str]] = None) -> None:
        """Watch repository for real-time metrics.

        Args:
            metrics: List of specific metrics to track
        """
        # TODO: Implement real-time repository monitoring
        raise NotImplementedError("Real-time monitoring not yet implemented")
