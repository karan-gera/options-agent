"""
Sentiment analysis for Reddit posts.

Uses NLTK VADER + custom rules for options-specific terminology.
"""

import re
import nltk
from typing import Dict, List, Literal
from nltk.sentiment import SentimentIntensityAnalyzer

# Global VADER analyzer instance
_vader_analyzer = None

# Heuristic rules for closed trade outcomes
POSITIVE_KEYWORDS = [
    "closed for profit", "took profit", "realized profit", "credit received",
    "assigned then cc profit", "assigned and sold calls", "profit taken",
    "closed profitably", "expired worthless", "kept premium", "full profit"
]

NEGATIVE_KEYWORDS = [
    "closed for loss", "blew up", "debit to roll", "realized loss", 
    "rolled for debit", "took a loss", "closed at loss", "assignment loss",
    "margin call", "stopped out"
]

UNCLEAR_KEYWORDS = [
    "rolled", "holding", "open", "still open", "monitoring", "watching",
    "continuing to hold", "keeping position", "letting it ride"
]

# Regex patterns for profit/loss indicators
PROFIT_PATTERNS = [
    r'\+\$\d+',           # +$123
    r'\+\d+%',            # +12%
    r'p/l \+',            # P/L +
    r'profit.*\+\$?\d+',  # profit +$123 or profit +123
    r'made.*\+\$?\d+',    # made +$123
    r'gained.*\+\$?\d+'   # gained +$123
]

LOSS_PATTERNS = [
    r'-\$\d+',            # -$123
    r'-\d+%',             # -12%
    r'p/l -',             # P/L -
    r'loss.*-\$?\d+',     # loss -$123 or loss -123
    r'lost.*\$?\d+',      # lost $123
    r'down.*\$?\d+'       # down $123
]


def _ensure_vader_downloaded():
    """Download VADER lexicon if not already present."""
    global _vader_analyzer
    
    if _vader_analyzer is not None:
        return _vader_analyzer
    
    try:
        # Try to initialize VADER
        _vader_analyzer = SentimentIntensityAnalyzer()
        return _vader_analyzer
    except LookupError:
        # Download VADER lexicon if not present
        print("📥 Downloading VADER lexicon for sentiment analysis...")
        nltk.download('vader_lexicon', quiet=True)
        _vader_analyzer = SentimentIntensityAnalyzer()
        print("✅ VADER lexicon downloaded successfully")
        return _vader_analyzer


def _has_positive_outcome(text: str) -> bool:
    """Check if text contains positive outcome indicators."""
    text_lower = text.lower()
    
    # Check explicit positive keywords
    for keyword in POSITIVE_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Check positive regex patterns
    for pattern in PROFIT_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    
    return False


def _has_negative_outcome(text: str) -> bool:
    """Check if text contains negative outcome indicators."""
    text_lower = text.lower()
    
    # Check explicit negative keywords
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Check negative regex patterns
    for pattern in LOSS_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    
    return False


def _has_unclear_outcome(text: str) -> bool:
    """Check if text contains unclear/ongoing indicators."""
    text_lower = text.lower()
    
    # Check unclear keywords
    for keyword in UNCLEAR_KEYWORDS:
        if keyword in text_lower:
            return True
    
    return False


def label_post(post: Dict) -> Literal["positive", "negative", "unclear"]:
    """
    Label a Reddit post as positive, negative, or unclear based on trade outcome.
    
    Uses heuristic rules prioritizing explicit results, with VADER for tie-breaking.
    
    Args:
        post: Dictionary with post data (must have 'title' and 'selftext')
        
    Returns:
        Sentiment label: "positive", "negative", or "unclear"
    """
    # Combine title and content for analysis
    title = post.get('title', '')
    content = post.get('selftext', '')
    full_text = f"{title} {content}"
    
    # Apply heuristic rules first (prioritize explicit results)
    has_positive = _has_positive_outcome(full_text)
    has_negative = _has_negative_outcome(full_text)
    has_unclear = _has_unclear_outcome(full_text)
    
    # Clear positive outcome
    if has_positive and not has_negative:
        return "positive"
    
    # Clear negative outcome
    if has_negative and not has_positive:
        return "negative"
    
    # Explicitly unclear/ongoing
    if has_unclear:
        return "unclear"
    
    # Conflicting signals or no clear indicators - use VADER for tie-breaking
    analyzer = _ensure_vader_downloaded()
    scores = analyzer.polarity_scores(full_text)
    
    # Use compound score for overall sentiment
    compound = scores['compound']
    
    if compound >= 0.2:  # Positive threshold
        return "positive"
    elif compound <= -0.2:  # Negative threshold
        return "negative"
    else:
        return "unclear"


def filter_posts_by_sentiment(
    posts: List[Dict], 
    include_positive: bool = True,
    include_negative: bool = False, 
    include_unclear: bool = False
) -> List[Dict]:
    """
    Filter posts by sentiment labels.
    
    Args:
        posts: List of post dictionaries
        include_positive: Include posts labeled as positive
        include_negative: Include posts labeled as negative  
        include_unclear: Include posts labeled as unclear
        
    Returns:
        Filtered list of posts with sentiment labels added
    """
    filtered_posts = []
    
    for post in posts:
        label = label_post(post)
        
        # Add sentiment label to post
        post_with_sentiment = post.copy()
        post_with_sentiment['sentiment'] = label
        
        # Filter based on inclusion criteria
        if (
            (include_positive and label == "positive") or
            (include_negative and label == "negative") or
            (include_unclear and label == "unclear")
        ):
            filtered_posts.append(post_with_sentiment)
    
    return filtered_posts


def analyze_sentiment_distribution(posts: List[Dict]) -> Dict[str, int]:
    """
    Analyze the distribution of sentiment labels in a set of posts.
    
    Args:
        posts: List of post dictionaries
        
    Returns:
        Dictionary with sentiment counts
    """
    distribution = {"positive": 0, "negative": 0, "unclear": 0}
    
    for post in posts:
        label = label_post(post)
        distribution[label] += 1
    
    return distribution
