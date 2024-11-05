"""
Data processor module for transforming and analyzing repository metrics.
"""

from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

class DataProcessor:
    """Processes and analyzes repository data to generate insights."""

    def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw repository data and generate insights.

        Args:
            raw_data: Dictionary containing raw repository metrics

        Returns:
            Dictionary containing processed metrics and insights
        """
        return {
            "summary": self._generate_summary(raw_data),
            "commit_insights": self._analyze_commit_patterns(raw_data),
            "contributor_insights": self._analyze_contributor_patterns(raw_data),
            "code_insights": self._analyze_code_patterns(raw_data),
            "recommendations": self._generate_recommendations(raw_data)
        }

    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a high-level summary of repository metrics.

        Args:
            data: Raw repository data

        Returns:
            Dictionary containing summary metrics
        """
        commit_stats = data["commit_stats"]
        contributor_stats = data["contributor_stats"]
        code_stats = data["code_stats"]

        return {
            "total_commits": commit_stats["total_commits"],
            "total_contributors": contributor_stats["total_contributors"],
            "total_files": code_stats["total_files"],
            "commit_frequency": commit_stats["commit_frequency"],
            "active_contributors": self._count_active_contributors(contributor_stats),
            "primary_language": self._get_primary_language(code_stats)
        }

    def _analyze_commit_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze commit patterns and trends.

        Args:
            data: Raw repository data

        Returns:
            Dictionary containing commit pattern insights
        """
        commit_stats = data["commit_stats"]
        
        return {
            "frequency_trends": self._analyze_frequency_trends(commit_stats),
            "contribution_patterns": self._analyze_contribution_patterns(commit_stats),
            "peak_activity_times": self._identify_peak_activity(commit_stats),
            "commit_size_distribution": self._analyze_commit_sizes(commit_stats)
        }

    def _analyze_contributor_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze contributor behavior and patterns.

        Args:
            data: Raw repository data

        Returns:
            Dictionary containing contributor pattern insights
        """
        contributor_stats = data["contributor_stats"]
        contributor_details = contributor_stats["contributor_details"]

        return {
            "core_contributors": self._identify_core_contributors(contributor_details),
            "contribution_distribution": self._analyze_contribution_distribution(contributor_details),
            "expertise_areas": self._analyze_expertise_areas(contributor_details),
            "collaboration_patterns": self._analyze_collaboration_patterns(contributor_details)
        }

    def _analyze_code_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code patterns and structure.

        Args:
            data: Raw repository data

        Returns:
            Dictionary containing code pattern insights
        """
        code_stats = data["code_stats"]
        file_stats = code_stats["file_stats"]

        return {
            "language_trends": self._analyze_language_trends(code_stats),
            "file_size_distribution": self._analyze_file_sizes(file_stats),
            "code_organization": self._analyze_code_organization(file_stats),
            "complexity_indicators": self._analyze_complexity(file_stats)
        }

    def _generate_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis.

        Args:
            data: Raw repository data

        Returns:
            List of recommendations with priorities
        """
        recommendations = []
        
        # Analyze commit frequency
        commit_freq = data["commit_stats"]["commit_frequency"]
        if commit_freq["daily"] < 0.5:  # Less than 1 commit every 2 days
            recommendations.append({
                "type": "workflow",
                "priority": "high",
                "description": "Consider increasing commit frequency for better version control",
                "rationale": "Regular commits help track changes and reduce merge conflicts"
            })

        # Analyze contributor distribution
        contributor_stats = data["contributor_stats"]
        if contributor_stats["total_contributors"] < 3:
            recommendations.append({
                "type": "collaboration",
                "priority": "medium",
                "description": "Consider expanding the contributor base",
                "rationale": "More contributors can bring diverse perspectives and skills"
            })

        # Analyze code complexity
        code_stats = data["code_stats"]
        large_files = sum(1 for stats in code_stats["file_stats"].values() 
                         if stats["size"] > 1000)  # Files larger than 1000 lines
        if large_files > 0:
            recommendations.append({
                "type": "code_quality",
                "priority": "medium",
                "description": f"Consider refactoring {large_files} large files",
                "rationale": "Smaller files are easier to maintain and understand"
            })

        return recommendations

    def _count_active_contributors(self, stats: Dict[str, Any]) -> int:
        """Count contributors with recent activity."""
        # Consider a contributor active if they have made at least 1 commit
        return sum(1 for details in stats["contributor_details"].values()
                  if details["commits"] > 0)

    def _get_primary_language(self, stats: Dict[str, Any]) -> str:
        """Determine the primary programming language used."""
        lang_dist = stats["language_distribution"]
        return max(lang_dist.items(), key=lambda x: x[1])[0] if lang_dist else "unknown"

    def _analyze_frequency_trends(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze commit frequency trends over time."""
        activity = stats.get("commit_activity", {})
        if not activity:
            return {"trend": "insufficient_data"}

        # Convert to pandas series for trend analysis
        series = pd.Series(activity)
        trend = "increasing" if series.is_monotonic_increasing else \
                "decreasing" if series.is_monotonic_decreasing else \
                "fluctuating"
        
        return {
            "trend": trend,
            "average_commits_per_period": series.mean(),
            "stability_score": 1 - (series.std() / series.mean() if series.mean() != 0 else 0)
        }

    def _analyze_contribution_patterns(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in contribution behavior."""
        top_contributors = stats.get("top_contributors", {})
        total_commits = stats.get("total_commits", 0)

        if not top_contributors or total_commits == 0:
            return {"pattern": "insufficient_data"}

        # Calculate contribution concentration
        top_contribution_share = sum(top_contributors.values()) / total_commits

        return {
            "contribution_concentration": top_contribution_share,
            "distribution_type": "concentrated" if top_contribution_share > 0.8 else "distributed"
        }

    def _identify_peak_activity(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Identify peak activity periods."""
        activity = stats.get("commit_activity", {})
        if not activity:
            return {"peaks": "insufficient_data"}

        series = pd.Series(activity)
        peak_periods = series[series > series.mean() + series.std()]

        return {
            "peak_periods": peak_periods.to_dict(),
            "peak_intensity": float(peak_periods.mean() / series.mean() if series.mean() != 0 else 0)
        }

    def _analyze_commit_sizes(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the distribution of commit sizes."""
        # Implementation would analyze the insertions/deletions per commit
        return {"size_analysis": "not_implemented"}

    def _identify_core_contributors(self, details: Dict[str, Any]) -> List[str]:
        """Identify core contributors based on contribution patterns."""
        threshold = sum(d["commits"] for d in details.values()) * 0.1  # 10% of total commits
        return [author for author, stats in details.items()
                if stats["commits"] > threshold]

    def _analyze_contribution_distribution(self, details: Dict[str, Any]) -> Dict[str, float]:
        """Analyze the distribution of contributions among contributors."""
        total_commits = sum(d["commits"] for d in details.values())
        if total_commits == 0:
            return {}

        return {
            author: stats["commits"] / total_commits
            for author, stats in details.items()
        }

    def _analyze_expertise_areas(self, details: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze areas of expertise for each contributor."""
        expertise = {}
        for author, stats in details.items():
            # Analyze frequently touched files to determine expertise
            expertise[author] = list(stats["files_touched"])
        return expertise

    def _analyze_collaboration_patterns(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns of collaboration between contributors."""
        # Implementation would analyze file overlap between contributors
        return {"collaboration_analysis": "not_implemented"}

    def _analyze_language_trends(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze programming language usage trends."""
        lang_dist = stats["language_distribution"]
        total_files = sum(lang_dist.values())
        
        if total_files == 0:
            return {"trends": "insufficient_data"}

        return {
            "language_shares": {
                lang: count / total_files
                for lang, count in lang_dist.items()
            }
        }

    def _analyze_file_sizes(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the distribution of file sizes."""
        sizes = [s["size"] for s in stats.values()]
        if not sizes:
            return {"size_analysis": "insufficient_data"}

        return {
            "average_size": sum(sizes) / len(sizes),
            "size_distribution": {
                "small": sum(1 for s in sizes if s < 100),
                "medium": sum(1 for s in sizes if 100 <= s < 500),
                "large": sum(1 for s in sizes if s >= 500)
            }
        }

    def _analyze_code_organization(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code organization patterns."""
        # Implementation would analyze directory structure and file organization
        return {"organization_analysis": "not_implemented"}

    def _analyze_complexity(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code complexity indicators."""
        # Implementation would calculate complexity metrics
        return {"complexity_analysis": "not_implemented"}
