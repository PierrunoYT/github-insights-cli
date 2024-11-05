"""
Tests for the repository analyzer module.
"""

import pytest
from pathlib import Path
from datetime import datetime
from git import Repo
import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repo_analyzer import RepoAnalyzer

@pytest.fixture
def sample_repo(tmp_path):
    """Create a temporary Git repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    repo = Repo.init(repo_path)
    
    # Create some sample files
    (repo_path / "file1.py").write_text("print('Hello, World!')")
    (repo_path / "file2.js").write_text("console.log('Hello, World!');")
    
    # Add files to git
    repo.index.add(["file1.py", "file2.js"])
    repo.index.commit("Initial commit")
    
    return repo_path

def test_repo_analyzer_initialization(sample_repo):
    """Test RepoAnalyzer initialization."""
    analyzer = RepoAnalyzer(str(sample_repo))
    assert analyzer.repo_path == Path(sample_repo)
    assert analyzer.repo.git_dir

def test_repo_analyzer_invalid_repo(tmp_path):
    """Test RepoAnalyzer with invalid repository."""
    with pytest.raises(ValueError):
        RepoAnalyzer(str(tmp_path))

def test_analyze_basic_metrics(sample_repo):
    """Test basic repository metrics analysis."""
    analyzer = RepoAnalyzer(str(sample_repo))
    metrics = analyzer.analyze()
    
    assert "commit_stats" in metrics
    assert "contributor_stats" in metrics
    assert "code_stats" in metrics
    assert "branch_stats" in metrics

def test_analyze_commit_stats(sample_repo):
    """Test commit statistics analysis."""
    analyzer = RepoAnalyzer(str(sample_repo))
    metrics = analyzer.analyze()
    commit_stats = metrics["commit_stats"]
    
    assert commit_stats["total_commits"] > 0
    assert "commit_frequency" in commit_stats
    assert "top_contributors" in commit_stats
    assert "commit_activity" in commit_stats

def test_analyze_code_stats(sample_repo):
    """Test code statistics analysis."""
    analyzer = RepoAnalyzer(str(sample_repo))
    metrics = analyzer.analyze()
    code_stats = metrics["code_stats"]
    
    assert code_stats["total_files"] == 2
    assert ".py" in code_stats["language_distribution"]
    assert ".js" in code_stats["language_distribution"]

def test_analyze_with_date_range(sample_repo):
    """Test analysis with date range filters."""
    analyzer = RepoAnalyzer(str(sample_repo))
    
    # Add another commit
    (sample_repo / "file3.txt").write_text("Hello")
    analyzer.repo.index.add(["file3.txt"])
    analyzer.repo.index.commit("Second commit")
    
    # Test with date range
    since_date = datetime.now().strftime("%Y-%m-%d")
    metrics = analyzer.analyze(since=since_date)
    
    assert metrics["commit_stats"]["total_commits"] > 0

def test_analyze_branches(sample_repo):
    """Test branch analysis."""
    analyzer = RepoAnalyzer(str(sample_repo))
    
    # Create a new branch
    repo = analyzer.repo
    new_branch = repo.create_head("feature-branch")
    new_branch.checkout()
    
    metrics = analyzer.analyze()
    branch_stats = metrics["branch_stats"]
    
    assert branch_stats["total_branches"] == 2
    assert "feature-branch" in [b for b in branch_stats["branch_details"]]

def test_analyze_contributors(sample_repo):
    """Test contributor analysis."""
    analyzer = RepoAnalyzer(str(sample_repo))
    metrics = analyzer.analyze()
    contributor_stats = metrics["contributor_stats"]
    
    assert contributor_stats["total_contributors"] > 0
    assert len(contributor_stats["contributor_details"]) > 0

def test_analyze_empty_repo(tmp_path):
    """Test analysis of empty repository."""
    repo_path = tmp_path / "empty_repo"
    repo_path.mkdir()
    Repo.init(repo_path)
    
    analyzer = RepoAnalyzer(str(repo_path))
    metrics = analyzer.analyze()
    
    assert metrics["commit_stats"]["total_commits"] == 0
    assert metrics["contributor_stats"]["total_contributors"] == 0
    assert metrics["code_stats"]["total_files"] == 0
