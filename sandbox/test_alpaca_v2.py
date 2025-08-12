#!/usr/bin/env python3
"""
Test Alpaca API v2 - Let's get this working!
"""

import os
from datetime import datetime, timedelta

# Set credentials
os.environ['ALPACA_API_KEY'] = 'PKU1N7FUI5SNL5UQ9PCS'
os.environ['ALPACA_API_SECRET'] = 'Y5xtRqY4CSNLgYeIDpSUnBxoLPEYdMFuYiD5PwNJ'

print("🚀 Testing Alpaca Markets Data API\n")

try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
    from alpaca.data.timeframe import TimeFrame
    
    # Initialize client
    client = StockHistoricalDataClient(
        api_key=os.environ['ALPACA_API_KEY'],
        secret_key=os.environ['ALPACA_API_SECRET']
    )
    
    print("Testing different endpoints:\n")
    
    # Test 1: Get latest quote
    print("1. Getting latest quote for AAPL...")
    try:
        request = StockLatestQuoteRequest(symbol_or_symbols="AAPL")
        quote = client.get_stock_latest_quote(request)
        
        if quote and 'AAPL' in quote:
            q = quote['AAPL']
            print(f"✅ Latest AAPL quote: Bid=${q.bid_price:.2f}, Ask=${q.ask_price:.2f}")
        else:
            print("❌ No quote data")
    except Exception as e:
        print(f"❌ Quote error: {e}")
    
    # Test 2: Get historical bars with explicit dates
    print("\n2. Getting historical bars...")
    try:
        # Use explicit dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        request = StockBarsRequest(
            symbol_or_symbols=["AAPL"],
            timeframe=TimeFrame.Day,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )
        
        bars = client.get_stock_bars(request)
        
        if bars:
            print(f"✅ Response received: {type(bars)}")
            
            # Check different ways to access the data
            if hasattr(bars, 'data'):
                if 'AAPL' in bars.data:
                    aapl_bars = bars.data['AAPL']
                    print(f"✅ Got {len(aapl_bars)} bars for AAPL")
                    
                    # Show last bar
                    if aapl_bars:
                        last_bar = aapl_bars[-1]
                        print(f"   Latest: {last_bar.timestamp} - Close: ${last_bar.close:.2f}")
            elif isinstance(bars, dict) and 'AAPL' in bars:
                aapl_data = bars['AAPL']
                print(f"✅ Got data for AAPL: {type(aapl_data)}")
            else:
                print(f"❓ Unexpected response structure: {bars}")
        else:
            print("❌ No bars returned")
            
    except Exception as e:
        print(f"❌ Bars error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Try with limit parameter
    print("\n3. Getting bars with limit...")
    try:
        request = StockBarsRequest(
            symbol_or_symbols="AAPL",
            timeframe=TimeFrame.Day,
            limit=10
        )
        
        bars = client.get_stock_bars(request)
        
        if bars:
            # Try to access the data
            if hasattr(bars, '__dict__'):
                print(f"   Bars attributes: {bars.__dict__.keys()}")
            
            # Try direct indexing
            if 'AAPL' in bars:
                print(f"✅ Direct access works!")
                aapl_bars = bars['AAPL']
                print(f"   Type: {type(aapl_bars)}")
                
                # Try to iterate
                for i, bar in enumerate(aapl_bars):
                    if i < 3:  # Show first 3
                        print(f"   {bar.timestamp}: ${bar.close:.2f}")
                    else:
                        break
        else:
            print("❌ No data with limit")
            
    except Exception as e:
        print(f"❌ Limit error: {e}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure alpaca-py is installed:")
    print("pip install alpaca-py")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("If data isn't showing, it might be because:")
print("1. Market is closed (try adding asof parameter)")
print("2. Paper trading account needs activation")
print("3. API keys need to be regenerated")