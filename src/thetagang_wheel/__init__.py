"""
ThetagangWheel - Options Screening Tool

A Python tool that screens cash-secured put options based on 
sentiment analysis of r/thetagang posts.

For educational use only - not financial advice.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Package-level imports for convenience
from .config import Config
from .models import ScreeningResult, OptionCandidate

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "Config",
    "ScreeningResult",
    "OptionCandidate",
]
