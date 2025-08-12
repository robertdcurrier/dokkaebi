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

## Next Steps - PRIORITY ORDER

### 1. FIX WATCHLIST SCROLLING (IMMEDIATE) 🔴
- **Bob's exact words:** "For starters, the watchlist isn't scrollable. So I can't see all of it."
- File: src/price_downloader/textual_interface.py
- Need scrollable container for watchlist display
- Test with: sandbox/test_textual_interface.py

### 2. Textual Interface Improvements
- Better progress indicators during downloads
- Error handling for failed symbols
- Refresh button for cache statistics
- Ability to select specific symbols from watchlist to download

## Completed Today (Aug 12)
- ✅ DuckDB cache integration with AlpacaProvider
- ✅ Root directory cleanup (all test files → sandbox/)
- ✅ Memory bank enforcement protocol
- ✅ Basic Textual interface (needs scrolling fix)