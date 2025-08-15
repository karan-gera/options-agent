# ThetagangWheel - Options Screening Tool

A Python-based tool that screens cash-secured put options based on sentiment analysis of r/thetagang posts.

## ⚠️ IMPORTANT DISCLAIMERS

**FOR EDUCATIONAL USE ONLY**

- This tool is for educational and research purposes only
- NOT financial advice or trading recommendations
- Yahoo Finance data is delayed and unofficial - use for screening only
- Always conduct your own due diligence before making any investment decisions
- Options trading involves significant risk and may not be suitable for all investors
- Past performance does not guarantee future results

## Overview

ThetagangWheel analyzes posts from r/thetagang to:

1. **Ingest** top Reddit posts using the free Reddit API
2. **Classify** post sentiment as positive/negative/unclear using VADER sentiment analysis
3. **Extract** stock tickers from posts and validate against official NASDAQ symbol masters
4. **Screen** cash-secured put options for tickers with positive sentiment
5. **Rank** options by weekly yield with safety guardrails (open interest, bid-ask spread, earnings proximity)
6. **Output** results as sorted tables and exportable JSON/CSV files

## Features

- **Free Tier Stack**: Uses only free APIs and data sources
- **Sentiment Analysis**: NLTK VADER + custom rules for options-specific terminology
- **Symbol Validation**: Daily refresh of official NASDAQ/NYSE symbol masters
- **Options Screening**: Focuses on Friday expiration cash-secured puts for $10k accounts
- **Safety Guardrails**: Filters for minimum open interest, reasonable spreads, earnings blackouts
- **Market Hours Aware**: Handles market holidays and post-market expiry shifts
- **Multiple Output Formats**: Console tables, JSON, and CSV export

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/thetagang-wheel.git
cd thetagang-wheel

# Install with pip
pip install -e .

# Or with poetry (if available)
poetry install
```

### 2. Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your Reddit API credentials:

```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_SECRET=your_secret_here
REDDIT_USER_AGENT=thetagang_wheel/0.1.0 by yourusername
```

To get Reddit API credentials:
1. Go to https://www.reddit.com/prefs/apps
2. Create a new "script" application
3. Copy the client ID (under the app name) and secret

### 3. Usage

```bash
# Run the screening tool
thetagang-wheel screen

# Show help
thetagang-wheel --help

# Screen with custom parameters
thetagang-wheel screen --posts 50 --min-oi 100 --output results.json
```

## Data Sources

- **Reddit Posts**: r/thetagang via PRAW (Reddit API)
- **Options Data**: Yahoo Finance via yfinance (delayed, unofficial)
- **Symbol Validation**: NASDAQ FTP symbol masters (daily refresh)
- **Market Calendar**: pandas_market_calendars for holidays/trading days

## Technical Details

- **Python**: 3.11+ required
- **Timezone**: America/New_York for market hours
- **Options**: Friday expiration cash-secured puts only
- **Account Size**: $10,000 assumption for position sizing
- **Yield Calculation**: `mid_price / (strike * 100)` for weekly yield
- **Greeks**: Optional Black-Scholes Delta computation using Yahoo IV

## Limitations

- Yahoo Finance data has delays and may be inaccurate
- Earnings dates are best-effort and may fail
- No real-time Greeks provided by Yahoo
- Sentiment analysis is experimental and may misclassify posts
- Tool is for screening only - not a trading system

## Contributing

This is a personal-use educational tool. Feel free to fork and modify for your own learning.

## License

MIT License - See LICENSE file for details.
