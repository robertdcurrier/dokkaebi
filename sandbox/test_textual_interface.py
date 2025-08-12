#!/usr/bin/env python3
"""
Test launcher for the PRODUCTION Textual Interface

This script tests the REAL interface that works with:
- AlpacaProvider for downloads
- PriceCacheV2 for cache operations  
- data/watchlist.txt for symbol list
- data/price_cache.duckdb for actual data

Run from project root: python sandbox/test_textual_interface.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.price_downloader.textual_interface import main

if __name__ == "__main__":
    print("🚀 Testing PRODUCTION Textual Interface...")
    print("📍 Working with REAL data and providers")
    print("💾 Cache: data/price_cache.duckdb")
    print("📋 Watchlist: data/watchlist.txt")
    print()
    
    main()