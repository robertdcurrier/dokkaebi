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
    
    try:
        # Test with a popular stock
        symbol = "AAPL"
        
        # Get historical data (avoid current date issues)
        end_date = datetime.now() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=30)      # 30 days ago
        
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
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing IEX Cloud: {e}")
        print("This might be due to:")
        print("1. Missing IEX_TOKEN environment variable")
        print("2. Invalid token")
        print("3. Network issues")
        print("4. Free tier limitations")
        return False


def test_without_token():
    """Test what happens without a token (should fail gracefully)."""
    print("\n--- Testing without token (expected to fail) ---")
    
    try:
        # This should fail but show us the error message
        symbol = "AAPL"
        stock = Stock(symbol)
        quote = stock.get_quote()
        print(f"Unexpected success: {quote}")
        return True
        
    except Exception as e:
        print(f"Expected error without token: {e}")
        return False


def get_token_instructions():
    """Print instructions for getting a free IEX Cloud token."""
    print("\n" + "="*60)
    print("🔑 HOW TO GET A FREE IEX CLOUD TOKEN:")
    print("="*60)
    print("1. Go to https://iexcloud.io/")
    print("2. Click 'Sign Up' for a free account")
    print("3. Verify your email")
    print("4. Go to your account dashboard")
    print("5. Find your API tokens (publishable and secret)")
    print("6. Set environment variable:")
    print("   export IEX_TOKEN='pk_xxxxxxxxxx'  # Use publishable token")
    print("7. Or set it in your shell profile:")
    print("   echo 'export IEX_TOKEN=\"pk_xxxxxxxxxx\"' >> ~/.bashrc")
    print("\nFree tier includes:")
    print("- 500,000 messages per month")
    print("- Real-time and historical data")
    print("- No credit card required")
    print("="*60)


if __name__ == "__main__":
    print("🚀 Testing IEX Cloud integration for DOKKAEBI")
    print("=" * 50)
    
    # Check if token is set
    token = os.getenv('IEX_TOKEN')
    if not token:
        print("⚠️  IEX_TOKEN not set in environment variables")
        get_token_instructions()
        print("\nTesting without token (will likely fail)...")
        test_without_token()
    else:
        print(f"✓ IEX_TOKEN found: {token[:8]}...")
        print()
        
        # Run actual test
        if test_iex_basic():
            print("\n🎉 IEX Cloud integration looks good!")
            print("Ready to implement as Yahoo Finance alternative.")
        else:
            print("\n💥 IEX Cloud test failed - check token and connection")
    
    print("\n📋 Next steps:")
    print("1. Get free IEX Cloud token (if not done)")
    print("2. Set IEX_TOKEN environment variable") 
    print("3. Re-run this test")
    print("4. Implement IEX provider in PriceDownloader")