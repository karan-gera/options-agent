"""
Tests for ticker extraction and validation.
"""

import pytest
from unittest.mock import patch, mock_open
from thetagang_wheel.tickers import (
    _extract_tickers_from_text,
    extract_valid_tickers, 
    get_top_tickers,
    filter_tickers_by_mentions,
    _load_symbol_masters
)


def test_extract_tickers_from_text():
    """Test ticker extraction from text using cashtags and ALL-CAPS."""
    # Test cashtag extraction
    text_with_cashtags = "I bought $AAPL and $TSLA puts today"
    tickers = _extract_tickers_from_text(text_with_cashtags)
    assert 'AAPL' in tickers
    assert 'TSLA' in tickers
    
    # Test ALL-CAPS extraction
    text_with_caps = "My NVDA position is doing well, also holding SPY"
    tickers = _extract_tickers_from_text(text_with_caps)
    assert 'NVDA' in tickers
    assert 'SPY' in tickers
    
    # Test mixed extraction
    text_mixed = "Sold $MSFT calls and bought GOOGL puts"
    tickers = _extract_tickers_from_text(text_mixed)
    assert 'MSFT' in tickers
    assert 'GOOGL' in tickers
    
    # Test exclusion of common words
    text_with_excluded = "I PUT my money in THE market for A good GAIN"
    tickers = _extract_tickers_from_text(text_with_excluded)
    assert 'PUT' not in tickers  # Excluded word
    assert 'THE' not in tickers  # Excluded word
    assert 'A' not in tickers    # Single letter
    assert 'GAIN' not in tickers # Excluded word
    
    # Test case insensitivity for cashtags
    text_lowercase = "bought $aapl and $Tsla"
    tickers = _extract_tickers_from_text(text_lowercase)
    assert 'AAPL' in tickers
    assert 'TSLA' in tickers


def test_extract_tickers_length_limits():
    """Test ticker length limits (1-5 characters)."""
    text = "I have $A $AAPL $ABCDE $ABCDEF and IBM APPLE GOOGL ABCDEF"
    tickers = _extract_tickers_from_text(text)
    
    # Valid lengths should be included
    assert 'A' in tickers      # 1 char cashtag
    assert 'AAPL' in tickers   # 4 char cashtag
    assert 'ABCDE' in tickers  # 5 char cashtag
    assert 'IBM' in tickers    # 3 char ALL-CAPS
    assert 'GOOGL' in tickers  # 5 char ALL-CAPS
    
    # 6+ chars should be excluded by regex
    # Note: ABCDEF (6 chars) should not match the regex patterns


@patch('thetagang_wheel.tickers._load_symbol_masters')
def test_extract_valid_tickers(mock_load_symbols):
    """Test full ticker extraction and validation."""
    # Mock valid symbols
    mock_load_symbols.return_value = {'AAPL', 'TSLA', 'MSFT', 'GOOGL', 'SPY'}
    
    # Sample posts
    posts = [
        {
            'title': 'My $AAPL trade update',
            'selftext': 'Sold AAPL puts for profit, also holding TSLA'
        },
        {
            'title': 'MSFT earnings play',
            'selftext': 'Bought $MSFT calls and INVALID_TICKER puts'
        },
        {
            'title': 'SPY analysis', 
            'selftext': 'SPY looking good, might add AAPL'
        }
    ]
    
    result = extract_valid_tickers(posts)
    
    # Check that valid tickers are present with correct counts
    assert 'AAPL' in result
    assert result['AAPL'] == 2  # Mentioned in post 1 (title + content) and post 3 (content) = 2 posts
    assert 'TSLA' in result  
    assert result['TSLA'] == 1  # Mentioned once
    assert 'MSFT' in result
    assert result['MSFT'] == 1  # Mentioned in 1 post (both title and content)  
    assert 'SPY' in result
    assert result['SPY'] == 1   # Mentioned in 1 post (both title and content)
    
    # Invalid ticker should not be present
    assert 'INVALID_TICKER' not in result


def test_get_top_tickers():
    """Test getting top tickers by mention count."""
    ticker_mentions = {
        'AAPL': 5,
        'TSLA': 3, 
        'MSFT': 1,
        'GOOGL': 4,
        'SPY': 2
    }
    
    top_3 = get_top_tickers(ticker_mentions, limit=3)
    
    assert len(top_3) == 3
    assert top_3[0] == ('AAPL', 5)   # Most mentions
    assert top_3[1] == ('GOOGL', 4)  # Second most
    assert top_3[2] == ('TSLA', 3)   # Third most


def test_filter_tickers_by_mentions():
    """Test filtering tickers by minimum mention count."""
    ticker_mentions = {
        'AAPL': 5,
        'TSLA': 3,
        'MSFT': 1,
        'GOOGL': 4,
        'SPY': 2
    }
    
    # Filter by minimum 3 mentions
    filtered = filter_tickers_by_mentions(ticker_mentions, min_mentions=3)
    
    expected = {'AAPL': 5, 'TSLA': 3, 'GOOGL': 4}
    assert filtered == expected


@patch('builtins.open', new_callable=mock_open)
@patch('thetagang_wheel.tickers._is_symbol_file_fresh')
@patch('thetagang_wheel.tickers._download_symbol_master')
def test_load_symbol_masters(mock_download, mock_fresh, mock_file):
    """Test loading symbol masters from cached files."""
    # Mock files as fresh (no download needed)
    mock_fresh.return_value = True
    
    # Mock file contents
    nasdaq_content = """Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares
AAPL|Apple Inc. - Common Stock|Q|N|N|100|N|N
TSLA|Tesla, Inc. - Common Stock|Q|N|N|100|N|N
File Creation Time: 1234567890"""
    
    other_content = """ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol
MSFT|Microsoft Corporation|N|MSFT|N|100|N|MSFT
GOOGL|Alphabet Inc. - Class A|Q|GOOGL|N|100|N|GOOGL
File Creation Time: 1234567890"""
    
    # Mock file reads
    mock_file.side_effect = [
        mock_open(read_data=nasdaq_content).return_value,
        mock_open(read_data=other_content).return_value
    ]
    
    symbols = _load_symbol_masters()
    
    assert 'AAPL' in symbols
    assert 'TSLA' in symbols  
    assert 'MSFT' in symbols
    assert 'GOOGL' in symbols
    assert len(symbols) == 4


def test_real_world_examples():
    """Test with real-world thetagang post examples."""
    sample_text = """
    Closed my $TSLA 220P for +$500 profit! 
    Also rolled my AAPL position and bought SPY puts.
    THE market is volatile but I MADE good money.
    """
    
    tickers = _extract_tickers_from_text(sample_text)
    
    # Should extract valid tickers
    assert 'TSLA' in tickers
    assert 'AAPL' in tickers  
    assert 'SPY' in tickers
    
    # Should exclude common words
    assert 'THE' not in tickers
    assert 'MADE' not in tickers
