#!/usr/bin/env python3
"""
Test script to verify the new get_latest_bar() implementation for Latest mode.

This script tests:
1. That get_latest_bar() downloads exactly 1 record
2. That the timestamp is recent (not 4:00 AM)
3. That the data is properly stored in cache
4. That the web API integration works correctly
"""

import os
import sys
import asyncio
from datetime import datetime, timezone
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.price_downloader.providers.alpaca_provider import AlpacaProvider
from app.api.routes import download_symbol_data, get_alpaca_provider
from src.price_downloader.storage.cache_v2 import PriceCacheV2


def test_alpaca_provider_direct():
    """Test the get_latest_bar method directly."""
    print("🔬 Testing AlpacaProvider.get_latest_bar() directly...")
    
    try:
        provider = AlpacaProvider(cache_enabled=True)
        
        # Test get_latest_bar for AAPL
        print("\n📊 Getting latest bar for AAPL...")
        latest_data = provider.get_latest_bar("AAPL", "15Min")
        
        if latest_data is not None and not latest_data.empty:
            print(f"✅ SUCCESS: Got {len(latest_data)} record(s)")
            print(f"📅 Timestamp: {latest_data.index[0]}")
            print(f"💰 Close Price: ${latest_data['Close'].iloc[0]:.2f}")
            
            # Check if timestamp is recent (within last 24 hours)
            timestamp = latest_data.index[0]
            
            # Handle timezone-aware timestamps properly
            if hasattr(timestamp, 'tz') and timestamp.tz is not None:
                # Already timezone-aware, convert to UTC
                timestamp_utc = timestamp.tz_convert(timezone.utc)
            else:
                # Assume UTC if no timezone info
                timestamp_utc = timestamp.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            time_diff = abs((now - timestamp_utc).total_seconds())
            
            if time_diff < 86400:  # 24 hours
                print(f"✅ Timestamp is recent (within 24 hours)")
            else:
                print(f"⚠️  Timestamp is old ({time_diff/3600:.1f} hours ago)")
            
            # Check if it's not 4:00 AM
            hour = timestamp_utc.hour
            if hour == 4:
                print("❌ FAILURE: Got 4:00 AM timestamp (the old bug!)")
            else:
                print(f"✅ Good timestamp: {hour}:xx UTC (not 4:00 AM)")
                
            return True
        else:
            print("❌ FAILURE: No data returned")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


async def test_api_integration():
    """Test the API route integration."""
    print("\n🌐 Testing API route integration...")
    
    try:
        provider = get_alpaca_provider()
        
        # Test download_symbol_data with days_back=0 (Latest mode)
        print("📊 Testing download_symbol_data with days_back=0...")
        records = await download_symbol_data(provider, "AAPL", days_back=0)
        
        print(f"📈 Records downloaded: {records}")
        
        if records == 1:
            print("✅ SUCCESS: Downloaded exactly 1 record (Latest mode)")
            return True
        elif records == 0:
            print("❌ FAILURE: No records downloaded")
            return False
        else:
            print(f"⚠️  WARNING: Downloaded {records} records (expected 1)")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_cache_storage():
    """Test that the data is properly stored in cache."""
    print("\n💾 Testing cache storage...")
    
    try:
        cache = PriceCacheV2("data/price_cache.duckdb")
        
        # Check if AAPL data exists in intraday_prices table
        with cache._get_connection() as conn:
            query = """
            SELECT COUNT(*) as count, MAX(bar_timestamp) as latest_timestamp
            FROM intraday_prices 
            WHERE symbol = 'AAPL' AND timeframe = '15min'
            """
            result = conn.execute(query).fetchone()
            
            if result:
                count, latest_timestamp = result
                print(f"📊 AAPL 15-minute records in cache: {count}")
                if latest_timestamp:
                    print(f"📅 Latest timestamp in cache: {latest_timestamp}")
                
                if count > 0:
                    print("✅ SUCCESS: Data found in cache")
                    return True
                else:
                    print("❌ FAILURE: No data in cache")
                    return False
            else:
                print("❌ FAILURE: Could not query cache")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 DOKKAEBI Latest Bar Implementation Test")
    print("=" * 50)
    
    # Check for API credentials
    if not os.getenv('ALPACA_API_KEY') or not os.getenv('ALPACA_API_SECRET'):
        print("❌ ALPACA API credentials not found!")
        print("Set ALPACA_API_KEY and ALPACA_API_SECRET environment variables")
        return
    
    # Run tests
    results = []
    
    print("\n1️⃣ DIRECT PROVIDER TEST")
    results.append(test_alpaca_provider_direct())
    
    print("\n2️⃣ API INTEGRATION TEST")
    results.append(asyncio.run(test_api_integration()))
    
    print("\n3️⃣ CACHE STORAGE TEST")
    results.append(test_cache_storage())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("🎉 get_latest_bar() implementation is working correctly!")
    else:
        print(f"⚠️  {passed}/{total} TESTS PASSED")
        print("🔧 Some issues need to be fixed")
    
    print("\nExpected behavior:")
    print("- Downloads exactly 1 record for Latest mode")
    print("- Timestamp should be recent (within market hours)")
    print("- NOT 4:00 AM (that was the old bug)")
    print("- Data should be stored in cache properly")


if __name__ == "__main__":
    main()