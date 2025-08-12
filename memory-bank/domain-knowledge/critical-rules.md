# Critical Rules - DOKKAEBI 📜

## SACRED PARAMETERS (NEVER CHANGE)

### HebbNet Architecture
- **Learning Rule**: Hebbian ONLY (no backpropagation)
- **Plasticity**: Spike-timing dependent
- **Updates**: Local weight updates only
- **No Gradient Descent**: This is biological, not traditional DL

### Trading Rules
- **Every Signal**: Must come from HebbNet
- **Every Decision**: Must use HebbNet output
- **No Mixing**: Cannot combine with traditional indicators
- **No Fallback**: Cannot revert to simple strategies

## CORE PRINCIPLE

If Bob says "use HebbNet for trading," then:
- Market predictions = HebbNet
- Entry signals = HebbNet
- Exit signals = HebbNet
- Risk management = HebbNet
- Position sizing = HebbNet

## FORBIDDEN ACTIONS

1. **NEVER** implement moving averages as primary signals
2. **NEVER** use RSI, MACD, or Bollinger Bands as decision makers
3. **NEVER** fall back to "simple" strategies when HebbNet seems complex
4. **NEVER** mix HebbNet with traditional ML (no sklearn, no TensorFlow)
5. **NEVER** claim "HebbNet isn't working" without extensive proof

## BOB'S EXPLICIT REQUIREMENTS

1. **"Algorithmic trading platform using our HebbNet lessons"**
2. **"Full-stack all the way"**
3. **"Make us some serious bank"**

## Technology Stack (IMMUTABLE)

- **Core Algorithm**: HebbNet (biological neural networks)
- **Language**: Python for trading engine
- **Data Source**: Alpaca Markets API ONLY (no Yahoo Finance)
- **Data Pipeline**: Real-time market data ingestion
- **Frontend**: React/TypeScript for dashboard
- **Database**: DuckDB for tick data (Diesel's preference)

## Data Provider Rules

1. **ONLY USE ALPACA MARKETS** - Yahoo Finance is banned
2. **No fallback providers** - Alpaca or nothing
3. **Professional data only** - No web scraping
4. **API credentials required** - Get FREE account at alpaca.markets
5. **Default watchlist at data/watchlist.txt** - Contains ~31 symbols for meme detection
6. **Dual-table DuckDB architecture** - Separate daily_prices and intraday_prices tables

## Cache Architecture (Per Diesel's Design)

1. **Two separate tables** - Never mix daily and intraday data
2. **Explicit metadata fields** - data_type='daily' or 'intraday' with CHECK constraints
3. **Automatic caching** - Every download stores to appropriate table
4. **View cache with**: `python -m src.price_downloader.cli cache`

## Code Organization Rules

1. **ALL test code MUST go in sandbox/ directory**
   - Test scripts → sandbox/
   - Demo scripts → sandbox/
   - Experimental code → sandbox/
   - One-off analysis → sandbox/
   - Debug utilities → sandbox/
   
2. **Root directory is for PRODUCTION ONLY**
   - Root = clean and organized
   - Root = production code only
   - Root = final implementations
   - NO test files in root
   - NO demo files in root

3. **File naming in sandbox/**
   - test_*.py for test scripts
   - demo_*.py for demos
   - check_*.py for validation scripts
   - debug_*.py for debugging
   - run_*.py for launchers

4. **Documentation goes in docs/**
   - ALL .md files → docs/
   - README files → docs/
   - Technical specs → docs/
   - NO documentation in root

## MANDATORY AGENT HANDOFF PROTOCOL

When using Task tool to hand off work to agents (Viper, Diesel, Repo, etc.):

1. **ALWAYS include file location rules in the prompt:**
   - "Put ALL test/demo scripts in sandbox/"
   - "Put ALL documentation in docs/"  
   - "Put ONLY production code in root or src/"

2. **COPY relevant memory bank rules into agent prompt**
   - Don't assume agents know the rules
   - Explicitly state WHERE files should go
   - Include consequences of violations

3. **CHECK agent output before presenting to Bob**
   - Did they put files in correct locations?
   - Did they follow the rules?
   - Fix violations before Bob sees them

**FAILURE TO INCLUDE THESE RULES = GUARANTEED VIOLATIONS**

Last Updated: August 12, 2025 - Added MANDATORY AGENT HANDOFF PROTOCOL
EOF < /dev/null