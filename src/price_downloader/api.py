"""
Programmatic API for the DOKKAEBI Price Downloader.

This allows other modules (like meme detector) to automatically
download price data without CLI interaction.

Viper's clean API - because automation should be fucking elegant!
"""

import os
import sys
import logging
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from price_downloader.providers.alpaca_provider import AlpacaProvider


logger = logging.getLogger(__name__)


class PriceDownloaderAPI:
    """
    Programmatic interface for downloading price data.
    
    Usage:
        api = PriceDownloaderAPI()
        data = api.download_symbols(['GME', 'AMC', 'DNUT'])
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None):
        """
        Initialize the API.
        
        Args:
            api_key: Alpaca API key (or use env var)
            api_secret: Alpaca API secret (or use env var)
        """
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.api_secret = api_secret or os.getenv('ALPACA_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "Alpaca API credentials required! "
                "Set ALPACA_API_KEY and ALPACA_API_SECRET env vars"
            )
        
        self.provider = AlpacaProvider(self.api_key, self.api_secret)
        
    def download_symbols(
        self,
        symbols: Union[List[str], str],
        period: str = '1mo',
        interval: str = '1Day'
    ) -> Dict[str, pd.DataFrame]:
        """
        Download price data for given symbols.
        
        Args:
            symbols: List of symbols or path to JSON/text file
            period: Time period to download
            interval: Data interval (1Day, 1Hour, 5Min, etc.)
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        # Handle different input types
        if isinstance(symbols, str):
            symbols = self._load_symbols_from_file(symbols)
        elif not isinstance(symbols, list):
            symbols = list(symbols)
        
        # Clean symbols
        symbols = [s.strip().upper() for s in symbols]
        
        logger.info(f"Downloading {len(symbols)} symbols via API")
        
        # Download data
        results = {}
        success_count = 0
        fail_count = 0
        
        for symbol in symbols:
            try:
                data = self.provider.get_historical_data(
                    symbol, 
                    interval=interval
                )
                
                if not data.empty:
                    results[symbol] = data
                    success_count += 1
                    logger.info(f"✅ {symbol}: {len(data)} days downloaded")
                else:
                    results[symbol] = pd.DataFrame()
                    fail_count += 1
                    logger.warning(f"❌ {symbol}: No data returned")
                    
            except Exception as e:
                logger.error(f"❌ {symbol}: Error - {e}")
                results[symbol] = pd.DataFrame()
                fail_count += 1
        
        logger.info(
            f"Download complete: {success_count} succeeded, "
            f"{fail_count} failed"
        )
        
        return results
    
    def download_from_json(self, json_data: Union[dict, str]) -> Dict[str, pd.DataFrame]:
        """
        Download symbols from JSON input.
        
        Args:
            json_data: Dict with 'symbols' key or path to JSON file
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        import json
        
        # Load from file if path provided
        if isinstance(json_data, str):
            with open(json_data, 'r') as f:
                json_data = json.load(f)
        
        # Extract symbols
        symbols = json_data.get('symbols', [])
        period = json_data.get('period', '1mo')
        interval = json_data.get('interval', '1Day')
        
        return self.download_symbols(symbols, period, interval)
    
    def download_watchlist(self, watchlist_file: str = 'data/watchlist.txt') -> Dict[str, pd.DataFrame]:
        """
        Download symbols from default watchlist file.
        
        Args:
            watchlist_file: Path to watchlist file
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        if not os.path.exists(watchlist_file):
            logger.warning(f"Watchlist file not found: {watchlist_file}")
            return {}
        
        return self.download_symbols(watchlist_file)
    
    def get_latest_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get just the latest prices for symbols.
        
        Args:
            symbols: List of symbols
            
        Returns:
            Dictionary mapping symbols to latest prices
        """
        prices = {}
        
        for symbol in symbols:
            price = self.provider.get_latest_price(symbol)
            if price:
                prices[symbol] = price
        
        return prices
    
    def _load_symbols_from_file(self, filepath: str) -> List[str]:
        """Load symbols from text or JSON file."""
        if filepath.endswith('.json'):
            import json
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data.get('symbols', [])
        else:
            # Text file - one symbol per line
            with open(filepath, 'r') as f:
                return [line.strip().upper() for line in f 
                       if line.strip() and not line.startswith('#')]


# Convenience function for meme detector integration
def download_for_meme_detector(symbols: List[str]) -> Dict[str, pd.DataFrame]:
    """
    Quick function for meme detector to call.
    
    Args:
        symbols: List of symbols to download
        
    Returns:
        Dictionary of DataFrames with price data
    """
    api = PriceDownloaderAPI()
    return api.download_symbols(symbols, period='1mo', interval='1Day')


# Example usage for testing
def test_api():
    """Test the API functionality."""
    print("🚀 Testing Price Downloader API\n")
    
    # Initialize API
    api = PriceDownloaderAPI()
    
    # Test with list
    print("Testing with symbol list...")
    data = api.download_symbols(['GME', 'AMC', 'DNUT'])
    
    for symbol, df in data.items():
        if not df.empty:
            print(f"✅ {symbol}: {len(df)} days, latest: ${df['Close'].iloc[-1]:.2f}")
        else:
            print(f"❌ {symbol}: No data")
    
    # Test JSON input
    print("\nTesting with JSON input...")
    json_input = {
        'symbols': ['AAPL', 'MSFT'],
        'period': '5d',
        'interval': '1Day'
    }
    data = api.download_from_json(json_input)
    
    for symbol, df in data.items():
        if not df.empty:
            print(f"✅ {symbol}: {len(df)} days")
    
    print("\n✨ API test complete!")


if __name__ == "__main__":
    test_api()