#!/usr/bin/env python3
"""
Test IEX Cloud API functionality before integration.
Quick verification that we can fetch OHLCV data with the free tier.
"""

import os
from datetime import datetime, timedelta
from iexfinance.stocks import get_historical_data, Stock
import pandas as pd


def test_iex_basic():
    """Test basic IEX Cloud functionality."""
    print("Testing IEX Cloud API...")
    
    # You'll need to set IEX_TOKEN environment variable
    # or pass token directly to functions
    
    try:
        # Test with a popular stock
        symbol = "AAPL"
        
        # Get recent data (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print(f"Fetching {symbol} data from {start_date.date()} to {end_date.date()}")
        
        # Method 1: Using get_historical_data
        data = get_historical_data(
            symbol, 
            start_date, 
            end_date,
            output_format='pandas'
        )
        
        print(f"✓ Successfully fetched {len(data)} rows")
        print(f"Columns: {list(data.columns)}")
        print(f"Date range: {data.index.min()} to {data.index.max()}")
        print("\nSample data:")
        print(data.head(3))
        
        # Check if we have OHLCV data
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        available_cols = [col for col in required_cols if col in data.columns]
        print(f"\nOHLCV columns available: {available_cols}")
        
        # Method 2: Using Stock class for current data
        print(f"\n--- Testing Stock class for {symbol} ---")
        stock = Stock(symbol)
        quote = stock.get_quote()
        print(f"Current price info: {quote}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing IEX Cloud: {e}")
        print("Note: You may need to set IEX_TOKEN environment variable")
        return False


def test_batch_symbols():
    """Test fetching multiple symbols."""
    print("\n--- Testing batch symbol fetch ---")
    
    try:
        symbols = ["AAPL", "MSFT", "GOOGL"]
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # Just 1 week to conserve messages
        
        results = {}
        for symbol in symbols:
            print(f"Fetching {symbol}...")
            data = get_historical_data(
                symbol,
                start_date,
                end_date,
                output_format='pandas'
            )
            results[symbol] = data
            print(f"  ✓ {len(data)} rows")
            
        print(f"Successfully fetched data for {len(results)} symbols")
        return True
        
    except Exception as e:
        print(f"❌ Error in batch test: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Testing IEX Cloud integration for DOKKAEBI")
    print("=" * 50)
    
    # Check if token is set
    token = os.getenv('IEX_TOKEN')
    if not token:
        print("⚠️  IEX_TOKEN not set in environment variables")
        print("You can get a free token at: https://iexcloud.io/")
        print("Then run: export IEX_TOKEN='your_token_here'")
        print("\nTesting anyway (may fail)...")
    else:
        print(f"✓ IEX_TOKEN found: {token[:8]}...")
    
    print()
    
    # Run tests
    if test_iex_basic():
        test_batch_symbols()
        print("\n🎉 IEX Cloud integration looks good!")
        print("Ready to implement as Yahoo Finance alternative.")
    else:
        print("\n💥 IEX Cloud test failed - check token and connection")