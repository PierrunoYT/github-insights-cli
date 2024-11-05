"""
Visualizer module for generating reports and visualizations from repository insights.
"""

from typing import Dict, Any, List
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json
import pandas as pd
from datetime import datetime

class Visualizer:
    """Generates visual reports and charts from repository data."""

    def generate_report(self, data: Dict[str, Any], format: str = "text") -> str:
        """Generate a report in the specified format.

        Args:
            data: Processed repository data
            format: Output format (text/json/html)

        Returns:
            Formatted report string
        """
        # Ensure data has all required sections with default values
        data = self._ensure_data_structure(data)

        if format == "json":
            return self._generate_json_report(data)
        elif format == "html":
            return self._generate_html_report(data)
        else:
            return self._generate_text_report(data)

    def _ensure_data_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure data has all required sections with default values."""
        default_data = {
            "summary": {
                "total_commits": 0,
                "total_contributors": 0,
                "total_files": 0,
                "primary_language": "unknown",
                "active_contributors": 0,
                "commit_frequency": {"daily": 0, "weekly": 0, "monthly": 0}
            },
            "commit_insights": {
                "frequency_trends": {"trend": "insufficient_data"},
                "contribution_patterns": {
                    "distribution_type": "insufficient_data",
                    "contribution_concentration": 0
                },
                "commit_activity": {}
            },
            "contributor_insights": {
                "core_contributors": [],
                "contribution_distribution": {},
                "expertise_areas": {}
            },
            "code_insights": {
                "language_trends": {"language_shares": {}},
                "file_size_distribution": {
                    "average_size": 0,
                    "size_distribution": {"small": 0, "medium": 0, "large": 0}
                }
            },
            "recommendations": []
        }

        # Recursively merge data with default values
        return self._merge_dict(default_data, data)

    def _merge_dict(self, default: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries, using default values for missing keys."""
        result = default.copy()
        for key, value in data.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dict(result[key], value)
            else:
                result[key] = value
        return result

    def _generate_text_report(self, data: Dict[str, Any]) -> str:
        """Generate a text-based report.

        Args:
            data: Processed repository data

        Returns:
            Formatted text report
        """
        summary = data["summary"]
        commit_insights = data["commit_insights"]
        contributor_insights = data["contributor_insights"]
        recommendations = data["recommendations"]

        report = [
            "=== GitHub Repository Insights Report ===",
            "",
            "== Summary ==",
            f"Total Commits: {summary['total_commits']}",
            f"Total Contributors: {summary['total_contributors']}",
            f"Total Files: {summary['total_files']}",
            f"Primary Language: {summary['primary_language']}",
            f"Active Contributors: {summary['active_contributors']}",
            "",
            "== Commit Activity ==",
            f"Daily Commits: {summary['commit_frequency']['daily']:.2f}",
            f"Weekly Commits: {summary['commit_frequency']['weekly']:.2f}",
            f"Monthly Commits: {summary['commit_frequency']['monthly']:.2f}",
            "",
            "== Contribution Patterns ==",
            f"Pattern: {commit_insights['contribution_patterns']['distribution_type']}",
            f"Concentration: {commit_insights['contribution_patterns']['contribution_concentration']:.2%}",
            "",
            "== Core Contributors =="
        ]

        # Add core contributors if any
        if contributor_insights['core_contributors']:
            report.extend([f"- {contributor}" for contributor in contributor_insights['core_contributors']])
        else:
            report.append("No core contributors identified")

        # Add recommendations if any
        report.extend(["", "== Recommendations =="])
        if recommendations:
            for rec in recommendations:
                report.extend([
                    f"[{rec['priority'].upper()}] {rec['description']}",
                    f"  Rationale: {rec['rationale']}"
                ])
        else:
            report.append("No recommendations available")

        return "\n".join(report)

    def _generate_json_report(self, data: Dict[str, Any]) -> str:
        """Generate a JSON report.

        Args:
            data: Processed repository data

        Returns:
            JSON-formatted report string
        """
        return json.dumps(data, indent=2, default=str)

    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate an HTML report with interactive visualizations.

        Args:
            data: Processed repository data

        Returns:
            HTML-formatted report string
        """
        # Create visualizations
        commit_trend_fig = self._create_commit_trend_plot(data)
        contributor_dist_fig = self._create_contributor_distribution_plot(data)
        language_dist_fig = self._create_language_distribution_plot(data)

        # Generate recommendations HTML
        recommendations_html = self._generate_recommendations_html(data["recommendations"])

        # Create the complete HTML report
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>GitHub Repository Insights Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                h1, h2 {{
                    color: #333;
                }}
                .stat-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-box {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    text-align: center;
                }}
                .stat-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #007bff;
                }}
                .stat-label {{
                    color: #666;
                    margin-top: 5px;
                }}
                .recommendation {{
                    padding: 10px;
                    margin-bottom: 10px;
                    border-left: 4px solid;
                }}
                .high {{
                    border-color: #dc3545;
                    background-color: #fff5f5;
                }}
                .medium {{
                    border-color: #ffc107;
                    background-color: #fffbf0;
                }}
                .low {{
                    border-color: #28a745;
                    background-color: #f0fff4;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>GitHub Repository Insights Report</h1>
                
                <div class="section">
                    <h2>Summary</h2>
                    <div class="stat-grid">
                        <div class="stat-box">
                            <div class="stat-value">{data['summary']['total_commits']}</div>
                            <div class="stat-label">Total Commits</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{data['summary']['total_contributors']}</div>
                            <div class="stat-label">Contributors</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{data['summary']['total_files']}</div>
                            <div class="stat-label">Files</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{data['summary']['active_contributors']}</div>
                            <div class="stat-label">Active Contributors</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>Commit Activity</h2>
                    {commit_trend_fig.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>

                <div class="section">
                    <h2>Contributor Distribution</h2>
                    {contributor_dist_fig.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>

                <div class="section">
                    <h2>Language Distribution</h2>
                    {language_dist_fig.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>

                <div class="section">
                    <h2>Recommendations</h2>
                    {recommendations_html}
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _create_commit_trend_plot(self, data: Dict[str, Any]) -> go.Figure:
        """Create a commit trend visualization."""
        activity = data["commit_insights"].get("commit_activity", {})
        if not activity:
            fig = go.Figure()
            fig.add_annotation(
                text="No commit activity data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig

        df = pd.DataFrame(list(activity.items()), columns=['date', 'commits'])
        fig = px.line(df, x='date', y='commits', 
                     title='Commit Activity Over Time',
                     labels={'date': 'Date', 'commits': 'Number of Commits'})
        fig.update_layout(showlegend=False)
        return fig

    def _create_contributor_distribution_plot(self, data: Dict[str, Any]) -> go.Figure:
        """Create a contributor distribution visualization."""
        dist = data["contributor_insights"].get("contribution_distribution", {})
        if not dist:
            fig = go.Figure()
            fig.add_annotation(
                text="No contributor distribution data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig

        df = pd.DataFrame(list(dist.items()), columns=['contributor', 'share'])
        df = df.sort_values('share', ascending=True)
        
        fig = px.bar(df, x='share', y='contributor', orientation='h',
                    title='Contribution Distribution',
                    labels={'share': 'Share of Contributions', 'contributor': 'Contributor'})
        return fig

    def _create_language_distribution_plot(self, data: Dict[str, Any]) -> go.Figure:
        """Create a language distribution visualization."""
        lang_trends = data["code_insights"].get("language_trends", {})
        shares = lang_trends.get("language_shares", {})
        if not shares:
            fig = go.Figure()
            fig.add_annotation(
                text="No language distribution data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig

        df = pd.DataFrame(list(shares.items()), columns=['language', 'share'])
        fig = px.pie(df, values='share', names='language',
                     title='Language Distribution')
        return fig

    def generate_contribution_report(self, data: Dict[str, Any], format: str = "text") -> str:
        """Generate a contribution-focused report.
        
        Args:
            data: Processed contribution data
            format: Output format (text/json/html)
            
        Returns:
            Formatted report string
        """
        # Ensure data has required structure
        data = self._ensure_contribution_data_structure(data)
        
        if format == "json":
            return self._generate_json_report(data)
        elif format == "html":
            return self._generate_html_contribution_report(data)
        else:
            return self._generate_text_contribution_report(data)

    def _ensure_contribution_data_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure contribution data has all required sections."""
        default_data = {
            "contributor_stats": {
                "total_contributors": 0,
                "contributor_details": {},
                "active_contributors": 0
            },
            "commit_patterns": {
                "frequency": {"daily": 0, "weekly": 0, "monthly": 0},
                "distribution": {"type": "unknown", "concentration": 0}
            },
            "collaboration_insights": {
                "highlights": [],
                "team_dynamics": {},
                "review_patterns": {}
            }
        }
        return self._merge_dict(default_data, data)

    def _generate_text_contribution_report(self, data: Dict[str, Any]) -> str:
        """Generate a text-based contribution report."""
        lines = [
            "=== Repository Contribution Analysis ===\n",
            "== Overview ==",
            f"Total Contributors: {data['contributor_stats']['total_contributors']}",
            f"Active Contributors: {data['contributor_stats']['active_contributors']}",
            
            "\n== Contribution Patterns ==",
            f"Daily Commits: {data['commit_patterns']['frequency']['daily']:.2f}",
            f"Weekly Commits: {data['commit_patterns']['frequency']['weekly']:.2f}",
            f"Monthly Commits: {data['commit_patterns']['frequency']['monthly']:.2f}",
            f"Distribution Type: {data['commit_patterns']['distribution']['type']}",
            
            "\n== Top Contributors =="
        ]
        
        # Add top contributors
        contributor_details = data['contributor_stats']['contributor_details']
        sorted_contributors = sorted(
            contributor_details.items(),
            key=lambda x: x[1].get('commits', 0),
            reverse=True
        )[:5]
        
        for author, details in sorted_contributors:
            lines.extend([
                f"\n{author}:",
                f"  Commits: {details.get('commits', 0)}",
                f"  Lines Added: {details.get('insertions', 0)}",
                f"  Lines Removed: {details.get('deletions', 0)}",
                f"  Files Modified: {len(details.get('files_touched', set()))}"
            ])
        
        # Add collaboration insights
        if data['collaboration_insights']['highlights']:
            lines.extend([
                "\n== Collaboration Insights ==",
                *[f"- {insight}" for insight in data['collaboration_insights']['highlights']]
            ])
        
        return "\n".join(lines)

    def _generate_html_contribution_report(self, data: Dict[str, Any]) -> str:
        """Generate an HTML contribution report with visualizations."""
        # Create visualizations
        contributor_dist_fig = self._create_contributor_distribution_plot(data)
        commit_timeline_fig = self._create_commit_timeline_plot(data)
        
        # Generate HTML for top contributors
        top_contributors_html = self._generate_top_contributors_html(
            data['contributor_stats']['contributor_details']
        )
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Repository Contribution Analysis</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                .stat-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-box {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    text-align: center;
                }}
                .contributor-card {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Repository Contribution Analysis</h1>
                
                <div class="section">
                    <h2>Overview</h2>
                    <div class="stat-grid">
                        <div class="stat-box">
                            <h3>Total Contributors</h3>
                            <div>{data['contributor_stats']['total_contributors']}</div>
                        </div>
                        <div class="stat-box">
                            <h3>Active Contributors</h3>
                            <div>{data['contributor_stats']['active_contributors']}</div>
                        </div>
                        <div class="stat-box">
                            <h3>Daily Commits</h3>
                            <div>{data['commit_patterns']['frequency']['daily']:.2f}</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>Contribution Distribution</h2>
                    {contributor_dist_fig.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>

                <div class="section">
                    <h2>Commit Timeline</h2>
                    {commit_timeline_fig.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>

                <div class="section">
                    <h2>Top Contributors</h2>
                    {top_contributors_html}
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _generate_top_contributors_html(self, contributor_details: Dict[str, Any]) -> str:
        """Generate HTML for top contributors section."""
        sorted_contributors = sorted(
            contributor_details.items(),
            key=lambda x: x[1].get('commits', 0),
            reverse=True
        )[:5]
        
        html_parts = []
        for author, details in sorted_contributors:
            html_parts.append(f"""
                <div class="contributor-card">
                    <h3>{author}</h3>
                    <p>Commits: {details.get('commits', 0)}</p>
                    <p>Lines Added: {details.get('insertions', 0)}</p>
                    <p>Lines Removed: {details.get('deletions', 0)}</p>
                    <p>Files Modified: {len(details.get('files_touched', set()))}</p>
                </div>
            """)
        
        return "\n".join(html_parts)

    def _create_commit_timeline_plot(self, data: Dict[str, Any]) -> go.Figure:
        """Create a timeline plot of commit activity."""
        commit_patterns = data.get('commit_patterns', {})
        activity = commit_patterns.get('activity', {})
        
        if not activity:
            fig = go.Figure()
            fig.add_annotation(
                text="No commit activity data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig
        
        dates = list(activity.keys())
        commits = list(activity.values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=commits,
            mode='lines+markers',
            name='Commits'
        ))
        
        fig.update_layout(
            title='Commit Activity Timeline',
            xaxis_title='Date',
            yaxis_title='Number of Commits',
            showlegend=True
        )
        
        return fig

    def _generate_recommendations_html(self, recommendations: List[Dict[str, Any]]) -> str:
        """Generate HTML for recommendations section."""
        if not recommendations:
            return "<p>No recommendations available.</p>"

        html_parts = []
        for rec in recommendations:
            priority = rec.get('priority', 'low')
            html_parts.append(f"""
                <div class="recommendation {priority}">
                    <strong>{rec.get('description', 'No description')}</strong>
                    <p>{rec.get('rationale', 'No rationale provided')}</p>
                </div>
            """)
        return "\n".join(html_parts)

    def save_plots(self, data: Dict[str, Any], output_dir: str) -> None:
        """Save visualizations as static image files.

        Args:
            data: Processed repository data
            output_dir: Directory to save plots
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save commit trend
        plt.figure(figsize=(10, 6))
        activity = data["commit_insights"].get("commit_activity", {})
        if activity:
            df = pd.DataFrame(list(activity.items()), columns=['date', 'commits'])
            plt.plot(df['date'], df['commits'])
            plt.title('Commit Activity Over Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_path / 'commit_trend.png')
            plt.close()

        # Save contributor distribution
        plt.figure(figsize=(10, 6))
        dist = data["contributor_insights"].get("contribution_distribution", {})
        if dist:
            df = pd.DataFrame(list(dist.items()), columns=['contributor', 'share'])
            df = df.sort_values('share', ascending=True)
            plt.barh(df['contributor'], df['share'])
            plt.title('Contribution Distribution')
            plt.tight_layout()
            plt.savefig(output_path / 'contributor_distribution.png')
            plt.close()

        # Save language distribution
        plt.figure(figsize=(8, 8))
        lang_trends = data["code_insights"].get("language_trends", {})
        shares = lang_trends.get("language_shares", {})
        if shares:
            plt.pie(shares.values(), labels=shares.keys(), autopct='%1.1f%%')
            plt.title('Language Distribution')
            plt.savefig(output_path / 'language_distribution.png')
            plt.close()
