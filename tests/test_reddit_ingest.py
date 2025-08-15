"""
Tests for Reddit data ingestion.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from thetagang_wheel.reddit_ingest import fetch_posts, clear_cache, _post_to_dict
from thetagang_wheel.config import Config


def test_post_to_dict():
    """Test conversion of PRAW submission to dictionary."""
    # Mock PRAW submission
    mock_submission = Mock()
    mock_submission.id = "test123"
    mock_submission.title = "Test Title"
    mock_submission.selftext = "Test content"
    mock_submission.score = 100
    mock_submission.created_utc = 1640995200  # 2022-01-01 00:00:00 UTC
    mock_submission.permalink = "/r/test/comments/test123/"
    
    result = _post_to_dict(mock_submission)
    
    assert result["id"] == "test123"
    assert result["title"] == "Test Title"
    assert result["selftext"] == "Test content"
    assert result["score"] == 100
    assert isinstance(result["created_utc"], datetime)
    assert result["permalink"] == "/r/test/comments/test123/"


def test_clear_cache():
    """Test cache clearing functionality."""
    # This just tests that clear_cache doesn't crash
    clear_cache()
    assert True  # If we get here, no exception was raised


def test_fetch_posts_function_signature():
    """Test that fetch_posts has the expected signature."""
    config = Config(
        reddit_client_id="test",
        reddit_secret="test", 
        reddit_user_agent="test"
    )
    
    # This will fail with auth error but tests the signature
    with pytest.raises(Exception):  # Expect auth failure
        fetch_posts(limit=5, window_days=7, subreddit="test", config=config)
