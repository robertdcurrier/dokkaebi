# DOKKAEBI Final State Documentation

**Last Updated:** August 13, 2025  
**Status:** Production Ready Web Application  
**Architecture:** FastAPI + DuckDB + Alpaca Markets  

## 🎯 What DOKKAEBI Is

DOKKAEBI is a professional web-based trading terminal designed for algorithmic trading research and market data management. It serves as the data foundation for future HebbNet (biologically-inspired neural network) trading strategy development.

## 🏗️ System Architecture

### Core Components
1. **Web Interface** (`main.py` + `templates/index.html`)
   - Professional trading terminal UI
   - Real-time operation logging
   - Responsive design for desktop/mobile

2. **API Layer** (`app/api/routes.py`)
   - FastAPI backend with 8 production endpoints
   - Real market data integration
   - Comprehensive error handling

3. **Data Storage** (`PriceCacheV2` + DuckDB)
   - Dual-table architecture (daily + intraday)
   - Currently storing 220,000+ price records
   - Fast query performance for analysis

4. **Market Data Provider** (`AlpacaProvider`)
   - Integration with Alpaca Markets API
   - 15-minute bars with 16-minute delay (free tier)
   - Automatic caching and data management

## 📊 Data Specifications

### Primary Data Type: 15-Minute Bars
- **Interval**: 15 minutes (optimal for Alpaca free tier)
- **Delay**: 16 minutes from real-time (API limitation)
- **Fields**: Symbol, Timestamp, OHLCV (Open, High, Low, Close, Volume)
- **Storage**: DuckDB `intraday_prices` table

### Database Schema

#### `intraday_prices` Table (Primary)
```sql
CREATE TABLE intraday_prices (
    symbol VARCHAR,           -- Stock symbol (e.g., 'AAPL')
    bar_timestamp TIMESTAMP,  -- 15-minute bar timestamp
    open_price DOUBLE,       -- Opening price
    high_price DOUBLE,       -- Highest price in period
    low_price DOUBLE,        -- Lowest price in period  
    close_price DOUBLE,      -- Closing price
    volume BIGINT,           -- Share volume
    timeframe VARCHAR,       -- '15min'
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `daily_prices` Table (Legacy Support)
```sql
CREATE TABLE daily_prices (
    symbol VARCHAR,          -- Stock symbol
    trading_date DATE,       -- Trading date
    open_price DOUBLE,       -- Daily open
    high_price DOUBLE,       -- Daily high
    low_price DOUBLE,        -- Daily low
    close_price DOUBLE,      -- Daily close
    volume BIGINT,           -- Daily volume
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🎛️ User Interface Features

### Command Bar (Fixed Top)
- **System Status**: DOKKAEBI TRADING TERMINAL branding
- **Connection Indicator**: Real-time Alpaca API connection status
- **Always Visible**: Remains fixed during scrolling

### Market Pulse Dashboard
- **Total Symbols**: Count of unique symbols in database
- **Total Records**: Combined daily + intraday record count  
- **Cache Size**: Database file size in MB
- **Actions**: Update stats, clear cache

### Data Acquisition Panel
- **Date Range Options**: Latest, 1 Day, 7 Days, 30 Days, 6 Months, 1 Year
- **Download Modes**:
  - **Watchlist Download**: Process all symbols from `data/watchlist.txt`
  - **Single Symbol**: Download specific symbol data
- **Real-time Feedback**: Operation status and progress

### Watchlist Management
- **Current Symbols**: Display active symbol count
- **Watchlist Editor**: Add/remove symbols
- **File Integration**: Automatically saves to `data/watchlist.txt`

### Market Data Analysis
- **Data Display**: Recent 15-minute bars in professional table
- **Symbol Filtering**: Filter data by specific symbols
- **Clean Presentation**: Removed clutter columns (v_wrap, trade_count, etc.)

### Activity Feed (Fixed Right Panel)
- **Real-time Logging**: All operations logged with timestamps
- **Message Types**: INFO, SUCCESS, ERROR, TRADE
- **Scroll Management**: Limited to 100 messages
- **Professional Styling**: Clean, readable format

## 🔗 API Endpoints

### Data Download Endpoints
1. **`POST /api/download/watchlist?days_back={n}`**
   - Downloads 15-minute data for all watchlist symbols
   - `days_back=0`: Latest bars only (optimal)
   - `days_back=1-365`: Historical data

2. **`POST /api/download/symbol/{symbol}?days_back={n}`**
   - Downloads 15-minute data for single symbol
   - Same date range options as watchlist

### Data Access Endpoints  
3. **`GET /api/cache/stats`**
   - Returns database statistics (symbols, records, file size)

4. **`GET /api/cache/recent?symbol={symbol}&limit={n}`**
   - Returns recent 15-minute bars
   - Optional symbol filtering

### Management Endpoints
5. **`GET /api/watchlist`**
   - Returns current watchlist symbols

6. **`POST /api/watchlist`**
   - Updates watchlist with new symbols

7. **`DELETE /api/cache/clear`**
   - Clears all cached price data (destructive)

### Utility Endpoints
8. **`GET /api/test/connection`**
   - Tests Alpaca API connection status

## ⚙️ Configuration & Setup

### Environment Variables Required
```bash
ALPACA_API_KEY=your_alpaca_key
ALPACA_API_SECRET=your_alpaca_secret
```

### File Structure
```
dokkaebi/
├── main.py                 # FastAPI application entry point
├── app/
│   ├── api/routes.py      # API endpoint implementations
│   └── core/config.py     # Configuration management
├── templates/
│   └── index.html         # Web interface
├── data/
│   ├── watchlist.txt      # Symbol list (31 meme stocks)
│   └── price_cache.duckdb # Database file
├── src/price_downloader/  # Core data components
└── sandbox/               # Development/testing files
```

### Default Watchlist (31 Symbols)
Located at `data/watchlist.txt`, includes:
- **Meme Stocks**: GME, AMC, BBBY, PLTR
- **Tech Giants**: AAPL, MSFT, GOOGL, TSLA
- **High Volume**: SPY, QQQ, IWM
- **Reddit Favorites**: Various trending symbols

## 🚀 How to Use DOKKAEBI

### 1. Start the System
```bash
cd /Users/rdc/src/dokkaebi
python main.py
```
- Starts FastAPI server on `http://localhost:8000`
- Shows startup messages with documentation links

### 2. Access Web Interface
- Open browser to `http://localhost:8000`
- Check connection status (green = connected)
- All features accessible through web interface

### 3. Download Market Data
- **Choose date range**: Latest recommended for regular use
- **Watchlist download**: Gets data for all 31 symbols
- **Single symbol**: Target specific stocks
- **Monitor activity feed**: Real-time operation status

### 4. View Market Data
- **Load Data**: Shows recent 15-minute bars
- **Filter by Symbol**: Focus on specific stocks  
- **Professional tables**: Clean, readable format

### 5. Manage Symbols
- **Load current watchlist**: See active symbols
- **Update watchlist**: Add/remove symbols
- **File sync**: Changes saved to `data/watchlist.txt`

## ⚡ Performance Characteristics

### Download Performance
- **Watchlist (31 symbols)**: ~30-60 seconds
- **Single symbol**: ~2-5 seconds
- **Rate limits**: Managed automatically
- **Error handling**: Continues processing if individual symbols fail

### Database Performance  
- **Query speed**: Sub-second for most operations
- **Storage**: ~40MB for 220,000+ records
- **Indexing**: Optimized for timestamp and symbol queries

### Web Interface Performance
- **Page load**: Instant on local server
- **Data refresh**: Real-time updates
- **Responsive**: Works on desktop and mobile

## ⚠️ Known Limitations

### Alpaca Free Tier Constraints
- **15-minute delay**: Cannot access data newer than 16 minutes ago
- **Rate limits**: 200 requests/minute (managed automatically)
- **Data scope**: US equities only (no forex, crypto, futures)

### Current System Limitations
- **Single data provider**: Only Alpaca Markets (could be extended)
- **15-minute intervals only**: Other intervals possible but not implemented
- **No trading execution**: Pure data management (as designed)
- **Local database**: Not cloud-synchronized

### User Interface Limitations
- **Desktop optimized**: Mobile usable but not perfect
- **Single session**: No multi-user support
- **No data export**: Database queries only

## 🔮 Future Development Roadmap

### Phase 2: HebbNet Integration (Next)
- **Neural network integration**: Add HebbNet trading signal generation
- **Pattern recognition**: Implement biological learning algorithms
- **Anomaly detection**: Real-time market pattern analysis
- **Signal storage**: Extend database for trading signals

### Phase 3: Trading Strategy Development
- **Strategy backtesting**: Historical performance analysis  
- **Risk management**: Position sizing and stop-loss logic
- **Portfolio management**: Multi-symbol strategy coordination

### Phase 4: Trading Execution (Future)
- **Paper trading**: Simulated order execution
- **Live trading**: Real order placement (when ready)
- **Performance tracking**: Strategy performance metrics

### Phase 5: Advanced Features
- **Multi-provider support**: Add IEX, Yahoo Finance, etc.
- **Cloud deployment**: Web-hosted version
- **Advanced analytics**: Custom indicators and analysis tools
- **Multi-user support**: Team collaboration features

## 🛡️ Security & Reliability

### Credential Management
- **Environment variables**: API keys not stored in code
- **Example file**: `.env.example` provided for setup
- **No hardcoded secrets**: GitGuardian compliant

### Error Handling
- **API failures**: Graceful degradation and user notification
- **Network issues**: Retry logic and timeout handling
- **Data validation**: Symbol cleanup and format checking
- **Database errors**: Comprehensive exception handling

### Data Integrity
- **Cache consistency**: Old data cleared before new downloads
- **Transaction safety**: Database operations are atomic
- **Backup strategy**: Database file can be backed up easily

## 📈 Success Metrics

### Data Management Success
- ✅ **220,000+ price records** stored and accessible
- ✅ **31 symbols** actively monitored
- ✅ **Real-time downloads** working reliably
- ✅ **Professional interface** for data management

### Technical Architecture Success  
- ✅ **8 API endpoints** fully functional
- ✅ **Sub-second query performance** on large dataset
- ✅ **Professional web interface** with real-time logging
- ✅ **Clean codebase** with proper error handling

### User Experience Success
- ✅ **Single interface** replaces multiple broken TUIs
- ✅ **Real operations** replace fake success messages
- ✅ **Professional appearance** suitable for trading use
- ✅ **Comprehensive logging** for operation transparency

## 🎯 DOKKAEBI Mission Statement

DOKKAEBI serves as the data foundation for algorithmic trading research using biologically-inspired neural networks (HebbNet). It provides professional-grade market data management with a clean, reliable interface that traders would actually want to use.

The system prioritizes:
1. **Data integrity**: Real operations, verified results
2. **Professional usability**: Clean interface, reliable performance  
3. **Extensible architecture**: Ready for advanced trading features
4. **Transparent operations**: Comprehensive logging and feedback

DOKKAEBI is now ready to support serious algorithmic trading development while maintaining the high standards required for financial applications.

---

*"A professional trading platform requires professional data management. DOKKAEBI delivers both."* - August 13, 2025