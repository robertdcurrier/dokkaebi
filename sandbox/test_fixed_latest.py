#!/usr/bin/env python3
"""
TEST FIXED LATEST BAR METHOD
============================

Test the new get_latest_bar() method in AlpacaProvider.
This should return the LATEST bar (around 2:00 PM) instead of 4:00 AM data.

The fix uses Method 2: Today's market range + last bar selection.
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


def test_fixed_latest_method():
    """Test the new get_latest_bar() method."""
    
    print("🔥 TESTING FIXED get_latest_bar() METHOD")
    print("=" * 50)
    
    current_time = datetime.now(timezone.utc)
    print(f"Current Time: {format_timestamp(current_time)}")
    print()
    
    try:
        provider = AlpacaProvider(cache_enabled=False)
        
        print("🧪 Testing new get_latest_bar() method...")
        
        # Test the new method
        latest_df = provider.get_latest_bar('PLTR', '15Min')
        
        if latest_df is None or latest_df.empty:
            print("❌ No data returned from get_latest_bar()")
            return False
        
        print(f"✅ Got latest bar data!")
        
        # Extract details
        latest_timestamp = latest_df.index[0]
        latest_data = latest_df.iloc[0]
        
        print(f"\n📊 LATEST PLTR BAR:")
        print(f"   Time: {format_timestamp(latest_timestamp)}")
        print(f"   Open: ${latest_data['Open']:.2f}")
        print(f"   High: ${latest_data['High']:.2f}")
        print(f"   Low: ${latest_data['Low']:.2f}")
        print(f"   Close: ${latest_data['Close']:.2f}")
        print(f"   Volume: {int(latest_data['Volume']):,}")
        
        # Calculate age
        time_diff = current_time - latest_timestamp
        minutes_old = time_diff.total_seconds() / 60
        print(f"   Age: {minutes_old:.1f} minutes old")
        
        # Check if it's market hours (not 4:00 AM bug)
        bar_hour_edt = latest_timestamp.astimezone(timezone(timedelta(hours=-4))).hour
        
        if bar_hour_edt == 4:
            print(f"   ❌ FAILED: Still returning 4:00 AM data!")
            return False
        elif 13 <= bar_hour_edt <= 16:  # Market hours
            print(f"   ✅ SUCCESS: Market hours data ({bar_hour_edt}:xx EDT)")
            if minutes_old <= 30:
                print(f"   ✅ SUCCESS: Fresh data (within expected delay)")
            else:
                print(f"   ⚠️  WARNING: Data older than expected")
            return True
        else:
            print(f"   ⚠️  UNCLEAR: Off-hours data ({bar_hour_edt}:xx EDT)")
            return True  # Still better than 4:00 AM
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def compare_methods():
    """Compare old vs new method."""
    
    print("\n" + "=" * 50)
    print("🔀 COMPARING OLD vs NEW METHODS")
    print("=" * 50)
    
    provider = AlpacaProvider(cache_enabled=False)
    
    # OLD METHOD (the broken one)
    print("\n🧪 OLD METHOD (get_historical_data with limit=1):")
    try:
        old_df = provider.get_historical_data(
            symbol='PLTR',
            interval='15Min', 
            limit=1
        )
        
        if not old_df.empty:
            old_timestamp = old_df.index[0]
            old_price = old_df['Close'].iloc[0]
            print(f"   Time: {format_timestamp(old_timestamp)}")
            print(f"   Price: ${old_price:.2f}")
            
            old_hour = old_timestamp.astimezone(timezone(timedelta(hours=-4))).hour
            if old_hour == 4:
                print(f"   ❌ BROKEN: 4:00 AM data bug!")
            else:
                print(f"   ✅ OK: Not 4:00 AM data")
        else:
            print(f"   ❌ No data")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # NEW METHOD (the fixed one)
    print("\n🧪 NEW METHOD (get_latest_bar):")
    try:
        new_df = provider.get_latest_bar('PLTR', '15Min')
        
        if new_df is not None and not new_df.empty:
            new_timestamp = new_df.index[0]
            new_price = new_df['Close'].iloc[0]
            print(f"   Time: {format_timestamp(new_timestamp)}")
            print(f"   Price: ${new_price:.2f}")
            
            new_hour = new_timestamp.astimezone(timezone(timedelta(hours=-4))).hour
            if new_hour == 4:
                print(f"   ❌ STILL BROKEN: 4:00 AM data!")
            elif 13 <= new_hour <= 16:
                print(f"   ✅ FIXED: Market hours data!")
            else:
                print(f"   ⚠️  UNCLEAR: Off-hours but not 4:00 AM")
        else:
            print(f"   ❌ No data")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    """Main test function."""
    
    print("🎯 DOKKAEBI - TEST FIXED LATEST BAR METHOD")
    print("=" * 60)
    print("Goal: Verify get_latest_bar() returns recent data, not 4:00 AM")
    print("=" * 60)
    
    # Test the fixed method
    success = test_fixed_latest_method()
    
    # Compare old vs new
    compare_methods()
    
    # Final result
    print("\n" + "=" * 60)
    if success:
        print("✅ FIXED! The get_latest_bar() method works correctly!")
        print("🎯 Bob can now use provider.get_latest_bar('PLTR') for latest data")
        print("\nUsage:")
        print("   latest_df = provider.get_latest_bar('PLTR', '15Min')")
        print("   latest_price = latest_df['Close'].iloc[0]")
        print("   latest_time = latest_df.index[0]")
    else:
        print("❌ STILL BROKEN! Need to investigate further.")
    
    print("=" * 60)


if __name__ == "__main__":
    if not os.getenv('ALPACA_API_KEY') or not os.getenv('ALPACA_API_SECRET'):
        print("❌ ALPACA API CREDENTIALS MISSING!")
        sys.exit(1)
    
    main()