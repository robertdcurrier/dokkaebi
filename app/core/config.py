"""
DOKKAEBI Configuration Settings
Following the shardrunner pattern but for price data domination!
"""

import os
from typing import List


class Settings:
    """Application settings."""
    
    # App info
    app_name: str = "DOKKAEBI Price System"
    app_version: str = "1.0.0"
    app_description: str = "HebbNet-powered algorithmic trading platform"
    
    # CORS settings
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Data paths
    cache_path: str = "data/price_cache.duckdb"
    watchlist_path: str = "data/watchlist.txt"
    
    # Alpaca settings
    alpaca_api_key: str = os.getenv("ALPACA_API_KEY", "")
    alpaca_api_secret: str = os.getenv("ALPACA_API_SECRET", "")
    
    # Development
    debug: bool = os.getenv("DEBUG", "").lower() in ["true", "1", "yes"]


settings = Settings()