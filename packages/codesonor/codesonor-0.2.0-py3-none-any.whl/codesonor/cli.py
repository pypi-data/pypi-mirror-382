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
from .config import Config
from .__init__ import __version__


console = Console()
config_manager = Config()


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
@click.option('--github-token', help='GitHub Personal Access Token (overrides stored config)')
@click.option('--gemini-key', help='Gemini API key for AI analysis (overrides stored config)')
def analyze(repo_url, no_ai, max_files, json_output, github_token, gemini_key):
    """
    Analyze a GitHub repository.
    
    REPO_URL: The URL of the GitHub repository to analyze
    
    Example: codesonor analyze https://github.com/pallets/flask
    """
    try:
        # Get API keys (priority: CLI option > config file > environment)
        if not github_token:
            github_token = config_manager.get_github_token()
        
        if not gemini_key:
            gemini_key = config_manager.get_gemini_key()
        
        # Check for required keys
        if not github_token:
            console.print("[yellow]⚠ GitHub token not configured. You may hit rate limits.[/yellow]")
            console.print("[yellow]Run 'codesonor setup' to configure your API keys.[/yellow]\n")
        
        if not no_ai and not gemini_key:
            console.print("[yellow]⚠ Gemini API key not configured. AI analysis will be skipped.[/yellow]")
            console.print("[yellow]Run 'codesonor setup' to configure your API keys.[/yellow]\n")
        
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
@click.option('--github-token', help='GitHub Personal Access Token (overrides stored config)')
def summary(repo_url, github_token):
    """
    Get a quick summary of a repository (no AI analysis).
    
    REPO_URL: The URL of the GitHub repository
    
    Example: codesonor summary https://github.com/pallets/flask
    """
    try:
        # Get GitHub token from config if not provided
        if not github_token:
            github_token = config_manager.get_github_token()
        
        if not github_token:
            console.print("[yellow]⚠ GitHub token not configured. You may hit rate limits.[/yellow]")
            console.print("[yellow]Run 'codesonor setup' to configure your API keys.[/yellow]\n")
        
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


@cli.command()
def setup():
    """
    Interactive setup wizard for API keys.
    
    Configure your GitHub and Gemini API keys once - they'll be saved for future use.
    """
    console.print("[bold cyan]🔧 CodeSonor Setup Wizard[/bold cyan]\n")
    
    # Check current status
    status = config_manager.get_config_status()
    
    console.print("[bold]Current Configuration:[/bold]")
    
    # GitHub Token status
    if status['github_token']['set']:
        source = status['github_token']['source']
        console.print(f"  GitHub Token: ✅ Configured (from {source})")
    else:
        console.print("  GitHub Token: ❌ Not configured")
    
    # Gemini Key status
    if status['gemini_key']['set']:
        source = status['gemini_key']['source']
        console.print(f"  Gemini API Key: ✅ Configured (from {source})")
    else:
        console.print("  Gemini API Key: ❌ Not configured")
    
    console.print(f"\n[dim]Config file: {status['config_file']}[/dim]\n")
    
    # Ask if user wants to configure
    if status['github_token']['set'] and status['gemini_key']['set']:
        console.print("[green]✓ All API keys are configured![/green]\n")
        reconfigure = click.confirm("Do you want to update your keys?", default=False)
        if not reconfigure:
            return
    
    console.print("[bold yellow]Let's configure your API keys:[/bold yellow]\n")
    
    # GitHub Token setup
    console.print("[bold]1. GitHub Personal Access Token[/bold] (Optional, but recommended)")
    console.print("   [dim]Without this, you may hit GitHub's rate limits[/dim]")
    console.print("   • Visit: [cyan]https://github.com/settings/tokens[/cyan]")
    console.print("   • Click 'Generate new token (classic)'")
    console.print("   • Select scope: [yellow]public_repo[/yellow]")
    console.print("   • Copy the token\n")
    
    github_token = click.prompt(
        "Enter your GitHub token (or press Enter to skip)",
        default="",
        hide_input=True,
        show_default=False
    )
    
    # Gemini API Key setup
    console.print("\n[bold]2. Google Gemini API Key[/bold] (Required for AI analysis)")
    console.print("   [dim]This enables AI-powered code summaries[/dim]")
    console.print("   • Visit: [cyan]https://aistudio.google.com/app/apikey[/cyan]")
    console.print("   • Click 'Create API key'")
    console.print("   • Copy the key\n")
    
    gemini_key = click.prompt(
        "Enter your Gemini API key (or press Enter to skip)",
        default="",
        hide_input=True,
        show_default=False
    )
    
    # Save configuration
    if github_token or gemini_key:
        config_manager.save_config(
            github_token=github_token if github_token else None,
            gemini_key=gemini_key if gemini_key else None
        )
        
        console.print("\n[bold green]✓ Configuration saved successfully![/bold green]")
        console.print(f"[dim]Keys stored in: {status['config_file']}[/dim]\n")
        
        if github_token:
            console.print("  ✓ GitHub token configured")
        if gemini_key:
            console.print("  ✓ Gemini API key configured")
        
        console.print("\n[bold cyan]You're all set![/bold cyan]")
        console.print("Try it out: [yellow]codesonor analyze https://github.com/pallets/flask[/yellow]\n")
    else:
        console.print("\n[yellow]No keys entered. Run 'codesonor setup' again when ready.[/yellow]\n")


@cli.command()
def config():
    """
    Show current configuration status.
    """
    status = config_manager.get_config_status()
    
    console.print("[bold cyan]📋 CodeSonor Configuration[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("API Key", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Source", style="yellow")
    
    # GitHub Token
    github_status = "✅ Configured" if status['github_token']['set'] else "❌ Not set"
    github_source = status['github_token']['source'] or "-"
    table.add_row("GitHub Token", github_status, github_source)
    
    # Gemini Key
    gemini_status = "✅ Configured" if status['gemini_key']['set'] else "❌ Not set"
    gemini_source = status['gemini_key']['source'] or "-"
    table.add_row("Gemini API Key", gemini_status, gemini_source)
    
    console.print(table)
    console.print(f"\n[dim]Config file: {status['config_file']}[/dim]")
    
    if not status['github_token']['set'] or not status['gemini_key']['set']:
        console.print("\n[yellow]💡 Run 'codesonor setup' to configure missing keys[/yellow]\n")


@cli.command()
def reset():
    """
    Clear stored API keys from configuration.
    """
    if click.confirm("Are you sure you want to clear all stored API keys?", default=False):
        config_manager.clear_config()
        console.print("[green]✓ Configuration cleared successfully[/green]")
        console.print("\n[dim]Run 'codesonor setup' to reconfigure[/dim]\n")
    else:
        console.print("[yellow]Cancelled[/yellow]\n")


if __name__ == '__main__':
    cli()

