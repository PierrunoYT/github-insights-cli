"""
Repository analyzer module for extracting Git repository metrics and data.
"""

from git import Repo, InvalidGitRepositoryError, GitCommandError
from github import Github, GithubException
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import os

class RepoAnalyzer:
    """Analyzes Git repositories and extracts various metrics."""

    @classmethod
    def clone(cls, url: str, target_path: str) -> 'RepoAnalyzer':
        """Clone a repository from URL and return an analyzer instance.

        Args:
            url: Git repository URL to clone
            target_path: Local path to clone into
        
        Returns:
            RepoAnalyzer instance for the cloned repository
            
        Raises:
            ValueError: If cloning fails or target path already exists
        """
        try:
            Repo.clone_from(url, target_path)
            return cls(target_path)
        except GitCommandError as e:
            raise ValueError(f"Failed to clone repository: {str(e)}")

    def __init__(self, repo_path: str, github_token: Optional[str] = None):
        """Initialize the repository analyzer.

        Args:
            repo_path: Path to the Git repository
            github_token: GitHub API token for additional metrics
        
        Raises:
            ValueError: If the path is not a valid Git repository
        """
        self.repo_path = Path(repo_path)
        try:
            self.repo = Repo(repo_path)
            if not self.repo.git_dir:
                raise ValueError(f"Not a valid Git repository: {self.repo_path}")
            
            # Initialize GitHub API client if token provided
            self.gh = None
            self.gh_repo = None
            if github_token:
                self.gh = Github(github_token)
                self._init_github_repo()
                
        except InvalidGitRepositoryError:
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")

    def _init_github_repo(self):
        """Initialize GitHub repository connection if possible."""
        try:
            if not self.gh:
                return
                
            # Get the remote URL
            remote_url = next(self.repo.remotes.origin.urls)
            
            # Extract owner/repo from remote URL
            parts = remote_url.split('github.com/')[-1].replace('.git', '').split('/')
            if len(parts) >= 2:
                owner, repo_name = parts[-2:]
                self.gh_repo = self.gh.get_repo(f"{owner}/{repo_name}")
        except (GithubException, AttributeError, IndexError) as e:
            print(f"Warning: Could not initialize GitHub API: {str(e)}")

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

        metrics = {
            "commit_stats": self._analyze_commits(since_date, until_date),
            "contributor_stats": self._analyze_contributors(since_date, until_date),
            "code_stats": self._analyze_code(),
            "branch_stats": self._analyze_branches()
        }

        # Add GitHub-specific metrics if available
        if self.gh_repo:
            metrics["github_stats"] = self._analyze_github_metrics(since_date, until_date)

        return metrics

    def _analyze_github_metrics(self, since: Optional[datetime], until: Optional[datetime]) -> Dict[str, Any]:
        """Analyze GitHub-specific metrics.

        Returns:
            Dictionary containing GitHub-specific metrics
        """
        if not self.gh_repo:
            return {}

        try:
            # Get basic repository information
            metrics = {
                "stars": self.gh_repo.stargazers_count,
                "forks": self.gh_repo.forks_count,
                "open_issues": self.gh_repo.open_issues_count,
                "watchers": self.gh_repo.subscribers_count,
                "pull_requests": {
                    "open": len(list(self.gh_repo.get_pulls(state='open'))),
                    "merged": len(list(self.gh_repo.get_pulls(state='closed', sort='updated')))
                },
                "issues": {
                    "open": len(list(self.gh_repo.get_issues(state='open'))),
                    "closed": len(list(self.gh_repo.get_issues(state='closed')))
                }
            }

            # Get release information
            releases = list(self.gh_repo.get_releases())
            metrics["releases"] = {
                "total": len(releases),
                "latest": releases[0].tag_name if releases else None,
                "published_at": releases[0].published_at.isoformat() if releases else None
            }

            # Get workflow information if available
            try:
                workflows = list(self.gh_repo.get_workflows())
                metrics["workflows"] = {
                    "total": len(workflows),
                    "active": sum(1 for w in workflows if w.state == "active")
                }
            except GithubException:
                metrics["workflows"] = {"total": 0, "active": 0}

            return metrics

        except GithubException as e:
            print(f"Warning: Error fetching GitHub metrics: {str(e)}")
            return {}

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
            Dictionary containing code-related metrics including:
            - File statistics
            - Language distribution
            - Complexity metrics
            - Complexity trends over time
        """
        from radon.complexity import cc_visit
        from radon.raw import analyze
        from radon.metrics import mi_visit

        file_stats = {}
        complexity_stats = {
            "average_complexity": 0,
            "complex_functions": [],
            "maintainability_index": {},
            "total_complexity": 0,
            "complexity_distribution": {
                "simple": 0,      # 1-10
                "moderate": 0,    # 11-20
                "complex": 0,     # 21-30
                "very_complex": 0 # 31+
            },
            "complexity_trends": {
                "by_date": {},
                "by_author": {},
                "trend_direction": "stable"
            }
        }
        
        try:
            total_complexity = 0
            num_files = 0
            
            for blob in self.repo.head.commit.tree.traverse():
                if blob.type == "blob":
                    path = blob.path
                    content = blob.data_stream.read().decode('utf-8', errors='ignore')
                    extension = Path(path).suffix
                    
                    file_stats[path] = {
                        "size": blob.size,
                        "lines": len(content.splitlines()),
                        "extension": extension
                    }
                    
                    # Only analyze Python files for complexity
                    if extension == '.py':
                        try:
                            # Calculate cyclomatic complexity
                            complexity_metrics = cc_visit(content)
                            file_complexity = sum(metric.complexity for metric in complexity_metrics)
                            total_complexity += file_complexity
                            
                            # Analyze complex functions
                            complex_funcs = [
                                {
                                    "name": metric.name,
                                    "complexity": metric.complexity,
                                    "line_number": metric.lineno,
                                    "file": path
                                }
                                for metric in complexity_metrics
                                if metric.complexity > 10  # threshold for complex functions
                            ]
                            complexity_stats["complex_functions"].extend(complex_funcs)
                            
                            # Calculate maintainability index
                            mi_score = mi_visit(content, multi=True)
                            complexity_stats["maintainability_index"][path] = mi_score
                            
                            # Update complexity distribution
                            for metric in complexity_metrics:
                                if metric.complexity <= 10:
                                    complexity_stats["complexity_distribution"]["simple"] += 1
                                elif metric.complexity <= 20:
                                    complexity_stats["complexity_distribution"]["moderate"] += 1
                                elif metric.complexity <= 30:
                                    complexity_stats["complexity_distribution"]["complex"] += 1
                                else:
                                    complexity_stats["complexity_distribution"]["very_complex"] += 1
                            
                            num_files += 1
                            
                            # Add complexity metrics to file stats
                            file_stats[path]["complexity"] = {
                                "total": file_complexity,
                                "average": file_complexity / len(complexity_metrics) if complexity_metrics else 0,
                                "functions": len(complexity_metrics),
                                "maintainability_index": mi_score
                            }
                            
                        except Exception as e:
                            file_stats[path]["complexity_error"] = str(e)
                    
            # Calculate average complexity
            if num_files > 0:
                complexity_stats["average_complexity"] = total_complexity / num_files
            complexity_stats["total_complexity"] = total_complexity
            
        except (ValueError, AttributeError):  # Handle empty repositories
            pass

        return {
            "total_files": len(file_stats),
            "file_stats": file_stats,
            "language_distribution": self._get_language_distribution(file_stats),
            "complexity_metrics": complexity_stats
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
