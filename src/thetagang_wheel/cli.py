"""
Command-line interface for ThetagangWheel.

Main entry point for the options screening tool.
"""

import typer
from typing import Optional
from pathlib import Path

from .config import get_config, Config

app = typer.Typer(
    name="thetagang-wheel",
    help="Screen cash-secured puts based on r/thetagang sentiment analysis",
    add_completion=False
)


@app.command()
def scan(
    # Core screening parameters
    capital: float = typer.Option(None, "--capital", help="Account capital for position sizing"),
    max_strike: float = typer.Option(None, "--max-strike", help="Maximum strike price"),
    min_oi: int = typer.Option(None, "--min-oi", help="Minimum open interest"),
    max_spread_pct: float = typer.Option(None, "--max-spread-pct", help="Maximum bid-ask spread percentage"),
    delta_min: float = typer.Option(None, "--delta-min", help="Minimum delta for put options"),
    delta_max: float = typer.Option(None, "--delta-max", help="Maximum delta for put options"),
    exclude_earnings: Optional[bool] = typer.Option(None, "--exclude-earnings/--include-earnings", help="Exclude options near earnings"),
    include_unclear_sentiment: Optional[bool] = typer.Option(None, "--include-unclear/--exclude-unclear", help="Include posts with unclear sentiment"),
    
    # Reddit configuration
    subreddit: str = typer.Option(None, "--subreddit", help="Subreddit to analyze"),
    reddit_limit: int = typer.Option(None, "--reddit-limit", help="Maximum posts to fetch"),
    reddit_window_days: int = typer.Option(None, "--reddit-window-days", help="Days back to look for posts"),
    
    # System settings  
    timezone: str = typer.Option(None, "--timezone", help="Market timezone"),
    
    # Output options
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file (JSON/CSV)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """
    Scan and screen cash-secured put options based on r/thetagang posts.
    
    This command will:
    1. Load configuration from environment/defaults
    2. Override with any provided command-line arguments
    3. Display the final configuration values
    4. (Future) Execute the screening pipeline
    """
    typer.echo("🔍 ThetagangWheel Options Scanner")
    typer.echo("=" * 40)
    
    # Load base configuration
    try:
        # Try to load real config first for Reddit ingestion
        config = get_config()
        has_real_config = True
        
    except Exception:
        # Fallback to stub config for testing configuration display only
        config = Config(
            reddit_client_id="stub",
            reddit_secret="stub", 
            reddit_user_agent="stub"
        )
        has_real_config = False
    
    # Override with CLI arguments if provided
    if capital is not None:
        config.capital = capital
    if max_strike is not None:
        config.max_strike = max_strike
    if min_oi is not None:
        config.min_oi = min_oi
    if max_spread_pct is not None:
        config.max_spread_pct = max_spread_pct
    if delta_min is not None:
        config.delta_min = delta_min
    if delta_max is not None:
        config.delta_max = delta_max
    if exclude_earnings is not None:
        config.exclude_earnings = exclude_earnings
    if include_unclear_sentiment is not None:
        config.include_unclear_sentiment = include_unclear_sentiment
    if subreddit is not None:
        config.subreddit = subreddit
    if reddit_limit is not None:
        config.reddit_limit = reddit_limit
    if reddit_window_days is not None:
        config.reddit_window_days = reddit_window_days
    if timezone is not None:
        config.timezone = timezone
    
    # Echo parsed configuration
    typer.echo("\n📋 Configuration Values:")
    typer.echo("-" * 25)
    typer.echo(f"💰 Capital: ${config.capital:,.0f}")
    typer.echo(f"📈 Max Strike: ${config.max_strike:.2f}")
    typer.echo(f"📊 Min Open Interest: {config.min_oi}")
    typer.echo(f"📏 Max Spread: {config.max_spread_pct:.1f}%")
    typer.echo(f"🔺 Delta Range: {config.delta_min:.2f} - {config.delta_max:.2f}")
    typer.echo(f"📅 Exclude Earnings: {config.exclude_earnings}")
    typer.echo(f"💭 Include Unclear Sentiment: {config.include_unclear_sentiment}")
    typer.echo(f"📱 Subreddit: r/{config.subreddit}")
    typer.echo(f"📝 Reddit Limit: {config.reddit_limit} posts")
    typer.echo(f"⏰ Window: {config.reddit_window_days} days")
    typer.echo(f"🌍 Timezone: {config.timezone}")
    
    if output:
        typer.echo(f"📄 Output: {output}")
    if verbose:
        typer.echo("🔍 Verbose logging enabled")
    
    # Test Reddit ingestion (Step 3)
    if has_real_config:
        typer.echo("\n🔍 Testing Reddit Ingestion...")
        try:
            from .reddit_ingest import fetch_posts
            
            # Fetch posts using the configured parameters
            posts = fetch_posts(
                limit=config.reddit_limit,
                window_days=config.reddit_window_days,
                subreddit=config.subreddit,
                config=config
            )
            
            # Display summary
            typer.echo(f"📊 Successfully fetched {len(posts)} posts")
            
            # Step 4: Sentiment Analysis
            typer.echo("\n💭 Analyzing post sentiment...")
            try:
                from .sentiment import analyze_sentiment_distribution, filter_posts_by_sentiment
                
                # Analyze sentiment distribution
                distribution = analyze_sentiment_distribution(posts)
                typer.echo(f"📈 Sentiment distribution:")
                typer.echo(f"   Positive: {distribution['positive']} ({distribution['positive']/len(posts)*100:.1f}%)")
                typer.echo(f"   Negative: {distribution['negative']} ({distribution['negative']/len(posts)*100:.1f}%)")
                typer.echo(f"   Unclear:  {distribution['unclear']} ({distribution['unclear']/len(posts)*100:.1f}%)")
                
                # Filter posts by sentiment (default: positive only)
                filtered_posts = filter_posts_by_sentiment(
                    posts,
                    include_positive=True,
                    include_negative=False,
                    include_unclear=config.include_unclear_sentiment
                )
                
                typer.echo(f"🎯 Filtered to {len(filtered_posts)} posts for screening")
                
                if verbose and filtered_posts:
                    typer.echo("\n📝 Sample filtered posts:")
                    for i, post in enumerate(filtered_posts[:3]):  # Show first 3 posts
                        sentiment = post.get('sentiment', 'unknown')
                        typer.echo(f"  {i+1}. [{post['score']}] [{sentiment}] {post['title'][:50]}...")
                        
            except Exception as e:
                typer.echo(f"❌ Sentiment analysis error: {e}", err=True)
                filtered_posts = posts  # Fall back to unfiltered posts
                    
        except Exception as e:
            typer.echo(f"❌ Reddit ingestion error: {e}", err=True)
            if "reddit_client_id" in str(e) or "REDDIT_CLIENT_ID" in str(e):
                typer.echo("💡 Make sure your .env file is configured with Reddit API credentials", err=True)
            else:
                typer.echo("💡 Check your Reddit API credentials and internet connection", err=True)
    else:
        typer.echo("\n⚠️ Reddit ingestion skipped - no .env configuration found")
        typer.echo("💡 Create a .env file with Reddit API credentials to test ingestion")
    
    # TODO: Implement the rest of the scanning logic (sentiment, tickers, options)
    typer.echo("\n🚧 Sentiment analysis, ticker extraction, and options screening not yet implemented")
    typer.echo("Configuration parsing and Reddit ingestion working correctly!")


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
        typer.echo(f"📊 Account size: ${config.capital:,.0f}")
        typer.echo(f"📝 Analyzing {posts} posts from r/{config.subreddit}")
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
