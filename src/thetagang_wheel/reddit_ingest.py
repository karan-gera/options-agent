"""
Reddit data ingestion for ThetagangWheel.

Fetches posts from r/thetagang using PRAW (Reddit API).
"""

from typing import List
from .models import RedditPost


def fetch_posts(subreddit: str, limit: int = 25) -> List[RedditPost]:
    """
    Fetch top posts from specified subreddit.
    
    Args:
        subreddit: Subreddit name (e.g., 'thetagang')
        limit: Maximum number of posts to fetch
        
    Returns:
        List of RedditPost objects
    """
    # TODO: Implement Reddit API integration using PRAW
    raise NotImplementedError("Reddit ingestion not yet implemented")
