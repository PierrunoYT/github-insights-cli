"""
Tests for the visualizer module.
"""

import pytest
import json
from pathlib import Path
import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from visualizer import Visualizer

@pytest.fixture
def sample_processed_data():
    """Create sample processed data for testing."""
    return {
        "summary": {
            "total_commits": 100,
            "total_contributors": 3,
            "total_files": 4,
            "primary_language": ".py",
            "active_contributors": 3,
            "commit_frequency": {
                "daily": 2.5,
                "weekly": 17.5,
                "monthly": 75.0
            }
        },
        "commit_insights": {
            "frequency_trends": {
                "trend": "increasing",
                "average_commits_per_period": 33.3,
                "stability_score": 0.85
            },
            "contribution_patterns": {
                "distribution_type": "distributed",
                "contribution_concentration": 0.45
            },
            "commit_activity": {
                "2023-01": 30,
                "2023-02": 35,
                "2023-03": 35
            }
        },
        "contributor_insights": {
            "core_contributors": ["dev1", "dev2"],
            "contribution_distribution": {
                "dev1": 0.5,
                "dev2": 0.3,
                "dev3": 0.2
            },
            "expertise_areas": {
                "dev1": ["file1.py", "file2.py"],
                "dev2": ["file2.py", "file3.py"],
                "dev3": ["file3.py", "file4.py"]
            }
        },
        "code_insights": {
            "language_trends": {
                "language_shares": {
                    ".py": 0.75,
                    ".js": 0.25
                }
            },
            "file_size_distribution": {
                "average_size": 132.5,
                "size_distribution": {
                    "small": 1,
                    "medium": 2,
                    "large": 1
                }
            }
        },
        "recommendations": [
            {
                "type": "workflow",
                "priority": "high",
                "description": "Consider increasing commit frequency",
                "rationale": "Regular commits help track changes"
            },
            {
                "type": "code_quality",
                "priority": "medium",
                "description": "Consider refactoring large files",
                "rationale": "Smaller files are easier to maintain"
            }
        ]
    }

def test_generate_text_report(sample_processed_data):
    """Test text report generation."""
    visualizer = Visualizer()
    report = visualizer.generate_report(sample_processed_data, format="text")
    
    assert isinstance(report, str)
    assert "GitHub Repository Insights Report" in report
    assert "Summary" in report
    assert "Commit Activity" in report
    assert "Recommendations" in report
    assert str(sample_processed_data["summary"]["total_commits"]) in report
    assert str(sample_processed_data["summary"]["total_contributors"]) in report

def test_generate_json_report(sample_processed_data):
    """Test JSON report generation."""
    visualizer = Visualizer()
    report = visualizer.generate_report(sample_processed_data, format="json")
    
    # Verify it's valid JSON
    json_data = json.loads(report)
    assert isinstance(json_data, dict)
    assert json_data["summary"]["total_commits"] == sample_processed_data["summary"]["total_commits"]
    assert json_data["summary"]["total_contributors"] == sample_processed_data["summary"]["total_contributors"]

def test_generate_html_report(sample_processed_data):
    """Test HTML report generation."""
    visualizer = Visualizer()
    report = visualizer.generate_report(sample_processed_data, format="html")
    
    assert isinstance(report, str)
    assert "<!DOCTYPE html>" in report
    assert "<html>" in report
    assert "GitHub Repository Insights Report" in report
    assert str(sample_processed_data["summary"]["total_commits"]) in report
    assert "plotly" in report.lower()  # Should include plotly visualizations

def test_save_plots(sample_processed_data, tmp_path):
    """Test saving plots to files."""
    visualizer = Visualizer()
    visualizer.save_plots(sample_processed_data, str(tmp_path))
    
    # Check if plot files were created
    assert (tmp_path / "commit_trend.png").exists()
    assert (tmp_path / "contributor_distribution.png").exists()
    assert (tmp_path / "language_distribution.png").exists()

def test_invalid_format():
    """Test handling of invalid report format."""
    visualizer = Visualizer()
    report = visualizer.generate_report({}, format="invalid")
    
    # Should default to text format
    assert isinstance(report, str)
    assert "GitHub Repository Insights Report" in report

def test_empty_data():
    """Test visualization with empty data."""
    visualizer = Visualizer()
    empty_data = {
        "summary": {
            "total_commits": 0,
            "total_contributors": 0,
            "total_files": 0,
            "primary_language": "unknown",
            "active_contributors": 0,
            "commit_frequency": {"daily": 0, "weekly": 0, "monthly": 0}
        },
        "commit_insights": {
            "frequency_trends": {},
            "contribution_patterns": {},
            "commit_activity": {}
        },
        "contributor_insights": {
            "core_contributors": [],
            "contribution_distribution": {},
            "expertise_areas": {}
        },
        "code_insights": {
            "language_trends": {"language_shares": {}},
            "file_size_distribution": {"average_size": 0, "size_distribution": {}}
        },
        "recommendations": []
    }
    
    # Test all formats with empty data
    text_report = visualizer.generate_report(empty_data, format="text")
    json_report = visualizer.generate_report(empty_data, format="json")
    html_report = visualizer.generate_report(empty_data, format="html")
    
    assert isinstance(text_report, str)
    assert isinstance(json_report, str)
    assert isinstance(html_report, str)
    assert "0" in text_report  # Should show zero values
    assert json.loads(json_report)  # Should be valid JSON
    assert "<!DOCTYPE html>" in html_report  # Should be valid HTML

def test_html_report_components(sample_processed_data):
    """Test specific components of HTML report."""
    visualizer = Visualizer()
    report = visualizer.generate_report(sample_processed_data, format="html")
    
    # Check for main sections
    assert "<div class=\"section\">" in report
    assert "<div class=\"stat-grid\">" in report
    assert "<div class=\"recommendation" in report
    
    # Check for visualization placeholders
    assert "Commit Activity" in report
    assert "Contributor Distribution" in report
    assert "Language Distribution" in report

def test_recommendations_html(sample_processed_data):
    """Test HTML formatting of recommendations."""
    visualizer = Visualizer()
    report = visualizer.generate_report(sample_processed_data, format="html")
    
    # Check recommendation styling
    for rec in sample_processed_data["recommendations"]:
        assert f"class=\"recommendation {rec['priority']}\"" in report
        assert rec["description"] in report
        assert rec["rationale"] in report
