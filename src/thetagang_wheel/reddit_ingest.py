"""
Reddit data ingestion for ThetagangWheel.

Fetches posts from r/thetagang using PRAW (Reddit API).
"""

import praw
from datetime import datetime, timedelta
from typing import List, Dict, Set
from .config import Config

# In-memory cache for the current run
_posts_cache: Dict[str, List[Dict]] = {}


def _get_reddit_client(config: Config) -> praw.Reddit:
    """
    Create PRAW Reddit client from configuration.
    
    Args:
        config: Configuration object with Reddit credentials
        
    Returns:
        Configured PRAW Reddit instance
    """
    return praw.Reddit(
        client_id=config.reddit_client_id,
        client_secret=config.reddit_secret,
        user_agent=config.reddit_user_agent,
        read_only=True  # We only need read access for fetching posts
    )


def _post_to_dict(submission) -> Dict:
    """
    Convert PRAW submission to dictionary with required fields.
    
    Args:
        submission: PRAW submission object
        
    Returns:
        Dictionary with post data
    """
    return {
        "id": submission.id,
        "title": submission.title,
        "selftext": submission.selftext,
        "score": submission.score,
        "created_utc": datetime.fromtimestamp(submission.created_utc),
        "permalink": submission.permalink
    }


def fetch_posts(limit: int, window_days: int, subreddit: str = "thetagang", config: Config = None) -> List[Dict]:
    """
    Fetch top posts from specified subreddit with deduplication and caching.
    
    Fetches both 'top' posts from the past week and 'hot' posts, then deduplicates
    by post ID. Uses in-memory caching for the current run.
    
    Args:
        limit: Maximum number of posts to fetch (applied to each category)
        window_days: Days back to look for posts (currently used for cache key)
        subreddit: Subreddit name (default: "thetagang")
        config: Configuration object with Reddit credentials
        
    Returns:
        List of dictionaries with post data
    """
    # Create cache key
    cache_key = f"{subreddit}_{limit}_{window_days}"
    
    # Check cache first
    if cache_key in _posts_cache:
        return _posts_cache[cache_key]
    
    if config is None:
        from .config import get_config
        config = get_config()
    
    # Initialize Reddit client
    reddit = _get_reddit_client(config)
    subreddit_obj = reddit.subreddit(subreddit)
    
    # Track post IDs for deduplication
    seen_ids: Set[str] = set()
    posts: List[Dict] = []
    
    try:
        # Fetch top posts from the past week
        print(f"📱 Fetching top posts from r/{subreddit} (limit: {limit})...")
        for submission in subreddit_obj.top(time_filter='week', limit=limit):
            if submission.id not in seen_ids:
                seen_ids.add(submission.id)
                posts.append(_post_to_dict(submission))
        
        # Fetch hot posts (limit ~100 as specified)
        hot_limit = min(100, limit * 2)  # Cap at 100 but scale with limit
        print(f"📱 Fetching hot posts from r/{subreddit} (limit: {hot_limit})...")
        for submission in subreddit_obj.hot(limit=hot_limit):
            if submission.id not in seen_ids:
                seen_ids.add(submission.id)
                posts.append(_post_to_dict(submission))
        
        print(f"✅ Fetched {len(posts)} unique posts (deduplicated from {len(seen_ids)} total)")
        
    except Exception as e:
        print(f"❌ Error fetching posts from r/{subreddit}: {e}")
        raise
    
    # Cache the results
    _posts_cache[cache_key] = posts
    
    return posts


def clear_cache():
    """Clear the in-memory posts cache."""
    global _posts_cache
    _posts_cache.clear()
    print("🧹 Cleared Reddit posts cache")
