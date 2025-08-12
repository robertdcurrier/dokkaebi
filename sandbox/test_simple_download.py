#!/usr/bin/env python3
"""
Simple test for the price downloader - let's make sure it fucking works!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.price_downloader.core.downloader import PriceDownloader
from src.price_downloader.storage.cache import PriceCache

def test_direct_download():
    """Test downloading prices directly with yfinance."""
    import yfinance as yf
    
    print("Testing direct yfinance download...")
    symbols = ["AAPL", "MSFT", "GOOGL"]
    
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1mo")
        
        if not data.empty:
            print(f"✅ {symbol}: Got {len(data)} days of data")
            print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
        else:
            print(f"❌ {symbol}: No data returned")
    
    print("\n" + "="*50)

def test_price_downloader():
    """Test our PriceDownloader implementation."""
    print("\nTesting PriceDownloader...")
    
    # Use a test database
    cache_path = "sandbox/test_prices.duckdb"
    
    try:
        downloader = PriceDownloader(cache_path=cache_path)
        
        # Test single symbol download
        print("\nDownloading AAPL data...")
        data = downloader.download_symbol("AAPL", period="1mo")
        
        if data is not None and not data.empty:
            print(f"✅ Got {len(data)} days of AAPL data")
            print(f"   Date range: {data.index[0]} to {data.index[-1]}")
            print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
        else:
            print("❌ Failed to download AAPL data")
        
        # Test batch download
        print("\nBatch downloading tech stocks...")
        symbols = ["MSFT", "GOOGL", "NVDA"]
        results = downloader.download_batch(symbols, period="1mo")
        
        for symbol, data in results.items():
            if data is not None and not data.empty:
                print(f"✅ {symbol}: {len(data)} days")
            else:
                print(f"❌ {symbol}: Failed")
        
        # Get stats
        stats = downloader.get_stats()
        print(f"\nStats: {stats}")
        
        # Close the downloader properly
        downloader.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 DOKKAEBI Price Downloader - Simple Test\n")
    print("="*50)
    
    test_direct_download()
    test_price_downloader()
    
    print("\n✨ Test complete!")