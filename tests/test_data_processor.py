"""
Tests for the data processor module.
"""

import pytest
from datetime import datetime
import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processor import DataProcessor

@pytest.fixture
def sample_raw_data():
    """Create sample repository data for testing."""
    return {
        "commit_stats": {
            "total_commits": 100,
            "commit_frequency": {
                "daily": 2.5,
                "weekly": 17.5,
                "monthly": 75.0
            },
            "top_contributors": {
                "dev1": 50,
                "dev2": 30,
                "dev3": 20
            },
            "commit_activity": {
                "2023-01": 30,
                "2023-02": 35,
                "2023-03": 35
            }
        },
        "contributor_stats": {
            "total_contributors": 3,
            "contributor_details": {
                "dev1": {
                    "commits": 50,
                    "insertions": 1000,
                    "deletions": 500,
                    "files_touched": {"file1.py", "file2.py"}
                },
                "dev2": {
                    "commits": 30,
                    "insertions": 600,
                    "deletions": 300,
                    "files_touched": {"file2.py", "file3.py"}
                },
                "dev3": {
                    "commits": 20,
                    "insertions": 400,
                    "deletions": 200,
                    "files_touched": {"file3.py", "file4.py"}
                }
            }
        },
        "code_stats": {
            "total_files": 4,
            "file_stats": {
                "file1.py": {"size": 100, "lines": 80, "extension": ".py"},
                "file2.py": {"size": 150, "lines": 120, "extension": ".py"},
                "file3.py": {"size": 200, "lines": 160, "extension": ".py"},
                "file4.js": {"size": 80, "lines": 60, "extension": ".js"}
            },
            "language_distribution": {
                ".py": 3,
                ".js": 1
            }
        },
        "branch_stats": {
            "total_branches": 2,
            "active_branch": "main",
            "branch_details": {
                "main": {
                    "commit_count": 80,
                    "last_commit": datetime.now()
                },
                "feature": {
                    "commit_count": 20,
                    "last_commit": datetime.now()
                }
            }
        }
    }

def test_process_basic(sample_raw_data):
    """Test basic data processing."""
    processor = DataProcessor()
    processed_data = processor.process(sample_raw_data)
    
    assert "summary" in processed_data
    assert "commit_insights" in processed_data
    assert "contributor_insights" in processed_data
    assert "code_insights" in processed_data
    assert "recommendations" in processed_data

def test_generate_summary(sample_raw_data):
    """Test summary generation."""
    processor = DataProcessor()
    processed_data = processor.process(sample_raw_data)
    summary = processed_data["summary"]
    
    assert summary["total_commits"] == 100
    assert summary["total_contributors"] == 3
    assert summary["total_files"] == 4
    assert summary["primary_language"] == ".py"
    assert summary["active_contributors"] == 3

def test_analyze_commit_patterns(sample_raw_data):
    """Test commit pattern analysis."""
    processor = DataProcessor()
    processed_data = processor.process(sample_raw_data)
    commit_insights = processed_data["commit_insights"]
    
    assert "frequency_trends" in commit_insights
    assert "contribution_patterns" in commit_insights
    assert "peak_activity_times" in commit_insights

def test_analyze_contributor_patterns(sample_raw_data):
    """Test contributor pattern analysis."""
    processor = DataProcessor()
    processed_data = processor.process(sample_raw_data)
    contributor_insights = processed_data["contributor_insights"]
    
    assert "core_contributors" in contributor_insights
    assert "contribution_distribution" in contributor_insights
    assert "expertise_areas" in contributor_insights
    assert len(contributor_insights["core_contributors"]) > 0

def test_analyze_code_patterns(sample_raw_data):
    """Test code pattern analysis."""
    processor = DataProcessor()
    processed_data = processor.process(sample_raw_data)
    code_insights = processed_data["code_insights"]
    
    assert "language_trends" in code_insights
    assert "file_size_distribution" in code_insights
    assert "code_organization" in code_insights

def test_generate_recommendations(sample_raw_data):
    """Test recommendation generation."""
    processor = DataProcessor()
    processed_data = processor.process(sample_raw_data)
    recommendations = processed_data["recommendations"]
    
    assert isinstance(recommendations, list)
    assert all(isinstance(rec, dict) for rec in recommendations)
    assert all("priority" in rec for rec in recommendations)
    assert all("description" in rec for rec in recommendations)
    assert all("rationale" in rec for rec in recommendations)

def test_contribution_distribution(sample_raw_data):
    """Test contribution distribution analysis."""
    processor = DataProcessor()
    processed_data = processor.process(sample_raw_data)
    contributor_insights = processed_data["contributor_insights"]
    distribution = contributor_insights["contribution_distribution"]
    
    assert isinstance(distribution, dict)
    assert abs(sum(distribution.values()) - 1.0) < 0.01  # Should sum to approximately 1
    assert all(0 <= v <= 1 for v in distribution.values())

def test_language_trends(sample_raw_data):
    """Test language trend analysis."""
    processor = DataProcessor()
    processed_data = processor.process(sample_raw_data)
    code_insights = processed_data["code_insights"]
    language_trends = code_insights["language_trends"]
    
    assert "language_shares" in language_trends
    shares = language_trends["language_shares"]
    assert abs(sum(shares.values()) - 1.0) < 0.01  # Should sum to approximately 1

def test_empty_data():
    """Test processing with empty data."""
    processor = DataProcessor()
    empty_data = {
        "commit_stats": {"total_commits": 0, "commit_frequency": {"daily": 0, "weekly": 0, "monthly": 0},
                        "top_contributors": {}, "commit_activity": {}},
        "contributor_stats": {"total_contributors": 0, "contributor_details": {}},
        "code_stats": {"total_files": 0, "file_stats": {}, "language_distribution": {}},
        "branch_stats": {"total_branches": 0, "active_branch": "", "branch_details": {}}
    }
    
    processed_data = processor.process(empty_data)
    assert processed_data["summary"]["total_commits"] == 0
    assert processed_data["summary"]["total_contributors"] == 0
    assert len(processed_data["recommendations"]) > 0  # Should still provide recommendations

def test_file_size_analysis(sample_raw_data):
    """Test file size analysis."""
    processor = DataProcessor()
    processed_data = processor.process(sample_raw_data)
    code_insights = processed_data["code_insights"]
    file_sizes = code_insights["file_size_distribution"]
    
    assert isinstance(file_sizes, dict)
    assert "average_size" in file_sizes
    assert "size_distribution" in file_sizes
    assert all(size in file_sizes["size_distribution"] for size in ["small", "medium", "large"])
