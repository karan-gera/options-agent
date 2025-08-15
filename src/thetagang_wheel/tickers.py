"""
Ticker extraction and validation.

Extracts tickers from posts and validates against NASDAQ symbol masters.
"""

from typing import List, Set
from .models import RedditPost, TickerValidation


def extract_tickers(posts: List[RedditPost]) -> List[RedditPost]:
    """
    Extract stock tickers from Reddit posts.
    
    Args:
        posts: List of RedditPost objects
        
    Returns:
        List of RedditPost objects with tickers populated
    """
    # TODO: Implement ticker extraction (cashtags + ALL-CAPS)
    raise NotImplementedError("Ticker extraction not yet implemented")


def validate_tickers(tickers: Set[str]) -> List[TickerValidation]:
    """
    Validate tickers against official NASDAQ symbol masters.
    
    Args:
        tickers: Set of ticker symbols to validate
        
    Returns:
        List of TickerValidation objects
    """
    # TODO: Implement ticker validation against NASDAQ FTP sources
    raise NotImplementedError("Ticker validation not yet implemented")
