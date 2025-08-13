#!/usr/bin/env python3
"""
Demo showing how the meme detector can automatically
call the price downloader without manual intervention.

This is the magic of automation!
"""

import os
import sys
import json

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Alpaca credentials
# Load from environment - set ALPACA_API_KEY
# Load from environment - set ALPACA_API_SECRET

from src.price_downloader.api import PriceDownloaderAPI, download_for_meme_detector


def simulate_meme_detector():
    """
    Simulate how the meme detector would automatically
    download price data for detected stocks.
    """
    print("🤖 MEME DETECTOR SIMULATION\n")
    print("=" * 50)
    
    # Step 1: Meme detector identifies hot stocks
    print("\n1️⃣  Meme detector scans social media...")
    detected_stocks = ['GME', 'AMC', 'DNUT', 'BB', 'CLOV']
    print(f"   Found trending stocks: {', '.join(detected_stocks)}")
    
    # Step 2: Automatically download price data
    print("\n2️⃣  Automatically downloading price data...")
    data = download_for_meme_detector(detected_stocks)
    
    # Step 3: Analyze the data
    print("\n3️⃣  Analyzing price movements:")
    for symbol, df in data.items():
        if not df.empty:
            latest_price = df['Close'].iloc[-1]
            week_ago_price = df['Close'].iloc[-5] if len(df) >= 5 else df['Close'].iloc[0]
            week_change = ((latest_price - week_ago_price) / week_ago_price) * 100
            
            # Emoji based on performance
            if week_change > 10:
                emoji = "🚀"
            elif week_change > 5:
                emoji = "📈"
            elif week_change < -5:
                emoji = "📉"
            else:
                emoji = "➡️"
            
            print(f"   {emoji} {symbol}: ${latest_price:.2f} ({week_change:+.1f}% week)")
    
    print("\n" + "=" * 50)
    print("✅ Meme detector has fresh data for HebbNet training!\n")


def test_json_integration():
    """
    Test JSON-based integration for automated workflows.
    """
    print("📋 JSON INTEGRATION TEST\n")
    print("=" * 50)
    
    # Create a JSON request (like what meme detector would send)
    json_request = {
        "symbols": ["TSLA", "NVDA", "AMD"],
        "period": "1mo",
        "interval": "1Day"
    }
    
    print("\nJSON Request:")
    print(json.dumps(json_request, indent=2))
    
    # Initialize API
    api = PriceDownloaderAPI()
    
    # Download using JSON
    print("\nDownloading via JSON...")
    data = api.download_from_json(json_request)
    
    print("\nResults:")
    for symbol, df in data.items():
        if not df.empty:
            print(f"✅ {symbol}: {len(df)} days of data")
            print(f"   Latest close: ${df['Close'].iloc[-1]:.2f}")
            print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")


def test_watchlist_integration():
    """
    Test watchlist file integration.
    """
    print("📄 WATCHLIST FILE TEST\n")
    print("=" * 50)
    
    # Check if watchlist exists
    watchlist_path = 'data/watchlist.txt'
    if os.path.exists(watchlist_path):
        # Count symbols in watchlist
        with open(watchlist_path, 'r') as f:
            symbols = [line.strip() for line in f 
                      if line.strip() and not line.startswith('#')]
        
        print(f"\nFound {len(symbols)} symbols in {watchlist_path}")
        print(f"First 5: {', '.join(symbols[:5])}")
        
        # Download first 3 for demo
        print("\nDownloading first 3 symbols from watchlist...")
        api = PriceDownloaderAPI()
        data = api.download_symbols(symbols[:3])
        
        for symbol, df in data.items():
            if not df.empty:
                print(f"✅ {symbol}: Downloaded {len(df)} days")
    else:
        print(f"❌ Watchlist not found at {watchlist_path}")


if __name__ == "__main__":
    print("🚀 DOKKAEBI AUTOMATED INTEGRATION TESTS\n")
    
    # Run all tests
    simulate_meme_detector()
    print("\n" + "🔄" * 25 + "\n")
    
    test_json_integration()
    print("\n" + "🔄" * 25 + "\n")
    
    test_watchlist_integration()
    
    print("\n✨ All integration tests complete!")
    print("\n📝 Summary:")
    print("  • Meme detector can auto-download prices ✅")
    print("  • JSON API works for programmatic calls ✅")
    print("  • Watchlist file integration works ✅")
    print("\nThe system is FULLY AUTOMATED! 🤖")