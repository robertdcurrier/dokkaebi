#!/usr/bin/env python3
"""
VALIDATE METHOD 2 - Today's Range + Last Bar
===========================================

Method 2 showed promising results (14:00:00 EDT, 23.6 minutes old).
This validates it's working correctly and can be used reliably.

Method 2 approach:
- Use today's market hours (9:30 AM EDT to now-16min)  
- Get all 15Min bars for today
- Take the last bar (df.tail(1))

This should be Bob's solution for getting the LATEST bar reliably.
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

try:
    from price_downloader.providers.alpaca_provider import AlpacaProvider
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)


def format_timestamp(dt):
    """Format timestamp for EDT display."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to EDT (UTC-4)
    edt = timezone(timedelta(hours=-4))
    local_time = dt.astimezone(edt)
    
    return f"{local_time.strftime('%Y-%m-%d %H:%M:%S')} EDT"


def get_latest_pltr_method2():
    """Get latest PLTR using Method 2 - Today's range + last bar."""
    
    print("🎯 METHOD 2 - Today's Market Range + Last Bar")
    print("=" * 50)
    
    provider = AlpacaProvider(cache_enabled=False)
    
    # Get today's data from market open to now-16min
    now = datetime.now(timezone.utc)
    today = now.date()
    
    # Market opens at 9:30 AM EDT = 13:30 UTC
    start_time = datetime.combine(today, datetime.min.time()).replace(
        tzinfo=timezone.utc
    ) + timedelta(hours=13, minutes=30)
    end_time = now - timedelta(minutes=16)
    
    print(f"📅 Date Range:")
    print(f"   Start: {format_timestamp(start_time)}")
    print(f"   End:   {format_timestamp(end_time)}")
    print(f"   Current Time: {format_timestamp(now)}")
    print()
    
    # Get all bars for today
    print("⏳ Fetching PLTR 15Min bars for today...")
    df = provider.get_historical_data(
        symbol='PLTR',
        start=start_time,
        end=end_time,
        interval='15Min'
    )
    
    if df.empty:
        print("❌ No data returned")
        return None
    
    print(f"✅ Got {len(df)} bars for today")
    
    # Show last few bars
    print("\n📊 Last 5 bars received:")
    print("-" * 60)
    print(f"{'Time (EDT)':<20} {'Open':<8} {'High':<8} {'Low':<8} {'Close':<8} {'Volume':<10}")
    print("-" * 60)
    
    last_5 = df.tail(5)
    for timestamp, row in last_5.iterrows():
        formatted_time = format_timestamp(timestamp)
        print(f"{formatted_time:<20} "
              f"{row['Open']:<8.2f} "
              f"{row['High']:<8.2f} "
              f"{row['Low']:<8.2f} "
              f"{row['Close']:<8.2f} "
              f"{int(row['Volume']):<10}")
    
    # Get the LATEST bar (last in the DataFrame)
    latest_bar_time = df.index[-1]
    latest_bar_data = df.iloc[-1]
    
    print("-" * 60)
    print(f"\n🎯 LATEST BAR (Method 2):")
    print(f"   📊 Time: {format_timestamp(latest_bar_time)}")
    print(f"   💰 Open: ${latest_bar_data['Open']:.2f}")
    print(f"   💰 High: ${latest_bar_data['High']:.2f}")
    print(f"   💰 Low: ${latest_bar_data['Low']:.2f}")
    print(f"   💰 Close: ${latest_bar_data['Close']:.2f}")
    print(f"   📊 Volume: {int(latest_bar_data['Volume']):,}")
    
    # Calculate how fresh this data is
    time_diff = now - latest_bar_time
    minutes_old = time_diff.total_seconds() / 60
    print(f"   ⏰ Age: {minutes_old:.1f} minutes old")
    
    # Validate this is recent market hours data
    bar_hour_edt = latest_bar_time.astimezone(timezone(timedelta(hours=-4))).hour
    if 13 <= bar_hour_edt <= 16:  # 1:00 PM to 4:00 PM EDT
        print(f"   ✅ VALIDATED: Market hours data ({bar_hour_edt}:xx EDT)")
        if minutes_old <= 30:  # Within expected delay
            print(f"   ✅ VALIDATED: Data is fresh (within 30 min expected delay)")
        else:
            print(f"   ⚠️  WARNING: Data is older than expected")
    else:
        print(f"   ❌ WARNING: Off-hours data ({bar_hour_edt}:xx EDT)")
    
    return latest_bar_time, latest_bar_data


def create_production_function():
    """Create the production function Bob can use."""
    
    print("\n" + "=" * 60)
    print("🔧 PRODUCTION FUNCTION FOR BOB")
    print("=" * 60)
    
    function_code = '''
def get_latest_pltr_bar():
    """
    Get the latest PLTR 15-minute bar using Method 2.
    
    This method:
    1. Gets today's market data (9:30 AM EDT to now-16min)
    2. Takes the last bar from the DataFrame
    3. Returns ONE record - the most recent available
    
    Returns:
        tuple: (timestamp, bar_data_dict) or None if error
    """
    from datetime import datetime, timedelta, timezone
    from price_downloader.providers.alpaca_provider import AlpacaProvider
    
    try:
        provider = AlpacaProvider(cache_enabled=False)
        
        # Get today's market hours data
        now = datetime.now(timezone.utc)
        today = now.date()
        
        # Market opens at 9:30 AM EDT = 13:30 UTC
        start_time = datetime.combine(today, datetime.min.time()).replace(
            tzinfo=timezone.utc
        ) + timedelta(hours=13, minutes=30)
        end_time = now - timedelta(minutes=16)  # Account for API delay
        
        # Get all 15Min bars for today
        df = provider.get_historical_data(
            symbol='PLTR',
            start=start_time,
            end=end_time,
            interval='15Min'
        )
        
        if df.empty:
            return None
        
        # Return the LATEST bar (last in DataFrame)
        latest_timestamp = df.index[-1]
        latest_data = {
            'Open': df['Open'].iloc[-1],
            'High': df['High'].iloc[-1], 
            'Low': df['Low'].iloc[-1],
            'Close': df['Close'].iloc[-1],
            'Volume': df['Volume'].iloc[-1]
        }
        
        return latest_timestamp, latest_data
        
    except Exception as e:
        print(f"Error getting latest PLTR: {e}")
        return None

# Usage example:
result = get_latest_pltr_bar()
if result:
    timestamp, data = result
    print(f"Latest PLTR Close: ${data['Close']:.2f} at {timestamp}")
else:
    print("Failed to get latest PLTR data")
'''
    
    print("Copy this function into your production code:")
    print(function_code)


def main():
    """Main validation function."""
    
    print("🔥 DOKKAEBI - METHOD 2 VALIDATION")
    print("=================================")
    print("Testing the winning approach: Today's range + last bar\n")
    
    # Test Method 2
    result = get_latest_pltr_method2()
    
    if result:
        timestamp, data = result
        print(f"\n✅ SUCCESS!")
        print(f"   Method 2 successfully returned the latest PLTR bar")
        print(f"   Time: {format_timestamp(timestamp)}")
        print(f"   Close: ${data['Close']:.2f}")
        
        # Create production function
        create_production_function()
    else:
        print(f"\n❌ FAILED!")
        print(f"   Method 2 did not return data")


if __name__ == "__main__":
    if not os.getenv('ALPACA_API_KEY') or not os.getenv('ALPACA_API_SECRET'):
        print("❌ ALPACA API CREDENTIALS MISSING!")
        sys.exit(1)
    
    main()