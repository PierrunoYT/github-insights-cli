"""
Repository analyzer module for extracting Git repository metrics and data.
"""

from git import Repo, InvalidGitRepositoryError, GitCommandError
from github import Github, GithubException, RateLimitExceededException
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import os
import time
import threading
import queue

class RepoAnalyzer:
    """Analyzes Git repositories and extracts various metrics."""

    def watch(self, metrics: Optional[List[str]] = None, interval: int = 60) -> None:
        """Watch repository for real-time metrics.

        Args:
            metrics: List of specific metrics to track (commits, branches, contributors, github)
            interval: Update interval in seconds
            
        This method runs continuously until interrupted, printing metric updates
        to the console at the specified interval.
        """
        if not metrics:
            metrics = ["commits", "branches", "contributors"]

        stop_event = threading.Event()
        metrics_queue = queue.Queue()

        def update_metrics():
            while not stop_event.is_set():
                try:
                    current_metrics = {}
                    
                    if "commits" in metrics:
                        current_metrics["commits"] = len(list(self.repo.iter_commits()))
                    
                    if "branches" in metrics:
                        current_metrics["branches"] = len(list(self.repo.heads))
                    
                    if "contributors" in metrics:
                        contributors = set()
                        for commit in self.repo.iter_commits():
                            contributors.add(commit.author.name)
                        current_metrics["contributors"] = len(contributors)
                    
                    if self.gh_repo and "github" in metrics:
                        try:
                            current_metrics["stars"] = self.gh_repo.stargazers_count
                            current_metrics["open_issues"] = self.gh_repo.open_issues_count
                        except RateLimitExceededException as e:
                            # Wait for rate limit reset
                            rate_limit = self.gh.get_rate_limit()
                            reset_time = rate_limit.core.reset.timestamp() - datetime.now().timestamp()
                            if reset_time > 0:
                                time.sleep(reset_time + 1)
                            # Retry after waiting
                            current_metrics["stars"] = self.gh_repo.stargazers_count
                            current_metrics["open_issues"] = self.gh_repo.open_issues_count
                    
                    metrics_queue.put(current_metrics)
                except Exception as e:
                    metrics_queue.put({"error": str(e)})
                
                stop_event.wait(interval)

        # Start metrics collection in a separate thread
        metrics_thread = threading.Thread(target=update_metrics)
        metrics_thread.start()

        try:
            print(f"Watching repository: {self.repo_path}")
            print("Press Ctrl+C to stop...")
            
            while True:
                metrics_update = metrics_queue.get()
                if "error" in metrics_update:
                    print(f"Error: {metrics_update['error']}")
                    continue
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n=== Update at {timestamp} ===")
                for metric, value in metrics_update.items():
                    print(f"{metric}: {value}")
                
        except KeyboardInterrupt:
            print("\nStopping repository watch...")
            stop_event.set()
            metrics_thread.join()

    def _handle_rate_limit(self, e: RateLimitExceededException) -> None:
        """Handle GitHub API rate limit exception.
        
        Args:
            e: The rate limit exception
            
        Raises:
            RateLimitExceededException: If rate limit cannot be handled
        """
        if not self.gh:
            raise e

        rate_limit = self.gh.get_rate_limit()
        reset_timestamp = rate_limit.core.reset.timestamp()
        current_timestamp = datetime.now().timestamp()
        sleep_time = int(reset_timestamp - current_timestamp)

        if sleep_time <= 0:
            # Rate limit should be reset, retry immediately
            return
        elif sleep_time > 3600:  # Don't wait more than an hour
            raise e
        
        print(f"Rate limit exceeded. Waiting {sleep_time} seconds for reset...")
        time.sleep(sleep_time + 1)  # Add 1 second buffer

    def _analyze_github_metrics(self, since: Optional[datetime], until: Optional[datetime]) -> Dict[str, Any]:
        """Analyze GitHub-specific metrics with rate limit handling."""
        if not self.gh_repo:
            return {}

        try:
            metrics = {
                "stars": self.gh_repo.stargazers_count,
                "forks": self.gh_repo.forks_count,
                "open_issues": self.gh_repo.open_issues_count,
                "watchers": self.gh_repo.subscribers_count
            }

            # Get pull requests with retry logic
            try:
                metrics["pull_requests"] = {
                    "open": len(list(self.gh_repo.get_pulls(state='open'))),
                    "merged": len(list(self.gh_repo.get_pulls(state='closed', sort='updated')))
                }
            except RateLimitExceededException as e:
                self._handle_rate_limit(e)
                metrics["pull_requests"] = {
                    "open": len(list(self.gh_repo.get_pulls(state='open'))),
                    "merged": len(list(self.gh_repo.get_pulls(state='closed', sort='updated')))
                }

            # Get release information with retry logic
            try:
                releases = list(self.gh_repo.get_releases())
                metrics["releases"] = {
                    "total": len(releases),
                    "latest": releases[0].tag_name if releases else None,
                    "published_at": releases[0].published_at.isoformat() if releases else None
                }
            except RateLimitExceededException as e:
                self._handle_rate_limit(e)
                releases = list(self.gh_repo.get_releases())
                metrics["releases"] = {
                    "total": len(releases),
                    "latest": releases[0].tag_name if releases else None,
                    "published_at": releases[0].published_at.isoformat() if releases else None
                }

            return metrics

        except GithubException as e:
            if isinstance(e, RateLimitExceededException):
                raise
            print(f"Warning: Error fetching GitHub metrics: {str(e)}")
            return {}
