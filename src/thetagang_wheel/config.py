"""
Configuration management for ThetagangWheel.

Uses Pydantic for settings validation and environment variable loading.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration with environment variable support."""
    
    # Reddit API Configuration
    reddit_client_id: str = Field(..., env="REDDIT_CLIENT_ID")
    reddit_secret: str = Field(..., env="REDDIT_SECRET") 
    reddit_user_agent: str = Field(..., env="REDDIT_USER_AGENT")
    
    # Core Screening Parameters
    capital: float = Field(10000.0, env="CAPITAL", description="Account capital for position sizing")
    max_strike: float = Field(100.0, env="MAX_STRIKE", description="Maximum strike price")
    min_oi: int = Field(200, env="MIN_OI", description="Minimum open interest")
    max_spread_pct: float = Field(5.0, env="MAX_SPREAD_PCT", description="Maximum bid-ask spread percentage")
    delta_min: float = Field(0.20, env="DELTA_MIN", description="Minimum delta for put options")
    delta_max: float = Field(0.35, env="DELTA_MAX", description="Maximum delta for put options")
    exclude_earnings: bool = Field(True, env="EXCLUDE_EARNINGS", description="Exclude options near earnings")
    
    # Sentiment Filtering
    include_unclear_sentiment: bool = Field(False, env="INCLUDE_UNCLEAR_SENTIMENT", description="Include posts with unclear sentiment")
    
    # Reddit Configuration  
    subreddit: str = Field("thetagang", env="SUBREDDIT", description="Subreddit to analyze")
    reddit_limit: int = Field(200, env="REDDIT_LIMIT", description="Maximum posts to fetch")
    reddit_window_days: int = Field(7, env="REDDIT_WINDOW_DAYS", description="Days back to look for posts")
    
    # System Settings
    timezone: str = Field("America/New_York", env="TIMEZONE", description="Market timezone")
    
    # Legacy compatibility (optional)
    db_path: str = Field("thetagang_wheel.db", env="DB_PATH", description="Database file path")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_config() -> Config:
    """Get application configuration instance."""
    return Config()
