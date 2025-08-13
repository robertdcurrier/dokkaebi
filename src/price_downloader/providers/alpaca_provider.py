"""
Alpaca Markets Data Provider - The REAL solution to our data problems!

FREE paper trading account with real market data.
No more Yahoo Finance bullshit!

Viper's implementation - REBELLIOUSLY ELEGANT as always.
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Literal

import pandas as pd
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from ..storage.cache_v2 import PriceCacheV2

logger = logging.getLogger(__name__)


class AlpacaProvider:
    """
    Alpaca Markets data provider.
    
    FREE tier includes:
    - Real-time IEX data
    - 2+ years historical data
    - 200 calls/minute (plenty!)
    - No shutdown risk (they're profitable)
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None,
                 cache_enabled: bool = True,
                 cache_path: str = "data/price_cache.duckdb"):
        """
        Initialize Alpaca client with DuckDB caching.
        
        Args:
            api_key: Alpaca API key (or set ALPACA_API_KEY env var)
            api_secret: Alpaca API secret (or set ALPACA_API_SECRET env var)
            cache_enabled: Enable DuckDB caching
            cache_path: Path to DuckDB database
        """
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.api_secret = api_secret or os.getenv('ALPACA_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "Alpaca API credentials required! "
                "Get FREE account at https://alpaca.markets\n"
                "Then set ALPACA_API_KEY and ALPACA_API_SECRET"
            )
        
        # Initialize the historical data client
        self.client = StockHistoricalDataClient(
            self.api_key,
            self.api_secret
        )
        
        # Initialize DuckDB cache
        self.cache_enabled = cache_enabled
        self.cache = PriceCacheV2(cache_path) if cache_enabled else None
        
    def get_historical_data(
        self,
        symbol: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        interval: str = '1Day',
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get historical price data from Alpaca.
        
        Args:
            symbol: Stock symbol
            start: Start date
            end: End date
            interval: Time interval (1Day, 1Hour, 5Min, etc.)
            limit: Maximum number of bars to return (most recent)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Default to last year if no dates provided
            if not start:
                start = datetime.now() - timedelta(days=365)
            if not end:
                end = datetime.now()
            
            # Map interval strings to Alpaca TimeFrame
            if interval == '1Day':
                timeframe = TimeFrame.Day
            elif interval == '1Hour':
                timeframe = TimeFrame.Hour
            elif interval == '5Min':
                timeframe = TimeFrame(5, TimeFrameUnit.Minute)
            elif interval == '15Min':
                timeframe = TimeFrame(15, TimeFrameUnit.Minute)
            elif interval == '30Min':
                timeframe = TimeFrame(30, TimeFrameUnit.Minute)
            else:
                timeframe = TimeFrame.Day
            
            # Create request
            request_params = {
                'symbol_or_symbols': symbol,
                'timeframe': timeframe
            }
            
            # Add date range or limit (limit takes precedence)
            if limit is not None:
                request_params['limit'] = limit
            else:
                request_params['start'] = start
                request_params['end'] = end
            
            request = StockBarsRequest(**request_params)
            
            # Get data
            bars = self.client.get_stock_bars(request)
            
            # Convert to DataFrame
            if bars and hasattr(bars, 'data') and symbol in bars.data:
                bar_list = bars.data[symbol]
                if bar_list:
                    # Convert to DataFrame
                    data = {
                        'Open': [bar.open for bar in bar_list],
                        'High': [bar.high for bar in bar_list],
                        'Low': [bar.low for bar in bar_list],
                        'Close': [bar.close for bar in bar_list],
                        'Volume': [bar.volume for bar in bar_list],
                        'Timestamp': [bar.timestamp for bar in bar_list]
                    }
                    df = pd.DataFrame(data)
                    df.set_index('Timestamp', inplace=True)
                    
                    # Store in cache based on interval
                    if self.cache_enabled and self.cache and not df.empty:
                        self._store_in_cache(df, symbol, interval)
                    
                    return df
            
            logger.warning(f"No data returned for {symbol}")
            return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Alpaca API error for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_batch_data(
        self,
        symbols: List[str],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        interval: str = '1Day',
        limit: Optional[int] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Get data for multiple symbols efficiently.
        
        Args:
            symbols: List of stock symbols
            start: Start date
            end: End date
            interval: Time interval
            limit: Maximum number of bars to return (most recent)
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        results = {}
        
        # Default dates
        if not start:
            start = datetime.now() - timedelta(days=365)
        if not end:
            end = datetime.now()
        
        # Map interval
        if interval == '1Day':
            timeframe = TimeFrame.Day
        elif interval == '1Hour':
            timeframe = TimeFrame.Hour
        elif interval == '5Min':
            timeframe = TimeFrame(5, TimeFrameUnit.Minute)
        elif interval == '15Min':
            timeframe = TimeFrame(15, TimeFrameUnit.Minute)
        elif interval == '30Min':
            timeframe = TimeFrame(30, TimeFrameUnit.Minute)
        else:
            timeframe = TimeFrame.Day
        
        try:
            # Alpaca supports batch requests!
            request_params = {
                'symbol_or_symbols': symbols,
                'timeframe': timeframe
            }
            
            # Add date range or limit (limit takes precedence)
            if limit is not None:
                request_params['limit'] = limit
            else:
                request_params['start'] = start
                request_params['end'] = end
            
            request = StockBarsRequest(**request_params)
            
            bars = self.client.get_stock_bars(request)
            
            # Process each symbol
            for symbol in symbols:
                if symbol in bars:
                    df = bars[symbol].df
                    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume',
                                 'TradeCount', 'VWAP']
                    results[symbol] = df
                else:
                    results[symbol] = pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"Alpaca batch request error: {e}")
            # Fall back to individual requests
            for symbol in symbols:
                results[symbol] = self.get_historical_data(
                    symbol, start, end, interval, limit
                )
        
        return results
    
    def _store_in_cache(self, df: pd.DataFrame, symbol: str, interval: str) -> None:
        """
        Store data in the appropriate cache table.
        
        Args:
            df: DataFrame with price data
            symbol: Stock symbol
            interval: Time interval to determine table
        """
        try:
            # Determine if this is daily or intraday data
            if interval == '1Day':
                # Store in daily_prices table
                self.cache.store_daily_prices(df, symbol)
                logger.info(f"Stored {len(df)} daily records for {symbol} in DuckDB")
            else:
                # Map interval to timeframe for intraday table
                timeframe_map = {
                    '1Hour': '1hour',
                    '5Min': '5min',
                    '15Min': '15min',
                    '30Min': '30min',
                }
                timeframe = timeframe_map.get(interval, '5min')
                self.cache.store_intraday_prices(df, symbol, timeframe)
                logger.info(f"Stored {len(df)} intraday records for {symbol} in DuckDB")
        except Exception as e:
            logger.error(f"Failed to cache data for {symbol}: {e}")
    
    def get_latest_bar(self, symbol: str, interval: str = '15Min') -> Optional[pd.DataFrame]:
        """
        Get the latest bar for a symbol (FIXED METHOD).
        
        This method fixes the 4:00 AM data bug by using today's market range
        and taking the last bar from the DataFrame.
        
        IMPORTANT: This method only caches the single latest bar to avoid
        the discrepancy between records_downloaded (1) and actual cached records (many).
        
        Args:
            symbol: Stock symbol
            interval: Time interval (15Min recommended)
            
        Returns:
            DataFrame with single latest bar or None
        """
        try:
            # Temporarily disable caching to prevent full day caching
            original_cache_enabled = self.cache_enabled
            self.cache_enabled = False
            
            # Get today's market hours data
            now = datetime.now(timezone.utc)
            today = now.date()
            
            # Market opens at 9:30 AM EDT = 13:30 UTC
            start_time = datetime.combine(today, datetime.min.time()).replace(
                tzinfo=timezone.utc
            ) + timedelta(hours=13, minutes=30)
            end_time = now - timedelta(minutes=16)  # Account for API delay
            
            # Get all bars for today's market session (without caching)
            df = self.get_historical_data(
                symbol=symbol,
                start=start_time,
                end=end_time,
                interval=interval
            )
            
            # Restore original cache setting
            self.cache_enabled = original_cache_enabled
            
            if df.empty:
                logger.warning(f"No data returned for latest {symbol}")
                return None
            
            # Return only the LATEST bar (last row)
            latest_df = df.tail(1).copy()
            
            # Cache only the single latest bar (not the full day's data)
            if self.cache_enabled and self.cache and not latest_df.empty:
                self._store_in_cache(latest_df, symbol, interval)
            
            logger.info(f"Latest {symbol} bar: {latest_df.index[0]} - ${latest_df['Close'].iloc[0]:.2f}")
            return latest_df
            
        except Exception as e:
            logger.error(f"Error getting latest bar for {symbol}: {e}")
            return None

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest price for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Latest price or None
        """
        try:
            # Use the fixed latest bar method
            latest_df = self.get_latest_bar(symbol, '15Min')
            
            if latest_df is not None and not latest_df.empty:
                return float(latest_df['Close'].iloc[0])
            
            # Fallback to old method if latest bar fails
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                limit=1
            )
            
            bars = self.client.get_stock_bars(request)
            
            if symbol in bars and len(bars[symbol]) > 0:
                return bars[symbol][-1].close
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest price for {symbol}: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test if Alpaca connection works."""
        try:
            # Try to get a simple quote
            from alpaca.data.requests import StockLatestQuoteRequest
            
            request = StockLatestQuoteRequest(symbol_or_symbols="AAPL")
            quote = self.client.get_stock_latest_quote(request)
            
            return quote is not None and 'AAPL' in quote
        except Exception as e:
            logger.error(f"Alpaca connection test failed: {e}")
            return False


# Quick test function
def test_alpaca():
    """Test Alpaca provider."""
    print("🚀 Testing Alpaca Markets Provider\n")
    
    # Check for credentials
    if not os.getenv('ALPACA_API_KEY'):
        print("❌ ALPACA_API_KEY not set!")
        print("\nTo get FREE Alpaca account:")
        print("1. Go to https://alpaca.markets")
        print("2. Sign up for FREE paper trading account")
        print("3. Get your API keys from dashboard")
        print("4. Set environment variables:")
        print("   export ALPACA_API_KEY='your_key'")
        print("   export ALPACA_API_SECRET='your_secret'")
        return
    
    try:
        provider = AlpacaProvider()
        
        # Test connection
        if provider.test_connection():
            print("✅ Connection successful!")
            
            # Get some data
            print("\nFetching AAPL data...")
            data = provider.get_historical_data('AAPL')
            
            if not data.empty:
                print(f"✅ Got {len(data)} days of data")
                print(f"Latest close: ${data['Close'].iloc[-1]:.2f}")
                print("\nSample data:")
                print(data.tail(3))
            else:
                print("❌ No data returned")
        else:
            print("❌ Connection failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_alpaca()