"""
Data processor module for transforming and analyzing repository metrics.
"""

from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
import networkx as nx
from collections import defaultdict

class DataProcessor:
    def _analyze_commit_sizes(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the distribution of commit sizes.

        Args:
            stats: Raw commit statistics

        Returns:
            Dictionary containing commit size analysis
        """
        commit_sizes = []
        for commit in stats.get("commits", []):
            size = commit.get("insertions", 0) + commit.get("deletions", 0)
            commit_sizes.append(size)

        if not commit_sizes:
            return {"size_analysis": "insufficient_data"}

        df = pd.Series(commit_sizes)
        return {
            "distribution": {
                "small": len(df[df < 50]),  # Less than 50 lines
                "medium": len(df[(df >= 50) & (df < 200)]),  # 50-200 lines
                "large": len(df[(df >= 200) & (df < 1000)]),  # 200-1000 lines
                "very_large": len(df[df >= 1000])  # 1000+ lines
            },
            "statistics": {
                "mean": df.mean(),
                "median": df.median(),
                "std": df.std(),
                "max": df.max(),
                "min": df.min()
            }
        }

    def _analyze_collaboration_patterns(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns of collaboration between contributors.

        Args:
            details: Contributor details

        Returns:
            Dictionary containing collaboration analysis
        """
        # Create a graph of file co-modifications
        G = nx.Graph()
        file_authors = defaultdict(set)
        
        # Build file-author relationships
        for author, stats in details.items():
            for file in stats.get("files_touched", set()):
                file_authors[file].add(author)
                
        # Create edges between authors who modified the same files
        for file, authors in file_authors.items():
            for author1 in authors:
                for author2 in authors:
                    if author1 < author2:  # Avoid duplicate edges
                        if not G.has_edge(author1, author2):
                            G.add_edge(author1, author2, weight=1)
                        else:
                            G[author1][author2]["weight"] += 1

        # Calculate collaboration metrics
        if not G.nodes():
            return {"collaboration_analysis": "insufficient_data"}

        return {
            "collaboration_network": {
                "total_collaborations": G.number_of_edges(),
                "avg_collaborations_per_dev": 2 * G.number_of_edges() / G.number_of_nodes(),
                "most_collaborative": max(G.degree(weight="weight"), key=lambda x: x[1])[0],
                "isolated_developers": [n for n, d in G.degree() if d == 0]
            },
            "team_structure": {
                "clusters": list(nx.connected_components(G)),
                "centrality": {
                    node: round(cent, 3)
                    for node, cent in nx.betweenness_centrality(G, weight="weight").items()
                }
            }
        }

    def _analyze_code_organization(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code organization patterns.

        Args:
            stats: File statistics

        Returns:
            Dictionary containing code organization analysis
        """
        if not stats:
            return {"organization_analysis": "insufficient_data"}

        # Analyze directory structure
        dir_structure = defaultdict(int)
        file_types = defaultdict(int)
        depth_stats = []
        large_files = []
        
        for filepath, file_stats in stats.items():
            # Analyze directory depth
            parts = filepath.split('/')
            depth = len(parts) - 1
            depth_stats.append(depth)
            
            # Count files per directory
            if depth > 0:
                dir_structure['/'.join(parts[:-1])] += 1
            
            # Analyze file types
            ext = filepath.split('.')[-1] if '.' in filepath else 'no_extension'
            file_types[ext] += 1
            
            # Track large files
            if file_stats.get("size", 0) > 1000:  # More than 1000 lines
                large_files.append({
                    "path": filepath,
                    "size": file_stats["size"]
                })

        depth_series = pd.Series(depth_stats)
        
        return {
            "directory_structure": {
                "total_directories": len(dir_structure),
                "max_depth": depth_series.max(),
                "avg_depth": depth_series.mean(),
                "files_per_directory": {
                    dir_path: count
                    for dir_path, count in sorted(
                        dir_structure.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10]  # Top 10 directories
                }
            },
            "file_organization": {
                "file_types": dict(file_types),
                "large_files": sorted(
                    large_files,
                    key=lambda x: x["size"],
                    reverse=True
                )[:10]  # Top 10 largest files
            },
            "recommendations": self._generate_organization_recommendations(
                depth_series,
                dir_structure,
                large_files
            )
        }

    def _generate_organization_recommendations(
        self,
        depth_series: pd.Series,
        dir_structure: Dict[str, int],
        large_files: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate recommendations for code organization.

        Args:
            depth_series: Series of directory depths
            dir_structure: Directory structure data
            large_files: List of large files

        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check directory depth
        if depth_series.max() > 5:
            recommendations.append({
                "type": "directory_structure",
                "priority": "medium",
                "message": "Consider flattening deep directory structures (>5 levels)"
            })
        
        # Check directory size
        large_dirs = [
            dir_path for dir_path, count in dir_structure.items()
            if count > 20  # More than 20 files
        ]
        if large_dirs:
            recommendations.append({
                "type": "directory_size",
                "priority": "medium",
                "message": f"Consider splitting large directories: {', '.join(large_dirs)}"
            })
        
        # Check file sizes
        if len(large_files) > 0:
            recommendations.append({
                "type": "file_size",
                "priority": "high",
                "message": "Consider refactoring large files (>1000 lines)"
            })
        
        return recommendations
