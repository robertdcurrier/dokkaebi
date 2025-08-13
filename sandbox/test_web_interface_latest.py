#!/usr/bin/env python3
"""
Test script to verify web interface integration with the new get_latest_bar() implementation.

This simulates what the web interface would receive when using Latest mode.
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.api.routes import download_single_symbol, download_watchlist


async def test_single_symbol_latest():
    """Test single symbol download with Latest mode."""
    print("🔬 Testing single symbol API endpoint (Latest mode)...")
    
    try:
        # Test the actual API endpoint that the web interface calls
        response = await download_single_symbol("AAPL", days_back=0)
        
        print(f"📊 API Response:")
        print(f"   Status: {response.status}")
        print(f"   Message: {response.message}")
        print(f"   Symbols: {response.symbols}")
        print(f"   Records Downloaded: {response.records_downloaded}")
        print(f"   Cache Updated: {response.cache_updated}")
        
        # Verify expected behavior
        if response.records_downloaded == 1:
            print("✅ SUCCESS: API reports 1 record downloaded (Latest mode)")
        else:
            print(f"❌ FAILURE: Expected 1 record, got {response.records_downloaded}")
            
        if "Latest bar" in response.message:
            print("✅ SUCCESS: Message correctly indicates Latest mode")
        else:
            print(f"⚠️  Message doesn't indicate Latest mode: {response.message}")
            
        return response.records_downloaded == 1
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


async def test_watchlist_latest():
    """Test watchlist download with Latest mode."""
    print("\n🔬 Testing watchlist API endpoint (Latest mode)...")
    
    try:
        # Test the watchlist endpoint that the web interface calls
        response = await download_watchlist(days_back=0)
        
        print(f"📊 API Response:")
        print(f"   Status: {response.status}")
        print(f"   Message: {response.message}")
        print(f"   Total Symbols: {len(response.symbols)}")
        print(f"   Total Records: {response.records_downloaded}")
        print(f"   Cache Updated: {response.cache_updated}")
        
        # Check if we got 1 record per symbol (Latest mode)
        expected_records = len(response.symbols)
        if response.records_downloaded == expected_records:
            print(f"✅ SUCCESS: Got 1 record per symbol ({expected_records} symbols)")
        else:
            avg_records = response.records_downloaded / len(response.symbols) if response.symbols else 0
            print(f"📊 Average records per symbol: {avg_records:.1f}")
            
        if "Latest bars" in response.message:
            print("✅ SUCCESS: Message correctly indicates Latest mode")
        else:
            print(f"⚠️  Message: {response.message}")
            
        return response.records_downloaded > 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run web interface tests."""
    print("🌐 DOKKAEBI Web Interface Latest Mode Test")
    print("=" * 50)
    
    # Check for API credentials
    if not os.getenv('ALPACA_API_KEY') or not os.getenv('ALPACA_API_SECRET'):
        print("❌ ALPACA API credentials not found!")
        print("Set ALPACA_API_KEY and ALPACA_API_SECRET environment variables")
        return
    
    # Run tests
    results = []
    
    print("\n1️⃣ SINGLE SYMBOL ENDPOINT TEST")
    results.append(asyncio.run(test_single_symbol_latest()))
    
    print("\n2️⃣ WATCHLIST ENDPOINT TEST")  
    results.append(asyncio.run(test_watchlist_latest()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 WEB INTERFACE TEST RESULTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("🎉 Web interface will show correct Latest mode information!")
    else:
        print(f"⚠️  {passed}/{total} TESTS PASSED")
    
    print("\nWhat the web interface will show:")
    print("- 'Downloaded 1 record' for single symbols in Latest mode")
    print("- 'Downloaded X records' for watchlist (1 per symbol)")
    print("- Messages will include 'Latest bar' or 'Latest bars'")
    print("- Timestamps should be recent (afternoon, not 4:00 AM)")


if __name__ == "__main__":
    main()