"""Command-line interface for CodeSonor."""

import click
import json
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from .analyzer import RepositoryAnalyzer
from .__init__ import __version__


console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="CodeSonor")
def cli():
    """
    CodeSonor - AI-Powered GitHub Repository Analyzer
    
    Analyze any public GitHub repository and get instant insights including
    language distribution, file statistics, and AI-generated code summaries.
    """
    pass


@cli.command()
@click.argument('repo_url')
@click.option('--no-ai', is_flag=True, help='Skip AI analysis (faster)')
@click.option('--max-files', default=500, help='Maximum files to analyze (default: 500)')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
@click.option('--github-token', envvar='GITHUB_TOKEN', help='GitHub Personal Access Token')
@click.option('--gemini-key', envvar='GEMINI_API_KEY', help='Gemini API key for AI analysis')
def analyze(repo_url, no_ai, max_files, json_output, github_token, gemini_key):
    """
    Analyze a GitHub repository.
    
    REPO_URL: The URL of the GitHub repository to analyze
    
    Example: codesonor analyze https://github.com/pallets/flask
    """
    try:
        # Check for required environment variables
        if not github_token:
            console.print("[yellow]Warning: GITHUB_TOKEN not set. You may hit rate limits.[/yellow]")
            console.print("[yellow]Set it with: export GITHUB_TOKEN=your_token_here[/yellow]\n")
        
        if not no_ai and not gemini_key:
            console.print("[yellow]Warning: GEMINI_API_KEY not set. AI analysis will be skipped.[/yellow]")
            console.print("[yellow]Set it with: export GEMINI_API_KEY=your_key_here[/yellow]\n")
        
        # Create analyzer
        analyzer = RepositoryAnalyzer(github_token, gemini_key)
        
        # Analyze with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task(description="Analyzing repository...", total=None)
            result = analyzer.analyze(repo_url, include_ai=not no_ai, max_files=max_files)
        
        # Output results
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            display_results(result)
        
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        sys.exit(1)
    except PermissionError as e:
        console.print(f"[red]Authentication Error:[/red] {e}", style="bold red")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}", style="bold red")
        sys.exit(1)


@cli.command()
@click.argument('repo_url')
@click.option('--github-token', envvar='GITHUB_TOKEN', help='GitHub Personal Access Token')
def summary(repo_url, github_token):
    """
    Get a quick summary of a repository (no AI analysis).
    
    REPO_URL: The URL of the GitHub repository
    
    Example: codesonor summary https://github.com/pallets/flask
    """
    try:
        analyzer = RepositoryAnalyzer(github_token)
        summary_text = analyzer.get_summary(repo_url)
        console.print(summary_text)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        sys.exit(1)


def display_results(result: dict):
    """Display analysis results in a beautiful format."""
    repo = result['repository']
    stats = result['statistics']
    
    # Repository Header
    console.print(f"\n[bold cyan]{'='*70}[/bold cyan]")
    console.print(f"[bold]Repository:[/bold] [green]{repo['name']}[/green] by [blue]{repo['owner']}[/blue]")
    console.print(f"[bold cyan]{'='*70}[/bold cyan]\n")
    
    # Basic Info
    console.print(f"[bold]Description:[/bold] {repo['description']}")
    console.print(f"[bold]URL:[/bold] {repo['url']}")
    console.print(f"[bold]Stars:[/bold] ⭐ {repo['stars']:,}  [bold]Forks:[/bold] 🔱 {repo['forks']:,}")
    console.print(f"[bold]Created:[/bold] {repo['created_at'][:10]}")
    console.print(f"[bold]Updated:[/bold] {repo['updated_at'][:10]}\n")
    
    # Statistics Table
    stats_table = Table(title="📊 Repository Statistics", show_header=False)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Total Files", f"{stats['total_files']:,}")
    stats_table.add_row("Primary Language", stats['primary_language'])
    
    console.print(stats_table)
    console.print()
    
    # Language Distribution Table
    if stats['language_distribution']:
        lang_table = Table(title="💻 Language Distribution", show_header=True)
        lang_table.add_column("Language", style="cyan")
        lang_table.add_column("Percentage", style="green", justify="right")
        lang_table.add_column("Bar", style="yellow")
        
        for lang, pct in stats['language_distribution'].items():
            bar = '█' * int(pct / 2)  # Scale to max 50 chars
            lang_table.add_row(lang, f"{pct:.2f}%", bar)
        
        console.print(lang_table)
        console.print()
    
    # AI Analysis
    if result['ai_analysis']:
        console.print("[bold magenta]🤖 AI-Powered Code Analysis[/bold magenta]\n")
        
        for i, analysis in enumerate(result['ai_analysis'], 1):
            console.print(f"[bold cyan]File {i}:[/bold cyan] [yellow]{analysis['file']}[/yellow]")
            console.print(f"[dim]{analysis['summary']}[/dim]\n")
    
    console.print(f"[bold cyan]{'='*70}[/bold cyan]\n")


if __name__ == '__main__':
    cli()
