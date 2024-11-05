"""
Command-line interface for GitHub Insights CLI.
Handles user input and coordinates analysis workflow.
"""

import click
from rich.console import Console
from rich.progress import Progress
from typing import Optional, List
from pathlib import Path

from repo_analyzer import RepoAnalyzer
from data_processor import DataProcessor
from visualizer import Visualizer

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def main():
    """GitHub Insights CLI - Analyze your Git repositories with powerful insights."""
    pass

@main.command()
@click.argument('url')
@click.argument('target_path', type=click.Path(exists=False))
def clone(url: str, target_path: str):
    """Clone a Git repository and analyze it.
    
    URL: Git repository URL to clone
    TARGET_PATH: Local path to clone into
    """
    try:
        target = Path(target_path)
        if target.exists():
            console.print(f"[bold red]Error:[/] Target path already exists: {target_path}")
            raise click.Abort()

        with Progress() as progress:
            task = progress.add_task("[green]Cloning repository...", total=100)
            
            # Clone and analyze
            analyzer = RepoAnalyzer.clone(url, target_path)
            progress.update(task, advance=50)
            
            processor = DataProcessor()
            visualizer = Visualizer()
            
            raw_data = analyzer.analyze()
            progress.update(task, advance=25)
            
            processed_data = processor.process(raw_data)
            report = visualizer.generate_report(processed_data)
            progress.update(task, advance=25)

        console.print("\n[bold green]Repository cloned and analyzed successfully![/]")
        console.print(f"[blue]Location:[/] {target_path}")
        console.print("\n[bold]Analysis Results:[/]")
        console.print(report)

    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise click.Abort()

@main.command()
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--since', '-s', help='Analysis start date (YYYY-MM-DD)')
@click.option('--until', '-u', help='Analysis end date (YYYY-MM-DD)')
@click.option('--output', '-o', help='Output format (text/json/html)', default='text')
def analyze(repo_path: str, since: Optional[str], until: Optional[str], output: str):
    """Analyze a Git repository and generate insights."""
    try:
        with Progress() as progress:
            # Initialize components
            analyzer = RepoAnalyzer(repo_path)
            processor = DataProcessor()
            visualizer = Visualizer()

            # Analysis steps
            task1 = progress.add_task("[green]Analyzing repository...", total=100)
            raw_data = analyzer.analyze(since=since, until=until)
            progress.update(task1, advance=50)

            task2 = progress.add_task("[blue]Processing data...", total=100)
            processed_data = processor.process(raw_data)
            progress.update(task2, advance=50)

            task3 = progress.add_task("[yellow]Generating report...", total=100)
            report = visualizer.generate_report(processed_data, format=output)
            progress.update(task3, advance=50)

        # Display results
        console.print("\n[bold green]Analysis Complete![/]")
        console.print(report)

    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise click.Abort()

@main.command()
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--since', '-s', help='Analysis start date (YYYY-MM-DD)')
@click.option('--until', '-u', help='Analysis end date (YYYY-MM-DD)')
@click.option('--output', '-o', help='Output format (text/json/html)', default='text')
def contributions(repo_path: str, since: Optional[str], until: Optional[str], output: str):
    """Generate detailed contribution insights for the repository."""
    try:
        with Progress() as progress:
            task = progress.add_task("[green]Analyzing contributions...", total=100)
            
            analyzer = RepoAnalyzer(repo_path)
            processor = DataProcessor()
            visualizer = Visualizer()
            
            # Get raw data with focus on contributions
            raw_data = analyzer.analyze(since=since, until=until)
            progress.update(task, advance=40)
            
            # Process with focus on contribution metrics
            processed_data = processor.process(raw_data)
            contribution_data = {
                "contributor_stats": processed_data.get("contributor_stats", {}),
                "commit_patterns": processed_data.get("commit_patterns", {}),
                "collaboration_insights": processed_data.get("collaboration_insights", {})
            }
            progress.update(task, advance=30)
            
            # Generate contribution-focused report
            report = visualizer.generate_contribution_report(contribution_data, format=output)
            progress.update(task, advance=30)

        console.print("\n[bold green]Contribution Analysis Complete![/]")
        console.print(report)

    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise click.Abort()

@main.command()
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--threshold', '-t', type=int, default=10,
              help='Complexity threshold for highlighting complex functions')
@click.option('--output', '-o', help='Output format (text/json/html)', default='text')
def complexity(repo_path: str, threshold: int, output: str):
    """Analyze code complexity metrics of the repository."""
    try:
        with Progress() as progress:
            task = progress.add_task("[green]Analyzing code complexity...", total=100)
            
            analyzer = RepoAnalyzer(repo_path)
            raw_data = analyzer.analyze()
            progress.update(task, advance=50)
            
            # Extract complexity metrics
            code_stats = raw_data.get("code_stats", {})
            complexity_data = {
                "complexity_metrics": code_stats.get("complexity_metrics", {}),
                "file_stats": {
                    path: stats for path, stats in code_stats.get("file_stats", {}).items()
                    if path.endswith('.py')  # Only include Python files
                }
            }
            
            # Generate report
            visualizer = Visualizer()
            report = visualizer.generate_complexity_report(complexity_data, threshold, format=output)
            progress.update(task, advance=50)

        console.print("\n[bold green]Complexity Analysis Complete![/]")
        console.print(report)

    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise click.Abort()

@main.command()
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output-dir', '-o', type=click.Path(), default='reports',
              help='Directory to save visualization files')
def export_viz(repo_path: str, output_dir: str):
    """Export repository visualizations to files."""
    try:
        with Progress() as progress:
            task = progress.add_task("[green]Generating visualizations...", total=100)
            
            analyzer = RepoAnalyzer(repo_path)
            processor = DataProcessor()
            visualizer = Visualizer()
            
            raw_data = analyzer.analyze()
            progress.update(task, advance=40)
            
            processed_data = processor.process(raw_data)
            progress.update(task, advance=30)
            
            visualizer.save_plots(processed_data, output_dir)
            progress.update(task, advance=30)

        console.print(f"\n[bold green]Visualizations exported to {output_dir}![/]")

    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise click.Abort()

@main.command()
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--metric', '-m', help='Specific metric to track', multiple=True)
def watch(repo_path: str, metric: List[str]):
    """Watch repository metrics in real-time."""
    try:
        console.print("[yellow]Starting repository watch...[/]")
        analyzer = RepoAnalyzer(repo_path)
        analyzer.watch(metrics=metric)
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise click.Abort()

if __name__ == '__main__':
    main()
