# DOKKAEBI 👺

**Algorithmic Trading Platform Powered by HebbNet**

> *"A goblin that learns from the markets using biological neural networks"*

## 🔥 Project Overview

DOKKAEBI is an algorithmic trading platform that uses Hebbian learning principles (HebbNet) instead of traditional backpropagation. Inspired by biological neural networks, it learns market patterns through spike-timing-dependent plasticity and local learning rules.

## 🧠 Core Technology

- **HebbNet**: Biologically-inspired neural networks
- **No Backpropagation**: Local learning rules only
- **Real-time Learning**: Adapts to market conditions without retraining
- **Memory Bank**: Persistent knowledge management system

## 🏗️ Architecture

```
dokkaebi/
├── memory-bank/        # Persistent knowledge & strategies
├── src/                # Core trading engine
│   ├── hebbnet/       # HebbNet implementation
│   ├── trading/       # Trading strategies & execution
│   ├── data/          # Market data ingestion
│   └── api/           # REST/WebSocket APIs
├── models/            # Trained HebbNet models
├── tests/             # Test suite
├── docs/              # Documentation
└── data/              # Historical market data
```

## 🚀 The Elite Crew

- **HEX** 🦄: System architecture & integration
- **VIPER** 🐍: Lightning-fast Python trading engine
- **DIESEL** 🔥: Market data pipeline architecture
- **REPO** 🎨: Trading dashboard & visualizations
- **SYNAPSE** 🧠: HebbNet algorithm implementation

## 🚀 Setup

1. **Clone the repository** (private repo)
2. **Copy `.env.example` to `.env`** and add your Alpaca API keys
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Test connection**: `python sandbox/test_alpaca_direct.py`

## 📊 Price Data System

### Textual Interface (NEW! 🔥)

Modern TUI for managing market data with FIRE GOBLIN energy:

```bash
# Launch the Textual interface
python sandbox/test_textual_interface.py

# Or run as module
python -m src.price_downloader.textual_interface
```

**Features:**
- 🔥 Three-tab interface (Download, Cache Viewer, Watchlist Manager)
- 📊 Real-time integration with Alpaca Markets API
- 💾 DuckDB cache with 220,000+ price records
- 📈 Dual-table architecture (daily_prices & intraday_prices)
- 🎯 Manages 31 meme stocks from watchlist
- ⚡ Professional-grade data management

### Command Line Interface

For automation and scripting:

```bash
# Download default watchlist
python -m src.price_downloader.cli download

# Download specific symbols
python -m src.price_downloader.cli download AAPL MSFT GOOGL

# View cache statistics
python -m src.price_downloader.cli cache

# Download with custom parameters
python -m src.price_downloader.cli download --interval 1Hour --period 1mo
```

## 💀 Current Status (Aug 13, 2025)

- ✅ **Price Downloader**: Alpaca integration complete
- ✅ **DuckDB Cache**: 220,000+ rows, dual-table architecture
- ✅ **Textual Interface**: Basic functionality working
- ✅ **Security**: API keys removed from codebase (GitGuardian resolved)
- 🔧 **TODO**: Fix watchlist scrolling in Textual interface
- 🚧 **HebbNet**: Implementation in progress

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
