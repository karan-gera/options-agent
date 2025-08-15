"""
Tests for sentiment analysis functionality.
"""

import pytest
from thetagang_wheel.sentiment import (
    label_post, 
    filter_posts_by_sentiment, 
    analyze_sentiment_distribution,
    _has_positive_outcome,
    _has_negative_outcome,
    _has_unclear_outcome
)


def test_positive_outcome_detection():
    """Test detection of positive outcome indicators."""
    positive_texts = [
        "closed for profit +$500",
        "took profit on my puts", 
        "realized profit this week",
        "credit received +25%",
        "expired worthless profit",
        "+$1000 profit made",
        "P/L +500"
    ]
    
    for text in positive_texts:
        assert _has_positive_outcome(text), f"Should detect positive in: {text}"


def test_negative_outcome_detection():
    """Test detection of negative outcome indicators."""
    negative_texts = [
        "closed for loss -$500",
        "trade blew up",
        "debit to roll position",
        "realized loss this week", 
        "rolled for debit",
        "took a loss -$1000",
        "P/L -500"
    ]
    
    for text in negative_texts:
        assert _has_negative_outcome(text), f"Should detect negative in: {text}"


def test_unclear_outcome_detection():
    """Test detection of unclear/ongoing indicators."""
    unclear_texts = [
        "rolled the position",
        "still holding shares",
        "position is open",
        "monitoring the trade",
        "watching closely",
        "continuing to hold"
    ]
    
    for text in unclear_texts:
        assert _has_unclear_outcome(text), f"Should detect unclear in: {text}"


def test_label_post_heuristic_rules():
    """Test post labeling with clear heuristic indicators."""
    # Clear positive case
    positive_post = {
        'title': 'Closed TSLA puts for profit',
        'selftext': 'Took profit +$500 on the 220P'
    }
    assert label_post(positive_post) == "positive"
    
    # Clear negative case
    negative_post = {
        'title': 'My trade blew up',
        'selftext': 'Realized loss -$800 on NVDA puts'
    }
    assert label_post(negative_post) == "negative"
    
    # Clear unclear case
    unclear_post = {
        'title': 'Still holding position',
        'selftext': 'Rolled my puts to next week'
    }
    assert label_post(unclear_post) == "unclear"


def test_filter_posts_by_sentiment():
    """Test filtering posts by sentiment labels."""
    test_posts = [
        {'title': 'Profit +$500', 'selftext': 'took profit'},
        {'title': 'Loss -$300', 'selftext': 'closed for loss'}, 
        {'title': 'Still holding', 'selftext': 'rolled position'},
        {'title': 'Great trade', 'selftext': 'made money'}
    ]
    
    # Test positive only (default)
    positive_only = filter_posts_by_sentiment(test_posts)
    assert len(positive_only) >= 1  # At least one positive
    for post in positive_only:
        assert post['sentiment'] == 'positive'
    
    # Test including unclear
    with_unclear = filter_posts_by_sentiment(
        test_posts, include_unclear=True
    )
    assert len(with_unclear) >= len(positive_only)  # Should have more posts


def test_analyze_sentiment_distribution():
    """Test sentiment distribution analysis."""
    test_posts = [
        {'title': 'Profit +$500', 'selftext': 'took profit'},
        {'title': 'Loss -$300', 'selftext': 'closed for loss'}, 
        {'title': 'Still holding', 'selftext': 'rolled position'}
    ]
    
    distribution = analyze_sentiment_distribution(test_posts)
    
    assert isinstance(distribution, dict)
    assert 'positive' in distribution
    assert 'negative' in distribution
    assert 'unclear' in distribution
    assert sum(distribution.values()) == len(test_posts)


def test_label_post_vader_fallback():
    """Test VADER sentiment analysis fallback."""
    # Test case with no clear heuristic indicators
    neutral_post = {
        'title': 'Options trading discussion',
        'selftext': 'What do you think about current market conditions?'
    }
    
    # Should use VADER for sentiment analysis
    label = label_post(neutral_post)
    assert label in ['positive', 'negative', 'unclear']
