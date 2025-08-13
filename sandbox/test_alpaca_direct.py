#!/usr/bin/env python3
"""
Direct test of Alpaca API with Bob's credentials.
Let's see what's going on!
"""

import os
import sys
from datetime import datetime, timedelta

# Load credentials from environment
# Set these in your shell or .env file:
# export ALPACA_API_KEY='your-api-key'
# export ALPACA_API_SECRET='your-secret-key'
if not os.getenv('ALPACA_API_KEY'):
    print("ERROR: Please set ALPACA_API_KEY and ALPACA_API_SECRET environment variables")
    sys.exit(1)

print("🚀 Testing Alpaca Markets Connection\n")
print(f"API Key: {os.environ['ALPACA_API_KEY'][:10]}...")
print(f"Using paper trading endpoint\n")

try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    
    # Initialize client (no auth needed for paper trading)
    client = StockHistoricalDataClient(
        api_key=os.environ['ALPACA_API_KEY'],
        secret_key=os.environ['ALPACA_API_SECRET'],
        raw_data=False
    )
    
    print("✅ Client initialized\n")
    
    # Try to get AAPL data
    print("Fetching AAPL data for last 5 days...")
    
    request_params = StockBarsRequest(
        symbol_or_symbols="AAPL",
        timeframe=TimeFrame.Day,
        start=datetime.now() - timedelta(days=5)
    )
    
    bars = client.get_stock_bars(request_params)
    
    if bars and 'AAPL' in bars:
        df = bars['AAPL']
        print(f"✅ Success! Got {len(df)} bars of data\n")
        
        # Show last few bars
        for i, bar in enumerate(df[-3:]):
            print(f"  {bar.timestamp}: Close=${bar.close:.2f}, Volume={bar.volume:,}")
    else:
        print("❌ No data returned")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTrying different import...")
    
    # Try alternative import
    try:
        from alpaca_trade_api import REST
        
        api = REST(
            key_id=os.environ['ALPACA_API_KEY'],
            secret_key=os.environ['ALPACA_API_SECRET'],
            base_url='https://paper-api.alpaca.markets'
        )
        
        print("✅ REST client initialized\n")
        
        # Get bars
        bars = api.get_bars('AAPL', '1Day', limit=5)
        print(f"✅ Got data using REST API!")
        
        for bar in bars:
            print(f"  {bar.t}: Close=${bar.c:.2f}, Volume={bar.v:,}")
            
    except Exception as e2:
        print(f"❌ REST API error: {e2}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()