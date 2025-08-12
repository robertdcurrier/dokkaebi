#!/usr/bin/env python3
"""
Integration Example - Price Downloader + Meme Scanner

Shows how the DOKKAEBI price downloader integrates with the existing
meme scanner for complete market data pipeline.

Viper's integration showcase - because everything works together.
"""

import sys
from pathlib import Path

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))

from price_downloader import PriceDownloader, TickerUniverse
from price_downloader.filters.market_filters import (
    LiquidityFilter, 
    PriceFilter,
    CompositeFilter
)

def create_hebbnet_universe():
    """
    Create an optimal ticker universe for HebbNet training.
    
    Returns list of high-quality, liquid stocks perfect for
    algorithmic trading.
    """
    print("🧠 Creating HebbNet-optimized ticker universe...")
    
    # Fetch comprehensive ticker lists
    ticker_universe = TickerUniverse(cache_dir="sandbox/ticker_cache")
    
    # Get major exchanges
    all_tickers = ticker_universe.get_combined_universe([
        'NASDAQ', 'NYSE'
    ])
    
    print(f"📊 Total universe: {len(all_tickers)} tickers")
    
    # Download recent price data for filtering
    print("📥 Downloading recent price data for filtering...")
    
    with PriceDownloader(cache_path="sandbox/hebbnet_cache.duckdb") as downloader:
        # Download 1 week of data for filtering  
        results = downloader.download_batch(
            all_tickers[:100],  # Limit for demo
            period="1wk",
            show_progress=True
        )
        
        # Get latest prices for filtering
        latest_prices = downloader.cache.get_latest_prices()
        
    if latest_prices.empty:
        print("❌ No price data available for filtering")
        return []
        
    print(f"💾 Got price data for {len(latest_prices)} symbols")
    
    # Apply HebbNet-specific filters
    hebbnet_filters = [
        # Minimum liquidity for safe trading
        LiquidityFilter(
            min_dollar_volume=5_000_000,  # $5M daily volume
            min_volume=100_000,           # 100k shares
            min_price=5.0                 # $5+ price
        ),
        
        # Avoid penny stocks and super expensive stocks
        PriceFilter(min_price=5.0, max_price=500.0)
    ]
    
    composite_filter = CompositeFilter(hebbnet_filters, logic='AND')
    
    print("🔍 Applying HebbNet quality filters...")
    filtered_data = composite_filter.apply(latest_prices)
    
    # Extract symbols
    hebbnet_symbols = filtered_data['symbol'].tolist()
    
    print(f"✅ HebbNet universe: {len(hebbnet_symbols)} high-quality symbols")
    print(f"📈 Sample symbols: {hebbnet_symbols[:10]}")
    
    # Show filter statistics
    stats = composite_filter.get_filter_stats()
    for filter_name, filter_stats in stats.items():
        filter_rate = filter_stats['filter_rate_percent']
        print(f"   {filter_name}: {filter_rate:.1f}% filtered out")
    
    return hebbnet_symbols


def demo_price_pipeline():
    """Demonstrate complete price data pipeline."""
    print("\n🚀 DOKKAEBI Price Pipeline Demo")
    print("=" * 50)
    
    # Step 1: Create optimal universe
    symbols = create_hebbnet_universe()
    
    if not symbols:
        print("❌ No symbols in universe")
        return
        
    # Step 2: Download historical data for HebbNet training
    print(f"\n🎯 Downloading training data for top {min(10, len(symbols))} symbols...")
    
    training_symbols = symbols[:10]  # Top 10 for demo
    
    with PriceDownloader(cache_path="sandbox/hebbnet_cache.duckdb") as downloader:
        # Download 1 year of daily data
        training_data = downloader.download_batch(
            training_symbols,
            period="1y",
            interval="1d",
            show_progress=True
        )
        
        # Show data summary
        print("\n📊 Training Data Summary:")
        for symbol, data in training_data.items():
            if data is not None and not data.empty:
                date_range = f"{data.index.min().date()} to {data.index.max().date()}"
                print(f"   {symbol}: {len(data)} bars ({date_range})")
                
                # Calculate some basic features HebbNet might use
                data['returns'] = data['close'].pct_change()
                data['volatility'] = data['returns'].rolling(20).std()
                data['volume_ma'] = data['volume'].rolling(20).mean()
                
                recent_vol = data['volatility'].iloc[-1]
                recent_vol_ma = data['volume_ma'].iloc[-1]
                
                print(f"      Recent volatility: {recent_vol:.4f}")
                print(f"      Avg volume (20d): {recent_vol_ma:,.0f}")
    
    print("\n✅ Price pipeline demo complete!")
    print("🧠 Data is ready for HebbNet training and trading!")


if __name__ == '__main__':
    try:
        demo_price_pipeline()
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()