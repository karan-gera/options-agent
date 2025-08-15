"""
Ticker extraction and validation.

Extracts tickers from posts and validates against NASDAQ symbol masters.
"""

import re
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set
from collections import defaultdict

# Cache directory for symbol masters
CACHE_DIR = Path(".cache/symbols")

# Symbol master URLs
NASDAQ_LISTED_URL = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

# Regex patterns for ticker extraction
CASHTAG_PATTERN = re.compile(r'\$([A-Za-z]{1,5})\b')
ALL_CAPS_PATTERN = re.compile(r'\b([A-Z]{1,5})\b')

# Common words to exclude from ALL-CAPS extraction
EXCLUDED_WORDS = {
    # Single letters
    'A', 'I',
    # Common words
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS',
    'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'USE', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE',
    'HIM', 'TWO', 'HOW', 'ITS', 'WHO', 'DID', 'YES', 'HIS', 'HAS', 'HAD', 'LET',
    'PUT', 'TOO', 'WHY', 'TRY', 'SHE', 'MAY', 'SAY', 'END', 'WAY', 'OWN', 'BUY',
    'WIN', 'RUN', 'TOP', 'GOT', 'SET', 'AGO', 'LOT', 'BAD', 'BIG', 'FEW', 'OFF',
    'FAR', 'ANY', 'LOW', 'HIGH', 'GOOD', 'WELL', 'VERY', 'MUCH', 'LONG', 'MADE',
    'OPEN', 'CALL', 'PUTS', 'CASH', 'RISK', 'LOSS', 'GAIN', 'SELL', 'HOLD',
    'ROLL', 'WEEK', 'YEAR', 'TIME', 'POOR', 'RICH', 'SAFE', 'PLAY', 'MOVE',
    # Trading-specific terms
    'CSP', 'CC', 'CCS', 'PCS', 'ITM', 'OTM', 'ATM', 'DTE', 'IV', 'ROI', 'P&L',
    'SIDE', 'BEST', 'LAST', 'NEXT', 'HELP', 'WORK', 'TAKE', 'MAKE', 'GIVE',
    'TELL', 'LOOK', 'COME', 'KNOW', 'WANT', 'NEED', 'FEEL', 'SEEM', 'KEEP',
    'TURN', 'SHOW', 'FIND', 'STOP', 'WAIT', 'STAY', 'FALL', 'RISE',
    'PUMP', 'DUMP', 'MOON', 'BEAR', 'BULL', 'YOLO', 'FOMO', 'HODL', 'BTFD',
    'EDIT', 'TLDR', 'IMHO', 'IIRC'
}


def _ensure_cache_dir():
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _is_symbol_file_fresh(file_path: Path, max_age_hours: int = 24) -> bool:
    """Check if symbol file is fresh (downloaded within max_age_hours)."""
    if not file_path.exists():
        return False
    
    file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
    return file_age < timedelta(hours=max_age_hours)


def _download_symbol_master(url: str, filename: str) -> Path:
    """Download symbol master file to cache."""
    _ensure_cache_dir()
    file_path = CACHE_DIR / filename
    
    try:
        print(f"📥 Downloading {filename} from NASDAQ...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✅ Downloaded {filename} to cache")
        return file_path
        
    except Exception as e:
        print(f"❌ Error downloading {filename}: {e}")
        raise


def _load_symbol_masters() -> Set[str]:
    """Load and parse symbol masters from cache or download if needed."""
    nasdaq_file = CACHE_DIR / "nasdaqlisted.txt"
    other_file = CACHE_DIR / "otherlisted.txt"
    
    # Download if files don't exist or are stale
    if not _is_symbol_file_fresh(nasdaq_file):
        _download_symbol_master(NASDAQ_LISTED_URL, "nasdaqlisted.txt")
    
    if not _is_symbol_file_fresh(other_file):
        _download_symbol_master(OTHER_LISTED_URL, "otherlisted.txt")
    
    valid_symbols = set()
    
    # Parse NASDAQ listed symbols
    try:
        with open(nasdaq_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('Symbol|'):  # Skip header
                    continue
                if '|' in line:
                    symbol = line.split('|')[0].strip()
                    if symbol and symbol != 'File Creation Time':
                        valid_symbols.add(symbol.upper())
    except Exception as e:
        print(f"⚠️ Error parsing {nasdaq_file}: {e}")
    
    # Parse other listed symbols  
    try:
        with open(other_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('ACT Symbol|'):  # Skip header
                    continue
                if '|' in line:
                    symbol = line.split('|')[0].strip()
                    if symbol and symbol != 'File Creation Time':
                        valid_symbols.add(symbol.upper())
    except Exception as e:
        print(f"⚠️ Error parsing {other_file}: {e}")
    
    print(f"📊 Loaded {len(valid_symbols)} valid symbols from NASDAQ masters")
    return valid_symbols


def _extract_tickers_from_text(text: str) -> Set[str]:
    """Extract potential tickers from text using cashtags and ALL-CAPS patterns."""
    tickers = set()
    
    # Extract cashtags ($AAPL)
    cashtags = CASHTAG_PATTERN.findall(text)
    for tag in cashtags:
        tickers.add(tag.upper())
    
    # Extract ALL-CAPS tokens (AAPL)
    all_caps = ALL_CAPS_PATTERN.findall(text)
    for token in all_caps:
        if token not in EXCLUDED_WORDS and len(token) >= 1:
            tickers.add(token.upper())
    
    return tickers


def extract_valid_tickers(posts: List[Dict]) -> Dict[str, int]:
    """
    Extract and validate tickers from posts, returning mention counts.
    
    Args:
        posts: List of post dictionaries with 'title' and 'selftext'
        
    Returns:
        Dictionary mapping valid ticker symbols to mention counts
    """
    # Load valid symbols from NASDAQ masters
    valid_symbols = _load_symbol_masters()
    
    # Track mentions per ticker
    ticker_mentions = defaultdict(int)
    
    print(f"🔍 Extracting tickers from {len(posts)} posts...")
    
    for post in posts:
        # Combine title and selftext
        title = post.get('title', '')
        selftext = post.get('selftext', '')
        full_text = f"{title} {selftext}"
        
        # Extract potential tickers
        extracted_tickers = _extract_tickers_from_text(full_text)
        
        # Validate against symbol masters and count mentions (each unique ticker per post counts as 1)
        for ticker in extracted_tickers:
            if ticker in valid_symbols:
                ticker_mentions[ticker] += 1
    
    # Convert defaultdict to regular dict and sort by mentions
    result = dict(ticker_mentions)
    
    print(f"📈 Found {len(result)} valid tickers with total {sum(result.values())} mentions")
    
    return result


def get_top_tickers(ticker_mentions: Dict[str, int], limit: int = 10) -> List[tuple]:
    """
    Get top tickers by mention count.
    
    Args:
        ticker_mentions: Dictionary of ticker -> mention count
        limit: Maximum number of tickers to return
        
    Returns:
        List of (ticker, count) tuples sorted by count descending
    """
    return sorted(ticker_mentions.items(), key=lambda x: x[1], reverse=True)[:limit]


def filter_tickers_by_mentions(
    ticker_mentions: Dict[str, int], 
    min_mentions: int = 2
) -> Dict[str, int]:
    """
    Filter tickers by minimum mention count.
    
    Args:
        ticker_mentions: Dictionary of ticker -> mention count
        min_mentions: Minimum mentions required
        
    Returns:
        Filtered dictionary with tickers meeting minimum mentions
    """
    return {
        ticker: count 
        for ticker, count in ticker_mentions.items() 
        if count >= min_mentions
    }
