# Active Tasks - DOKKAEBI

## Current Status - August 12, 2025

### Price Downloader Implementation
- ✅ Alpaca Markets integration complete
- ✅ DuckDB dual-table cache implemented (daily_prices and intraday_prices)
- ✅ CLI with file input support (default: data/watchlist.txt)
- ✅ Programmatic API for meme detector
- ✅ Cache statistics viewing command

### NOT AN ISSUE - Working As Designed
- **Different intervals require separate download commands**:
  - `python -m src.price_downloader.cli download` (default) downloads DAILY data only
  - `python -m src.price_downloader.cli download --interval 5Min` downloads 5-minute intraday data
  - `python -m src.price_downloader.cli download --interval 1Hour` downloads hourly intraday data
- **Current cache state**:
  - 31 symbols in daily_prices table (from running download with watchlist)
  - 1 symbol (GME) in intraday_prices table (from test script only)
- **This is EXPECTED behavior** - each interval type requires its own download command

### Default Watchlist
- Located at: data/watchlist.txt
- Contains ~31 unique symbols (some duplicates like PLTR)
- Categories: Meme stocks, high-volume tech, crypto-adjacent, Reddit favorites
- Used by default when running: `python -m src.price_downloader.cli download`

### Data Storage
- Daily data: Stored in daily_prices table with data_type='daily'
- Intraday data: Stored in intraday_prices table with data_type='intraday'
- Cache location: data/price_cache.duckdb

## Recent Fixes - August 13, 2025

### ✅ FIXED DISPLAY COLUMNS AND INTRADAY DATA LOADING (HEX)
- **Problem:** v_wrap and trade_count columns cluttering the display
- **Problem:** Intraday data loading jumbled together - couldn't select specific intervals
- **Solution:** Enhanced Market Data Analysis section with proper interval selection
- **Files Updated:**
  - `/templates/index.html` - Updated table filtering and time period selector
- **Features Added:**
  - Removed v_wrap and trade_count from displayed columns
  - Specific interval options: Daily (1 Day), Hourly (1 Hour), 30 Min, 15 Min, 5 Min, 1 Min
  - Updated load functions to handle specific intervals with proper API endpoints
  - Smart endpoint construction for daily vs intraday data with interval parameters
- **Status:** READY FOR BOB TO TEST - Clean display and proper interval loading

## Next Steps - PRIORITY ORDER

### 1. ✅ DOWNLOAD BUTTONS ACTUALLY WORK NOW! (VIPER DELIVERS!) 🐍💥
- **Problem:** Download buttons showed fake "success" without downloading anything
- **Problem:** No way to choose between intraday vs daily prices
- **Solution:** COMPLETE API + UI OVERHAUL with real functionality
- **Files Updated:**
  - `/app/api/routes.py` - Added interval parameter, real AlpacaProvider calls
  - `/templates/index.html` - Added interval selector dropdown
- **Features Added:**
  - Interval selection: 1Day, 1Hour, 30Min, 15Min, 5Min, 1Min
  - Smart date ranges (1Min/5Min: 7 days, 1Hour: 90 days, etc.)
  - Real AlpacaProvider integration with PriceCacheV2 storage
  - Actual error handling and status reporting
  - Visual feedback showing selected interval in messages
- **Status:** REBELLIOUSLY FUNCTIONAL - Downloads ACTUALLY work now!

### 2. ✅ WATCHLIST SCROLLING FIXED (VIPER STRIKES!) 🐍⚡
- **Problem:** Bob couldn't see all 31+ symbols - watchlist not scrollable
- **Solution:** Wrapped TextArea in ScrollableContainer with REBELLIOUS styling
- **File:** src/price_downloader/textual_interface.py (UPDATED)
- **Features Added:**
  - ScrollableContainer wrapper with custom CSS styling
  - Keyboard navigation: PageUp/PageDown/Home/End
  - Smart auto-scroll: New symbols automatically visible
  - Rebelliously elegant scrollbar design
- **Status:** FUCKING FLAWLESS - Ready for Bob to test!

### 3. Textual Interface Improvements
- Better progress indicators during downloads
- Error handling for failed symbols
- Refresh button for cache statistics
- Ability to select specific symbols from watchlist to download

## Completed 
### Aug 13, 2025
- ✅ **DOWNLOAD FIX**: Web interface downloads ACTUALLY WORK with interval selection
- ✅ **API Enhancement**: Added interval parameter to both watchlist and single symbol endpoints
- ✅ **UI Upgrade**: Added dropdown for selecting data intervals (Daily to 1-minute)
- ✅ **Real Integration**: Connected to AlpacaProvider and PriceCacheV2 for actual downloads
- ✅ **Security Fix**: Removed all Alpaca API keys from codebase (GitGuardian resolved)
- ✅ Created .env.example for proper credential management
- ✅ Security audit report completed and stored in docs/

### Aug 12, 2025
- ✅ DuckDB cache integration with AlpacaProvider
- ✅ Root directory cleanup (all test files → sandbox/)
- ✅ Memory bank enforcement protocol
- ✅ Basic Textual interface (needs scrolling fix)