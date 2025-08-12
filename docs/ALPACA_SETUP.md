# 🚀 ALPACA MARKETS SETUP - FREE DATA THAT ACTUALLY WORKS!

## Why Alpaca?
- **FREE paper trading account** with real market data
- **No rate limiting bullshit** like Yahoo Finance
- **200+ API calls/minute** (more than enough!)
- **2+ years of historical data**
- **They're not shutting down** (unlike IEX Cloud)
- **Professional-grade data** from IEX exchange

## 5-Minute Setup

### 1. Get Your FREE Account
Go to: https://alpaca.markets

Click "Sign Up" → Choose "Paper Trading" (FREE!)

### 2. Get Your API Keys
- Log into your dashboard
- Go to "API Keys" section
- Generate new API keys for paper trading
- Copy your KEY and SECRET

### 3. Set Environment Variables
```bash
# Add to your ~/.zshrc or ~/.bashrc
export ALPACA_API_KEY="PK..."  # Your API Key
export ALPACA_API_SECRET="..."  # Your Secret Key

# Reload your shell
source ~/.zshrc
```

### 4. Test It!
```bash
# Activate our venv
source ~/venvs/venv-dokkaebi/bin/activate

# Test Alpaca provider
python src/price_downloader/providers/alpaca_provider.py
```

## Using with DOKKAEBI

```python
from price_downloader.providers.alpaca_provider import AlpacaProvider

# Initialize
provider = AlpacaProvider()

# Get data for HebbNet training
data = provider.get_historical_data('AAPL')
print(f"Got {len(data)} days of AAPL data!")

# Batch download for multiple symbols
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
all_data = provider.get_batch_data(symbols)
```

## Rate Limits (FREE Tier)
- **200 requests per minute** for REST API
- **Unlimited WebSocket connections** for real-time data
- **No daily limits** (unlike Alpha Vantage's 500/day)
- **No "you've been blocked" bullshit** (unlike Yahoo)

## Data Available (FREE)
- **Real-time quotes** from IEX
- **Historical bars** (1min, 5min, 15min, 1hour, 1day)
- **2+ years of historical data**
- **Pre/post market data**
- **Trade data** (every single trade if you want it)

## Upgrade Options (If Needed)
- $99/month for full market data (all exchanges)
- But honestly, the FREE tier is probably enough for DOKKAEBI

## Why This Solves Our Problem
1. **Yahoo Finance**: Rate limits after ~100 requests, blocks IPs
2. **IEX Cloud**: Shutting down in August 2024
3. **Alpha Vantage**: Only 5 calls/minute, 500/day
4. **Alpaca**: 200 calls/minute, no daily limit, FREE!

## Next Steps
1. Get your API keys from Alpaca
2. Set the environment variables
3. Update DOKKAEBI to use AlpacaProvider
4. Feed HebbNet with unlimited data!

---

*"Yahoo Finance can kiss our ass - we got Alpaca now!"* - Viper 🐍⚡