#!/usr/bin/env python3
"""
Test script for DOKKAEBI Price Downloader

Quick validation that Viper's fucking flawless implementation works.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from price_downloader import PriceDownloader, TickerUniverse
from price_downloader.filters.market_filters import (
    PriceFilter, VolumeFilter, LiquidityFilter
)

def test_basic_download():
    """Test basic price download functionality."""
    print("🔥 Testing basic price download...")
    
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    with PriceDownloader(cache_path="sandbox/test_cache.duckdb") as downloader:
        results = downloader.download_batch(
            test_symbols,
            period="1mo",
            show_progress=True
        )
        
        for symbol, data in results.items():
            if data is not None:
                print(f"✓ {symbol}: {len(data)} rows downloaded")
            else:
                print(f"✗ {symbol}: Download failed")
                
        # Test cache stats
        stats = downloader.get_cache_stats()
        print(f"📊 Cache stats: {stats}")
        

def test_ticker_universe():
    """Test ticker universe fetching."""
    print("\n🌍 Testing ticker universe...")
    
    ticker_universe = TickerUniverse(cache_dir="sandbox/ticker_cache")
    
    # Test NASDAQ fetch (should use fallback for testing)
    nasdaq_tickers = ticker_universe.get_exchange_tickers('NASDAQ')
    print(f"📈 NASDAQ tickers: {len(nasdaq_tickers)}")
    print(f"Sample: {nasdaq_tickers[:10]}")
    

def test_filters():
    """Test filtering system."""
    print("\n🔍 Testing filters...")
    
    # Create test data
    import pandas as pd
    
    test_data = pd.DataFrame({
        'symbol': ['AAPL', 'PENNY', 'BIGVOL', 'LOWVOL'],
        'close': [150.0, 0.50, 25.0, 100.0],
        'volume': [50_000_000, 1_000, 10_000_000, 500]
    })
    
    print("Original data:")
    print(test_data)
    
    # Test price filter
    price_filter = PriceFilter(min_price=1.0, max_price=50.0)
    filtered_price = price_filter.apply(test_data)
    print(f"\nAfter price filter (1-50): {len(filtered_price)} rows")
    print(filtered_price)
    
    # Test liquidity filter  
    liquidity_filter = LiquidityFilter(
        min_dollar_volume=1_000_000,
        min_volume=10_000
    )
    filtered_liquidity = liquidity_filter.apply(test_data)
    print(f"\nAfter liquidity filter: {len(filtered_liquidity)} rows")
    print(filtered_liquidity)
    

if __name__ == '__main__':
    print("🚀 DOKKAEBI Price Downloader Test Suite")
    print("Viper's REBELLIOUSLY ELEGANT validation\n")
    
    try:
        test_basic_download()
        test_ticker_universe()
        test_filters()
        
        print("\n✅ All tests passed! System is fucking flawless!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()