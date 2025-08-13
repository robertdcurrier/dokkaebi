#!/usr/bin/env python3
"""
DEBUG LATEST PLTR Data - Fix 4:00 AM vs 2:00 PM Issue
====================================================

Bob is frustrated - "Latest" mode keeps returning 4:00 AM data instead of 
the most recent bar around 2:00-2:05 PM (accounting for 16-minute delay).

Current time is ~2:20 PM EDT. We should get ONE record from ~2:00-2:05 PM.

DEBUGGING APPROACHES:
1. Test limit=1 with different date ranges
2. Try sorting/ordering parameters  
3. Check adjustment parameters
4. Test different timeframe specifications
5. Get full day data and manually select last bar

Location: sandbox/ (following memory bank rules)
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add src directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

try:
    from price_downloader.providers.alpaca_provider import AlpacaProvider
    from alpaca.data import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the dokkaebi project directory")
    sys.exit(1)


def format_timestamp(dt):
    """Format timestamp for EDT display."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to EDT (UTC-4)
    edt = timezone(timedelta(hours=-4))
    local_time = dt.astimezone(edt)
    
    return f"{local_time.strftime('%Y-%m-%d %H:%M:%S')} EDT"


def current_time_info():
    """Show current time information."""
    now = datetime.now(timezone.utc)
    print(f"🕐 Current UTC Time: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"🕐 Current EDT Time: {format_timestamp(now)}")
    
    # Expected latest bar time (current time - 16 minutes for API delay)
    expected_latest = now - timedelta(minutes=16)
    print(f"🎯 Expected Latest Bar: {format_timestamp(expected_latest)} (16min delay)")
    return now, expected_latest


def test_method_1_limit_only():
    """Test Method 1: Just use limit=1 (current approach that fails)."""
    print("\n" + "="*60)
    print("🧪 METHOD 1: limit=1 only (current failing approach)")
    print("="*60)
    
    try:
        provider = AlpacaProvider(cache_enabled=False)
        
        # Current failing approach
        df = provider.get_historical_data(
            symbol='PLTR',
            interval='15Min',
            limit=1
        )
        
        if df.empty:
            print("❌ No data returned")
            return None
        
        print(f"✅ Got {len(df)} bar(s)")
        latest_bar = df.index[-1]
        latest_close = df['Close'].iloc[-1]
        
        print(f"📊 Latest Bar Time: {format_timestamp(latest_bar)}")
        print(f"💰 Latest Close: ${latest_close:.2f}")
        
        # Check if this is the problematic 4:00 AM data
        bar_hour_edt = latest_bar.astimezone(timezone(timedelta(hours=-4))).hour
        if bar_hour_edt == 4:
            print("❌ CONFIRMED: This is the 4:00 AM data bug!")
        
        return latest_bar, latest_close
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_method_2_today_range():
    """Test Method 2: Today's date range, then take last record."""
    print("\n" + "="*60)
    print("🧪 METHOD 2: Today's date range + manual last selection")
    print("="*60)
    
    try:
        provider = AlpacaProvider(cache_enabled=False)
        
        # Get today's data from market open to now-16min
        now = datetime.now(timezone.utc)
        today = now.date()
        
        # Market opens at 9:30 AM EDT = 13:30 UTC
        start_time = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc) + timedelta(hours=13, minutes=30)
        end_time = now - timedelta(minutes=16)
        
        print(f"📅 Start: {format_timestamp(start_time)}")
        print(f"📅 End: {format_timestamp(end_time)}")
        
        df = provider.get_historical_data(
            symbol='PLTR',
            start=start_time,
            end=end_time,
            interval='15Min'
        )
        
        if df.empty:
            print("❌ No data returned")
            return None
        
        print(f"✅ Got {len(df)} bars today")
        
        # Take the LAST bar (most recent)
        latest_bar = df.index[-1]
        latest_close = df['Close'].iloc[-1]
        
        print(f"📊 Latest Bar Time: {format_timestamp(latest_bar)}")
        print(f"💰 Latest Close: ${latest_close:.2f}")
        
        return latest_bar, latest_close
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_method_3_direct_alpaca():
    """Test Method 3: Direct Alpaca API call with proper parameters."""
    print("\n" + "="*60)
    print("🧪 METHOD 3: Direct Alpaca API with sort parameters")
    print("="*60)
    
    try:
        # Initialize direct Alpaca client
        api_key = os.getenv('ALPACA_API_KEY')
        api_secret = os.getenv('ALPACA_API_SECRET')
        
        client = StockHistoricalDataClient(api_key, api_secret)
        
        # Try different request configurations
        now = datetime.now(timezone.utc)
        end_time = now - timedelta(minutes=16)
        start_time = end_time - timedelta(hours=8)  # Last 8 hours to ensure we get recent data
        
        print(f"📅 Start: {format_timestamp(start_time)}")
        print(f"📅 End: {format_timestamp(end_time)}")
        
        # Create request with explicit time range and limit
        request = StockBarsRequest(
            symbol_or_symbols='PLTR',
            timeframe=TimeFrame(15, TimeFrameUnit.Minute),
            start=start_time,
            end=end_time,
            limit=1  # This should give us the LAST bar in the time range
        )
        
        bars = client.get_stock_bars(request)
        
        if not bars or 'PLTR' not in bars.data or not bars.data['PLTR']:
            print("❌ No data returned from direct API")
            return None
        
        bar_list = bars.data['PLTR']
        print(f"✅ Got {len(bar_list)} bar(s)")
        
        # Get the bar data
        latest_bar_obj = bar_list[-1]  # Take last bar
        latest_timestamp = latest_bar_obj.timestamp
        latest_close = latest_bar_obj.close
        
        print(f"📊 Latest Bar Time: {format_timestamp(latest_timestamp)}")
        print(f"💰 Latest Close: ${latest_close:.2f}")
        
        return latest_timestamp, latest_close
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_method_4_reverse_chronological():
    """Test Method 4: Get recent data and reverse sort to ensure latest first."""
    print("\n" + "="*60)
    print("🧪 METHOD 4: Recent data + reverse chronological sort")
    print("="*60)
    
    try:
        provider = AlpacaProvider(cache_enabled=False)
        
        # Get last few hours of data
        now = datetime.now(timezone.utc)
        end_time = now - timedelta(minutes=16)
        start_time = end_time - timedelta(hours=4)  # Last 4 hours
        
        print(f"📅 Start: {format_timestamp(start_time)}")
        print(f"📅 End: {format_timestamp(end_time)}")
        
        df = provider.get_historical_data(
            symbol='PLTR',
            start=start_time,
            end=end_time,
            interval='15Min'
        )
        
        if df.empty:
            print("❌ No data returned")
            return None
        
        print(f"✅ Got {len(df)} bars in last 4 hours")
        
        # Sort by timestamp descending (most recent first) and take first row
        df_sorted = df.sort_index(ascending=False)
        
        latest_bar = df_sorted.index[0]
        latest_close = df_sorted['Close'].iloc[0]
        
        print(f"📊 Latest Bar Time: {format_timestamp(latest_bar)}")
        print(f"💰 Latest Close: ${latest_close:.2f}")
        
        # Show last few bars for context
        print("\n📊 Last 3 bars (reverse chronological):")
        for i in range(min(3, len(df_sorted))):
            bar_time = df_sorted.index[i]
            bar_close = df_sorted['Close'].iloc[i]
            print(f"  {format_timestamp(bar_time)}: ${bar_close:.2f}")
        
        return latest_bar, latest_close
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_method_5_latest_quote():
    """Test Method 5: Try latest quote API if available."""
    print("\n" + "="*60)
    print("🧪 METHOD 5: Latest quote API (if available)")
    print("="*60)
    
    try:
        from alpaca.data.requests import StockLatestQuoteRequest
        
        api_key = os.getenv('ALPACA_API_KEY')
        api_secret = os.getenv('ALPACA_API_SECRET')
        
        client = StockHistoricalDataClient(api_key, api_secret)
        
        request = StockLatestQuoteRequest(symbol_or_symbols='PLTR')
        quote = client.get_stock_latest_quote(request)
        
        if quote and 'PLTR' in quote:
            pltr_quote = quote['PLTR']
            print(f"📊 Latest Quote Time: {format_timestamp(pltr_quote.timestamp)}")
            print(f"💰 Latest Bid: ${pltr_quote.bid_price:.2f}")
            print(f"💰 Latest Ask: ${pltr_quote.ask_price:.2f}")
            return pltr_quote.timestamp, (pltr_quote.bid_price + pltr_quote.ask_price) / 2
        else:
            print("❌ No quote data returned")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("ℹ️  Latest quote API may not be available on free tier")
        return None


def main():
    """Main test function."""
    print("🔥 DOKKAEBI - DEBUG ALPACA LATEST MODE")
    print("=====================================")
    print("Goal: Get ONE record - the MOST RECENT PLTR bar")
    print("Problem: Getting 4:00 AM data instead of ~2:00 PM data\n")
    
    # Show current time info
    current_time, expected_latest = current_time_info()
    
    # Test all methods
    results = []
    
    # Method 1: Current failing approach
    result1 = test_method_1_limit_only()
    if result1:
        results.append(("Method 1 (limit=1 only)", result1))
    
    # Method 2: Today's range + manual selection
    result2 = test_method_2_today_range()
    if result2:
        results.append(("Method 2 (today range + last)", result2))
    
    # Method 3: Direct API with time range
    result3 = test_method_3_direct_alpaca()
    if result3:
        results.append(("Method 3 (direct API + range)", result3))
    
    # Method 4: Reverse chronological sort
    result4 = test_method_4_reverse_chronological()
    if result4:
        results.append(("Method 4 (reverse sort)", result4))
    
    # Method 5: Latest quote
    result5 = test_method_5_latest_quote()
    if result5:
        results.append(("Method 5 (latest quote)", result5))
    
    # Summary of results
    print("\n" + "="*60)
    print("📋 RESULTS SUMMARY")
    print("="*60)
    
    if not results:
        print("❌ ALL METHODS FAILED!")
        return
    
    best_method = None
    best_time = None
    
    for method_name, (timestamp, price) in results:
        time_diff = current_time - timestamp
        minutes_old = time_diff.total_seconds() / 60
        
        print(f"\n🧪 {method_name}:")
        print(f"   📊 Time: {format_timestamp(timestamp)}")
        print(f"   💰 Price: ${price:.2f}")
        print(f"   ⏰ Age: {minutes_old:.1f} minutes old")
        
        # Check if this looks like recent data (not 4:00 AM)
        bar_hour_edt = timestamp.astimezone(timezone(timedelta(hours=-4))).hour
        if 13 <= bar_hour_edt <= 16:  # 1:00 PM to 4:00 PM EDT (market hours)
            print(f"   ✅ GOOD: Market hours data (not 4:00 AM bug)")
            if best_time is None or timestamp > best_time:
                best_method = method_name
                best_time = timestamp
        elif bar_hour_edt == 4:
            print(f"   ❌ BAD: 4:00 AM data (the bug we're trying to fix)")
        else:
            print(f"   ⚠️  UNCLEAR: Off-hours data")
    
    if best_method:
        print(f"\n🏆 WINNER: {best_method}")
        print(f"   📊 Time: {format_timestamp(best_time)}")
        print(f"   🎯 This method gets the MOST RECENT data!")
        
        # Extract the working method details for Bob
        if "Method 2" in best_method:
            print(f"\n🔧 IMPLEMENTATION FOR BOB:")
            print(f"   Use today's date range (9:30 AM EDT to now-16min)")
            print(f"   Get all 15Min bars, then take df.tail(1) for latest")
        elif "Method 3" in best_method:
            print(f"\n🔧 IMPLEMENTATION FOR BOB:")
            print(f"   Use direct Alpaca API with start/end time range")
            print(f"   Set end_time = now - 16 minutes")
            print(f"   Set start_time = end_time - 4 hours")
            print(f"   Use limit=1 with time range for latest bar")
        elif "Method 4" in best_method:
            print(f"\n🔧 IMPLEMENTATION FOR BOB:")
            print(f"   Get recent 4-hour data with 15Min interval")
            print(f"   Sort dataframe by timestamp descending")
            print(f"   Take first row (most recent)")
    else:
        print(f"\n❌ NO WORKING METHOD FOUND!")
        print(f"   All methods returned either no data or 4:00 AM data")
        print(f"   May need to investigate Alpaca API documentation further")


if __name__ == "__main__":
    # Check credentials first
    if not os.getenv('ALPACA_API_KEY') or not os.getenv('ALPACA_API_SECRET'):
        print("❌ ALPACA API CREDENTIALS MISSING!")
        print("Set ALPACA_API_KEY and ALPACA_API_SECRET environment variables")
        sys.exit(1)
    
    main()