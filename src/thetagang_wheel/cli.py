"""
Command-line interface for ThetagangWheel.

Main entry point for the options screening tool.
"""

import typer
from typing import Optional
from pathlib import Path

from .config import get_config

app = typer.Typer(
    name="thetagang-wheel",
    help="Screen cash-secured puts based on r/thetagang sentiment analysis",
    add_completion=False
)


@app.command()
def screen(
    posts: int = typer.Option(25, "--posts", "-p", help="Number of Reddit posts to analyze"),
    min_oi: int = typer.Option(50, "--min-oi", help="Minimum open interest filter"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file (JSON/CSV)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """
    Screen cash-secured put options based on r/thetagang posts.
    
    This command will:
    1. Fetch top posts from r/thetagang
    2. Analyze sentiment and extract tickers
    3. Screen options for positive sentiment tickers
    4. Rank by weekly yield with safety filters
    """
    typer.echo("🔍 ThetagangWheel Options Screener")
    typer.echo("=" * 40)
    
    # Load configuration
    try:
        config = get_config()
        typer.echo(f"📊 Account size: ${config.account_size:,.0f}")
        typer.echo(f"📝 Analyzing {posts} posts from r/{config.subreddit_name}")
        typer.echo(f"🎯 Min open interest: {min_oi}")
        
    except Exception as e:
        typer.echo(f"❌ Configuration error: {e}", err=True)
        typer.echo("💡 Make sure your .env file is configured correctly", err=True)
        raise typer.Exit(1)
    
    # TODO: Implement the actual screening logic
    typer.echo("\n🚧 Screening logic not yet implemented")
    typer.echo("This is a stub implementation for Step 1")
    
    if output:
        typer.echo(f"📄 Output will be saved to: {output}")
    
    typer.echo("\n✅ CLI stub working correctly!")


@app.command()
def validate_config():
    """Validate configuration and API access."""
    typer.echo("🔧 Validating configuration...")
    
    try:
        config = get_config()
        typer.echo("✅ Configuration loaded successfully")
        
        # TODO: Test Reddit API connection
        typer.echo("🚧 Reddit API validation not yet implemented")
        
    except Exception as e:
        typer.echo(f"❌ Configuration error: {e}", err=True)
        raise typer.Exit(1)


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show version and exit")
):
    """ThetagangWheel - Screen cash-secured puts based on r/thetagang sentiment."""
    if version:
        from . import __version__
        typer.echo(f"thetagang-wheel {__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    app()
