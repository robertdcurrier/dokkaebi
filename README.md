# DOKKAEBI 👺

**Professional Web-Based Trading Terminal**

> *"From broken TUIs to production-ready web application - A goblin's evolution"*

## 🔥 What DOKKAEBI Is Now (August 13, 2025)

DOKKAEBI is a **professional web-based trading terminal** built for market data management and analysis. It serves as the foundation for future HebbNet (biologically-inspired neural network) trading strategy development.

**🎯 Key Features:**
- **Web Interface**: Professional trading terminal accessible via browser
- **Real Market Data**: 15-minute bars from Alpaca Markets with 16-minute delay
- **DuckDB Storage**: Fast local database with 220,000+ price records
- **Live Operations**: Real downloads, not fake success messages
- **Activity Logging**: Real-time operation tracking and status updates

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Add your Alpaca API credentials to .env
ALPACA_API_KEY=your_key_here
ALPACA_API_SECRET=your_secret_here

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Trading Terminal
```bash
# Start the web application
python main.py

# Open browser to: http://localhost:8000
```

### 3. Ready to Trade Data!
- ✅ **Green status**: Alpaca connection confirmed
- ✅ **Download data**: Choose date range, download watchlist or specific symbols
- ✅ **View market data**: Recent 15-minute bars in professional tables
- ✅ **Manage watchlist**: Add/remove symbols from your trading universe

## 🏗️ System Architecture

### Current Production Architecture
```
dokkaebi/
├── main.py                 # FastAPI web application
├── app/
│   ├── api/routes.py      # 8 production API endpoints
│   └── core/config.py     # Configuration management
├── templates/
│   └── index.html         # Professional web interface
├── data/
│   ├── watchlist.txt      # 31 meme stock symbols
│   └── price_cache.duckdb # 220,000+ price records
├── src/price_downloader/  # Core market data components
├── memory-bank/           # Persistent knowledge system
└── sandbox/               # Development/testing files
```

### Technology Stack
- **Backend**: FastAPI + Python 3.9+
- **Database**: DuckDB (embedded, fast queries)
- **Market Data**: Alpaca Markets API (15-minute bars)
- **Frontend**: Modern HTML5 + JavaScript (no framework bloat)
- **Styling**: Professional blue/grey trading terminal theme

## 📊 Data Specifications

### 15-Minute Bars (Primary Data)
- **Source**: Alpaca Markets API (free tier)
- **Frequency**: 15-minute intervals
- **Delay**: 16 minutes from real-time (API limitation)
- **Coverage**: US equities, 31 meme stocks in default watchlist
- **Storage**: DuckDB `intraday_prices` table

### Default Watchlist (31 Symbols)
Curated collection of high-volume, meme-worthy stocks:
- **Meme Stocks**: GME, AMC, BBBY, PLTR
- **Tech Giants**: AAPL, MSFT, GOOGL, TSLA  
- **Market ETFs**: SPY, QQQ, IWM
- **Reddit Favorites**: Various trending symbols

## 🎛️ Web Interface Features

### Professional Trading Terminal Layout
- **Fixed Command Bar**: System status and connection indicators
- **Market Pulse**: Real-time database statistics and controls
- **Data Acquisition**: Download controls with date range selection
- **Market Data Analysis**: Clean, professional data tables
- **Watchlist Management**: Add/remove symbols with file sync
- **Activity Feed**: Real-time operation logging (fixed right panel)

### Data Download Options
- **Latest Bars**: Get most recent data for all symbols (recommended)
- **Historical Ranges**: 1 day, 7 days, 30 days, 6 months, 1 year
- **Single Symbol**: Target specific stocks for focused analysis
- **Batch Processing**: Download entire watchlist efficiently

### Professional Styling
- **Dark theme**: Easy on trader's eyes during long sessions
- **Information density**: Maximum useful data, minimal fluff
- **No distractions**: Removed flashy animations and popup effects
- **Responsive design**: Works on desktop and mobile devices

## 🔗 API Endpoints (8 Production Routes)

### Data Management
- `POST /api/download/watchlist` - Download all watchlist symbols
- `POST /api/download/symbol/{symbol}` - Download single symbol
- `GET /api/cache/stats` - Database statistics
- `GET /api/cache/recent` - Recent market data display
- `DELETE /api/cache/clear` - Clear all cached data

### Watchlist & System
- `GET /api/watchlist` - Load current watchlist
- `POST /api/watchlist` - Update watchlist symbols  
- `GET /api/test/connection` - Test Alpaca API connection

## 💡 How to Use DOKKAEBI

### Daily Workflow
1. **Start Application**: `python main.py`
2. **Check Connection**: Verify green status in web interface
3. **Download Latest Data**: Use "Latest" range for recent bars
4. **Analyze Data**: Load and filter market data tables
5. **Manage Symbols**: Update watchlist as market conditions change

### Data Management Best Practices
- **Use "Latest" downloads** for regular data updates (most efficient)
- **Historical downloads** for backtesting and analysis
- **Clear cache periodically** to manage disk space
- **Monitor activity feed** for operation status and errors

### Professional Usage
- **Real-time status**: All operations logged with timestamps
- **Error handling**: System continues processing if individual symbols fail
- **Data validation**: Automatic symbol cleanup and format checking
- **Performance monitoring**: Database statistics and cache management

## 🚨 Important Notes & Limitations

### Alpaca Free Tier Reality
- ⏰ **15-minute delay**: Cannot access data newer than 16 minutes
- 📊 **15-minute bars**: Optimal frequency for free tier limits  
- 🎯 **US Equities only**: No forex, crypto, or international markets
- 🔄 **Rate limits**: 200 requests/minute (managed automatically)

### System Limitations
- **Single data provider**: Only Alpaca Markets currently
- **Local database**: Not cloud-synchronized
- **Web interface**: Desktop optimized, mobile usable
- **No trading execution**: Pure data management system

### Known Working Parameters (SACRED - Don't Change!)
- **Interval**: 15Min (optimal for Alpaca free tier)
- **Delay**: 16 minutes from current time
- **Data clearing**: Old data removed before new downloads
- **Cache strategy**: Single-table storage for recent data

## 🔮 Future Development (Roadmap)

### Phase 2: HebbNet Integration (Next Priority)
DOKKAEBI will integrate biologically-inspired neural networks for:
- **Pattern Recognition**: Identify market anomalies using Hebbian learning
- **Signal Generation**: Trading signals from biological neural networks  
- **Adaptive Learning**: Real-time strategy adaptation without retraining
- **Memory Persistence**: Strategy knowledge stored in memory-bank

### Phase 3: Advanced Features
- **Strategy Backtesting**: Historical performance analysis
- **Risk Management**: Position sizing and stop-loss automation
- **Multi-provider Support**: Add IEX Cloud, Yahoo Finance
- **Cloud Deployment**: Web-hosted version for remote access

## 📈 Current Status & Achievements

### ✅ Production Ready Features (August 13, 2025)
- **Professional web interface**: Replaces broken TUI experiments
- **Real API integration**: Actual Alpaca Market data downloads
- **220,000+ price records**: Comprehensive historical dataset
- **8 working API endpoints**: Full CRUD operations for market data
- **Activity logging**: Transparent operation tracking
- **Professional styling**: Clean, trader-friendly interface

### 🔧 Development Journey Highlights
- **Latest Mode Bug**: Fixed sneaky caching issue that reported wrong record counts
- **UI Overhaul**: From broken Textual interfaces to professional web app
- **Real Integration**: Replaced fake success messages with actual data operations
- **Architecture Cleanup**: Removed fragmented TUI files, consolidated to web approach

## ⚠️ SACRED RULES (NEVER BREAK THESE!)

1. **NEVER ABANDON HEBBNET**: All future trading decisions must use biological neural networks
2. **MEMORY BANK FIRST**: Always check memory-bank/ before making changes
3. **REAL OPERATIONS ONLY**: No fake success messages or simulated data
4. **15-MINUTE STANDARD**: Don't change the working 15-minute bar configuration
5. **WEB INTERFACE PRIORITY**: Continue web-based development, avoid TUI experiments

## 🎯 Mission Statement

DOKKAEBI provides professional-grade market data management with a clean, reliable interface that serious traders would actually use. It serves as the foundation for revolutionary HebbNet trading strategies while maintaining the high standards required for financial applications.

**Core Values:**
- **Professional Quality**: Interface and functionality suitable for real trading
- **Data Integrity**: Real operations with verifiable results
- **Biological Intelligence**: Future HebbNet integration for unique market insights
- **Persistent Memory**: Knowledge accumulation across trading sessions

---

## 🚀 Get Started Now

```bash
# Quick start - 3 commands to trading terminal
git clone [repo-url]
cp .env.example .env  # Add your Alpaca keys
python main.py        # Launch at http://localhost:8000
```

**Ready to dominate the markets with biological intelligence!** 👺💰

---

*"From broken TUI experiments to production trading terminal - Evolution through iteration."* - DOKKAEBI Development Team, August 13, 2025

## ⚠️ SACRED RULES

1. **NEVER ABANDON HEBBNET**: Every prediction, every signal, every trading decision MUST use HebbNet. No reverting to moving averages, RSI, or traditional indicators without explicit approval.

2. **MEMORY BANK FIRST**: Check memory-bank/ before ANY action. No exceptions.

3. **FILE ORGANIZATION**: Test code → sandbox/, Docs → docs/, Production → src/

## 🎯 Mission

Build a trading platform that:
1. Uses ONLY biological learning principles
2. Adapts in real-time to market dynamics
3. Maintains persistent memory of successful strategies
4. Generates consistent alpha through unique insights

---

*"Let the goblin feast on market inefficiencies!"* 👺💰
