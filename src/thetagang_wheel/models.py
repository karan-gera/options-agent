"""
Data models for ThetagangWheel.

Pydantic models for type safety and validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class SentimentClass(str, Enum):
    """Sentiment classification for Reddit posts."""
    POSITIVE = "positive"
    NEGATIVE = "negative" 
    UNCLEAR = "unclear"


class RedditPost(BaseModel):
    """Reddit post data model."""
    id: str
    title: str
    content: str
    score: int
    created_utc: datetime
    author: str
    url: str
    sentiment: Optional[SentimentClass] = None
    tickers: List[str] = Field(default_factory=list)


class OptionCandidate(BaseModel):
    """Options candidate for screening."""
    ticker: str
    strike: float
    bid: float
    ask: float
    mid: float
    open_interest: int
    volume: Optional[int] = None
    expiration: datetime
    implied_volatility: Optional[float] = None
    delta: Optional[float] = None
    
    @property
    def bid_ask_spread_pct(self) -> float:
        """Calculate bid-ask spread as percentage of mid price."""
        if self.mid <= 0:
            return float('inf')
        return ((self.ask - self.bid) / self.mid) * 100
    
    @property
    def weekly_yield_pct(self) -> float:
        """Calculate weekly yield percentage."""
        return (self.mid / (self.strike * 100)) * 100


class ScreeningResult(BaseModel):
    """Results from options screening."""
    timestamp: datetime
    posts_analyzed: int
    tickers_found: List[str]
    candidates: List[OptionCandidate]
    
    @property
    def top_candidates(self) -> List[OptionCandidate]:
        """Get candidates sorted by weekly yield (descending)."""
        return sorted(self.candidates, key=lambda x: x.weekly_yield_pct, reverse=True)


class TickerValidation(BaseModel):
    """Ticker validation result."""
    ticker: str
    is_valid: bool
    exchange: Optional[str] = None
    company_name: Optional[str] = None
