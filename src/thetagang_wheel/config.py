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
    
    # Screening Parameters
    account_size: float = Field(10000.0, env="ACCOUNT_SIZE")
    min_open_interest: int = Field(50, env="MIN_OPEN_INTEREST")
    max_bid_ask_spread_pct: float = Field(5.0, env="MAX_BID_ASK_SPREAD_PCT")
    earnings_blackout_days: int = Field(7, env="EARNINGS_BLACKOUT_DAYS")
    
    # Reddit Scraping
    subreddit_name: str = Field("thetagang", env="SUBREDDIT_NAME")
    max_posts: int = Field(25, env="MAX_POSTS")
    
    # Data Storage
    db_path: str = Field("thetagang_wheel.db", env="DB_PATH")
    
    # Output Settings
    timezone: str = Field("America/New_York", env="TIMEZONE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_config() -> Config:
    """Get application configuration instance."""
    return Config()
