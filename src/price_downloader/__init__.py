"""
DOKKAEBI Price Downloader Package

A bulletproof, high-performance price data downloader with DuckDB caching.
Built for the DOKKAEBI algorithmic trading platform.

Viper's REBELLIOUSLY ELEGANT implementation - fucking flawless as always.
"""

# Legacy imports - commenting out as we're using AlpacaProvider now
# from .core.downloader import PriceDownloader
# from .core.ticker_universe import TickerUniverse
from .storage.cache import PriceCache
# from .filters.market_filters import (
#     PriceFilter,
#     VolumeFilter, 
#     MarketCapFilter,
#     ExchangeFilter
# )

__version__ = "1.0.0"
__author__ = "Viper - The PEP-8 Code Warrior"

__all__ = [
    # "PriceDownloader",
    # "TickerUniverse", 
    "PriceCache",
    # "PriceFilter",
    # "VolumeFilter",
    # "MarketCapFilter", 
    # "ExchangeFilter",
]