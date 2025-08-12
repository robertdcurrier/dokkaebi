# System Behavior - DOKKAEBI

## Price Downloader Behavior

### Download Command Intervals
The download command works with ONE interval at a time:
- Each run downloads data for the specified interval only
- Default interval is '1Day' (daily data → daily_prices table)
- Intraday intervals ('5Min', '15Min', '30Min', '1Hour') → intraday_prices table

### Example Usage Patterns

**To populate both tables for all watchlist symbols:**
```bash
# Download daily data for all symbols
python -m src.price_downloader.cli download

# Download 5-minute data for all symbols  
python -m src.price_downloader.cli download --interval 5Min

# Download hourly data for all symbols
python -m src.price_downloader.cli download --interval 1Hour
```

**To download specific interval for specific symbols:**
```bash
# Daily data for GME and AMC
python -m src.price_downloader.cli download GME AMC

# 5-minute data for GME
python -m src.price_downloader.cli download GME --interval 5Min
```

### Cache Storage Rules
- Daily data (interval='1Day') → stored in `daily_prices` table
- Intraday data (any other interval) → stored in `intraday_prices` table
- Each table has explicit `data_type` field for safety
- Tables are completely separate per Diesel's architecture

### Why We See Different Symbol Counts
If you see 31 symbols in daily but only 1 in intraday, it means:
- Someone ran `download` command (which downloaded daily for all 31 watchlist symbols)
- Someone only downloaded intraday data for 1 symbol (probably from a test script)
- This is NORMAL - not a bug!

### View What's in Cache
```bash
python -m src.price_downloader.cli cache
```

Shows:
- How many symbols in each table
- Total row counts
- Date/time ranges
- Cache file size

## Remember
Bob might ask "why only 1 symbol in intraday?" - The answer is: "Because we only downloaded intraday data for that one symbol. Run `download --interval 5Min` to get intraday for all watchlist symbols."

Last Updated: August 12, 2025