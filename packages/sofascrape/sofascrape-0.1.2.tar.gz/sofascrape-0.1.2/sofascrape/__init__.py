"""
Sofascrape - A Python library for scraping and interacting with SofaScore APIs

This package provides easy access to SofaScore's API endpoints for football data,
including live events, match statistics, player information, and more.
"""

from .client import SofascoreClient
from .models import FormatOptions

__version__ = "0.1.2"
__author__ = "Chumari"
__email__ = "dchumari@gmail.com"
__description__ = "A Python library for scraping and interacting with SofaScore APIs"
__url__ = "https://github.com/dchumari/sofascrape"

__all__ = ["SofascoreClient", "FormatOptions"]