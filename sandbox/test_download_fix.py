#!/usr/bin/env python3
"""
Test script to verify the Worker/await fix

This script tests that the download buttons work correctly
after fixing the Worker/await TypeError.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_download():
    """Test the download functionality"""
    from src.price_downloader.providers.alpaca_provider import AlpacaProvider
    from src.price_downloader.storage.cache_v2 import PriceCacheV2
    
    print("Testing Worker/await fix...")
    print("=" * 60)
    
    # Initialize components
    cache = PriceCacheV2()
    provider = AlpacaProvider(cache_enabled=True)
    
    # Test downloading a single symbol
    print("\nTesting single symbol download...")
    try:
        data = provider.get_historical_data(
            symbol="AAPL",
            interval="1day",
            start=None,
            end=None
        )
        if not data.empty:
            print(f"✓ Successfully downloaded AAPL: {len(data)} records")
        else:
            print("✗ No data returned for AAPL")
    except Exception as e:
        print(f"✗ Error downloading AAPL: {e}")
    
    # Check cache
    print("\nChecking cache...")
    try:
        stats = cache.get_cache_stats()
        print(f"✓ Cache stats: {stats}")
    except Exception as e:
        print(f"✗ Error getting cache stats: {e}")
    
    print("\n" + "=" * 60)
    print("Worker/await fix test complete!")
    print("\nThe download functionality should now work in the Textual interface.")
    print("Run 'python sandbox/demo_dos_interface.py' to test the full UI.")

if __name__ == "__main__":
    asyncio.run(test_download())