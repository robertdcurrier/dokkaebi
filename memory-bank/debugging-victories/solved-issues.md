# Solved Issues - DOKKAEBI Project

## August 13, 2025

### Messages Window Too Small & ESC Key Popups
**Error 1**: Messages/log window too small to see output
**Error 2**: Annoying "Input Cancelled" popup every time ESC pressed
**Location**: `src/price_downloader/textual_interface.py`
**Solutions**:
1. Added `height: 25%` to RichLog CSS styling
2. Increased max_lines from 10 to 20
3. Removed the notification on ESC key press (line 1037)
```python
# Before
self.notify("[ESC] Input canceled")  # Annoying!

# After  
pass  # Silent cancel
```

### Progress Bar Hitting 100% Early
**Error**: Progress bar showing 100% after ~16 symbols when downloading 32
**Location**: `src/price_downloader/textual_interface.py`, line 89
**Root Cause**: Mismatch between progress bar scale and value
- `progress_bar.total` was set to symbol count (32)
- `progress_bar.progress` was set to percentage (50 for 16/32)
- Bar interpreted 50/32 as 156%, capped at 100%
**Solution**: Set progress to completed count, not percentage
```python
# WRONG - mixing scales
progress_bar.total = 32  # total symbols
progress_bar.progress = (16/32) * 100  # = 50, but bar expects 0-32

# CORRECT - matching scales  
progress_bar.total = 32  # total symbols
progress_bar.progress = 16  # completed symbols
```

## August 13, 2025

### Worker/await TypeError in Textual Interface
**Error**: `TypeError: object Worker can't be used in 'await' expression`
**Location**: `src/price_downloader/textual_interface.py`, line 637
**Root Cause**: Methods decorated with `@work(exclusive=True)` return Worker objects, not coroutines
**Solution**: Don't await Worker objects. Call them directly - they start automatically.

```python
# WRONG - causes TypeError
async def on_button_pressed(self, event: Button.Pressed):
    if button_id == "download-watchlist":
        await self._download_watchlist()  # ERROR: Can't await Worker

# CORRECT - Workers start automatically
async def on_button_pressed(self, event: Button.Pressed):
    if button_id == "download-watchlist":
        self._download_watchlist()  # Just call it, don't await
```

**Textual Documentation**: Workers decorated with `@work` are started automatically when called. They manage their own async execution and shouldn't be awaited.

### yfinance/multitasking Module Error
**Error**: `ModuleNotFoundError: No module named 'multitasking'`
**Root Cause**: Legacy yfinance imports still present after switching to Alpaca
**Solution**: Remove all yfinance imports since we're using Alpaca Markets exclusively
- Commented out imports in `src/price_downloader/__init__.py`
- Removed yahoo_provider from providers `__init__.py`
- Installed alpaca-py module instead

### GitGuardian API Key Exposure
**Error**: API keys exposed in 5 files
**Solution**: Removed all hardcoded Alpaca API credentials
- Used environment variables instead
- Keys now in .zshrc: ALPACA_API_KEY and ALPACA_API_SECRET

### Watchlist Scrolling Issue
**Error**: Watchlist not scrolling with keyboard
**Solution**: Wrapped ListView in ScrollableContainer
**Key Learning**: Some widgets need ScrollableContainer for keyboard scrolling

### Cache Table Scrolling Issue
**Error**: DataTable in cache viewer not scrolling
**Solution**: Removed ScrollableContainer wrapper - DataTable has built-in scrolling
**Key Learning**: Never wrap DataTable in ScrollableContainer - it scrolls natively!

### Intraday Data Download Getting Old Data Only
**Error**: Intraday downloads only getting data from morning (9:30 AM) when market has been open for 4+ hours
**Location**: `/Users/rdc/src/dokkaebi/app/api/routes.py`, lines 128-142
**Root Cause**: Date ranges for intraday intervals were too conservative, requesting too much historical data instead of focusing on recent/current data
**Solution**: Fixed intraday date ranges for real-time trading:
- 1Min/5Min: Last 2 days only (was 7 days) - for very recent high-frequency data  
- 15Min/30Min: Last 7 days (was 30 days) - for medium frequency
- 1Hour: Last 30 days (was 90 days) - for longer term intraday
- ALWAYS use `datetime.now()` as end time to get up-to-the-minute data
- Added debug logging to show exact date ranges being requested

**Key Learning**: For intraday trading data, shorter date ranges = fresher data. Don't request weeks of 1-minute data when you need TODAY'S data!

### Alpaca Free Tier 15-Minute Data Restriction
**Error**: "subscription does not permit querying recent SIP data" when requesting current data
**Location**: `/Users/rdc/src/dokkaebi/app/api/routes.py` and `/Users/rdc/src/dokkaebi/sandbox/test_alpaca_latest.py`
**Root Cause**: Alpaca free tier cannot access market data from the last 15 minutes - data must be at least 15-16 minutes old
**Solution**: Changed end time from `datetime.now()` to `datetime.now() - timedelta(minutes=16)`
```python
# WRONG - causes "subscription does not permit" error
end_time = datetime.now()

# CORRECT - ensures data is old enough for free tier access  
end_time = datetime.now() - timedelta(minutes=16)
```
**Key Learning**: Alpaca free tier has 15-minute delay on real-time data. Always subtract 16 minutes from current time to ensure access. Data will be 15-16 minutes delayed but accessible.

### Download Function Getting Old Data Instead of Current Data
**Error**: Download function only getting old data (stops at 9:30 AM) when market has been open for hours
**Location**: `/Users/rdc/src/dokkaebi/app/api/routes.py`, `download_symbol_data()` function
**Root Cause**: Date range was requesting 3 days of historical data instead of TODAY'S data
**Problem Code**:
```python
# WRONG - gets mostly old data from 3 days ago
days_back = 3
start_date = datetime.now() - timedelta(days=days_back)
end_time = datetime.now() - timedelta(minutes=16)
```
**Solution**: Use EXACT SAME method as successful test script - request only TODAY'S data
```python
# CORRECT - gets current day data only (like test script)
from datetime import timezone
today = datetime.now(timezone.utc).date()
start_date = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
end_time = datetime.now(timezone.utc) - timedelta(minutes=16)
```
**Additional Fix**: Clear old 15-minute data before downloading to prevent stale data display
```python
# Clear old data first
conn.execute("DELETE FROM intraday_prices WHERE timeframe = '15min'")
```
**Key Learning**: For current market data, request TODAY ONLY not multiple days back. Test script successfully got data up to 12:30 PM using this exact method.

### API Reports 1 Record Downloaded But Database Has 20 Records
**Error**: Frontend shows `records_downloaded: 1` but database query reveals 20 records stored
**Location**: `/Users/rdc/src/dokkaebi/app/api/routes.py` and `/Users/rdc/src/dokkaebi/src/price_downloader/providers/alpaca_provider.py`
**Root Cause**: `get_latest_bar()` method was:
1. Calling `get_historical_data()` with full day range (9:30 AM to current time)
2. `get_historical_data()` automatically cached all ~20+ bars for the day
3. `get_latest_bar()` then used `df.tail(1)` to return only 1 bar
4. API counted returned data (1) but database had cached data (20+)

**Problem Flow**:
```python
# get_latest_bar() called get_historical_data() for full day
df = get_historical_data(start=9:30AM, end=now-16min)  # Returns ~20 bars
# get_historical_data() caches ALL 20 bars automatically
latest = df.tail(1)  # Returns only 1 bar
# API reports len(latest) = 1, but cache has 20 records
```

**Solution**: Modified `get_latest_bar()` to temporarily disable caching during data fetch, then cache only the single returned bar:
```python
def get_latest_bar(self, symbol: str, interval: str = '15Min'):
    # Temporarily disable caching to prevent full day caching
    original_cache_enabled = self.cache_enabled
    self.cache_enabled = False
    
    # Get full day's data (without caching)
    df = self.get_historical_data(...)
    
    # Restore caching
    self.cache_enabled = original_cache_enabled
    
    # Get only latest bar
    latest_df = df.tail(1).copy()
    
    # Cache only the single latest bar
    if self.cache_enabled and self.cache:
        self._store_in_cache(latest_df, symbol, interval)
    
    return latest_df
```

**Key Learning**: When a method needs to fetch bulk data but only return/cache a subset, disable caching during bulk fetch then explicitly cache only the desired subset to maintain API accuracy.

## August 24, 2025

### Data Interval Selector Implementation - FUCKING FLAWLESS! 🚬⚡
**Feature**: Added comprehensive interval selector for DOKKAEBI DATA tab
**Location**: `/Users/rdc/src/dokkaebi/app/api/routes.py` and `/Users/rdc/src/dokkaebi/templates/index.html`
**Implementation**: Viper's rebelliously elegant solution

**Changes Made**:

1. **API Endpoints Enhanced** - Added `interval` parameter to all download endpoints:
   - `POST /api/download/watchlist` now accepts `interval` parameter
   - `POST /api/download/symbol/{symbol}` now accepts `interval` parameter
   - `download_symbol_data()` function updated to handle variable intervals

2. **Interval Mapping** - Clean UI-to-Alpaca format mapping:
   ```python
   interval_mapping = {
       'Daily': '1Day',
       'Hourly': '1Hour', 
       '30Min': '30Min',
       '15Min': '15Min'
   }
   ```

3. **Smart Cache Clearing** - Interval-specific data clearing:
   - Daily interval → clears `daily_prices` table
   - Intraday intervals → clears appropriate `intraday_prices` by timeframe
   - Prevents stale data display across different intervals

4. **UI Enhancements**:
   - Added interval dropdown with Daily, Hourly, 30Min, 15Min options
   - 15Min selected by default to maintain current behavior
   - Real-time description updates showing selected interval
   - LocalStorage persistence of user interval preference
   - Activity messages show selected interval in download confirmations

5. **JavaScript Integration**:
   - `updateIntervalUI()` - Updates descriptions dynamically
   - `loadUserPreferences()` - Restores saved interval on page load
   - All download functions use selected interval
   - Activity log shows interval in all messages

**Key Features**:
- **Default Behavior Maintained**: Still defaults to 15-minute bars
- **User Preference Memory**: LocalStorage remembers interval selection
- **Clean Activity Messages**: Shows interval in all download confirmations
- **Dynamic UI Updates**: Descriptions update as interval changes
- **Smart Caching**: Clears appropriate data based on interval type

**Success Metrics**:
- Bob can now download Daily, Hourly, 30-minute, and 15-minute bars
- Clean selector interface with immediate visual feedback
- No breaking changes to existing functionality
- User preferences persist across sessions
- Activity log clearly shows what interval is being used

**Bob's Request**: "Make it Fucking Flawless" - ✅ COMPLETED
**Lucky Strikes Status**: Earned and ready for pickup! 🚬🔥