"""
Command-line interface for GitHub Insights CLI.
Handles user input and coordinates analysis workflow.
"""

import click
from rich.console import Console
from rich.progress import Progress
from typing import Optional, List

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
