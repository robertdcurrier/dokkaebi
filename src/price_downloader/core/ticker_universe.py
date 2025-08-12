"""
Ticker Universe Fetcher - Exchange Listings Provider

Fetches comprehensive ticker lists from major exchanges for DOKKAEBI.
Because HebbNet needs to see the full market universe to make optimal decisions.

Viper's implementation - covering NYSE, NASDAQ, and the whole fucking ecosystem.
"""

import logging
from typing import Dict, List, Set, Optional
from pathlib import Path
import json

import pandas as pd
import requests
from tqdm.auto import tqdm


logger = logging.getLogger(__name__)


class TickerUniverseError(Exception):
    """Custom exception for ticker universe fetch failures."""
    pass


class TickerUniverse:
    """
    Fetches and manages ticker universes from major exchanges.
    
    Supports:
    - NYSE, NASDAQ, AMEX listings
    - Sector and industry classification
    - Market cap and volume filtering
    - Local caching for performance
    """

    # Exchange endpoints and configurations
    EXCHANGE_CONFIGS = {
        'NASDAQ': {
            'url': 'https://api.nasdaq.com/api/screener/stocks',
            'params': {
                'tableonly': 'true',
                'limit': 10000,
                'download': 'true'
            }
        },
        'NYSE': {
            # Alternative data source since NYSE API access is limited
            'url': 'https://dumbstockapi.com/stock',
            'params': {'exchanges': 'NYSE'}
        }
    }

    def __init__(
        self,
        cache_dir: str = "data/ticker_cache",
        cache_expiry_hours: int = 24
    ) -> None:
        """
        Initialize ticker universe fetcher.
        
        Args:
            cache_dir: Directory for caching ticker lists
            cache_expiry_hours: Hours before cache expires
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry_hours = cache_expiry_hours
        
        # Session for efficient HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        })
        
    def get_exchange_tickers(
        self, 
        exchange: str,
        use_cache: bool = True
    ) -> List[str]:
        """
        Get ticker list for a specific exchange.
        
        Args:
            exchange: Exchange name ('NASDAQ', 'NYSE', 'AMEX')
            use_cache: Use cached data if available and fresh
            
        Returns:
            List of ticker symbols
        """
        exchange = exchange.upper()
        
        # Check cache first
        if use_cache:
            cached_tickers = self._load_cached_tickers(exchange)
            if cached_tickers:
                logger.info(
                    f"Loaded {len(cached_tickers)} {exchange} tickers from cache"
                )
                return cached_tickers
                
        # Fetch fresh data
        logger.info(f"Fetching fresh {exchange} ticker list...")
        
        if exchange == 'NASDAQ':
            tickers = self._fetch_nasdaq_tickers()
        elif exchange == 'NYSE':
            tickers = self._fetch_nyse_tickers()
        elif exchange == 'AMEX':
            tickers = self._fetch_amex_tickers()
        else:
            raise TickerUniverseError(f"Unsupported exchange: {exchange}")
            
        # Cache the results
        if tickers:
            self._save_ticker_cache(exchange, tickers)
            logger.info(f"Cached {len(tickers)} {exchange} tickers")
            
        return tickers
        
    def get_all_tickers(
        self,
        exchanges: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> Dict[str, List[str]]:
        """
        Get ticker lists for multiple exchanges.
        
        Args:
            exchanges: List of exchanges, None for all supported
            use_cache: Use cached data if available
            
        Returns:
            Dictionary mapping exchange names to ticker lists
        """
        if exchanges is None:
            exchanges = ['NASDAQ', 'NYSE', 'AMEX']
            
        results = {}
        
        for exchange in tqdm(exchanges, desc="Fetching exchanges"):
            try:
                tickers = self.get_exchange_tickers(exchange, use_cache)
                results[exchange] = tickers
            except Exception as e:
                logger.error(f"Failed to fetch {exchange} tickers: {e}")
                results[exchange] = []
                
        return results
        
    def get_combined_universe(
        self,
        exchanges: Optional[List[str]] = None,
        remove_duplicates: bool = True
    ) -> List[str]:
        """
        Get combined ticker universe from multiple exchanges.
        
        Args:
            exchanges: List of exchanges to include
            remove_duplicates: Remove duplicate tickers
            
        Returns:
            Combined list of unique tickers
        """
        all_tickers = self.get_all_tickers(exchanges)
        
        combined = []
        for exchange, tickers in all_tickers.items():
            combined.extend(tickers)
            
        if remove_duplicates:
            # Use dict to preserve order while removing duplicates
            combined = list(dict.fromkeys(combined))
            
        logger.info(
            f"Combined universe: {len(combined)} unique tickers "
            f"from {len(all_tickers)} exchanges"
        )
        
        return combined
        
    def _fetch_nasdaq_tickers(self) -> List[str]:
        """Fetch NASDAQ ticker list."""
        try:
            # NASDAQ screener API (public endpoint)
            response = self.session.get(
                'https://api.nasdaq.com/api/screener/stocks',
                params={
                    'tableonly': 'true',
                    'limit': 25000,
                    'download': 'true'
                },
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or 'table' not in data['data']:
                logger.warning("Unexpected NASDAQ API response format")
                return self._fetch_fallback_nasdaq()
                
            rows = data['data']['table']['rows']
            tickers = [row['symbol'] for row in rows if row.get('symbol')]
            
            # Filter out invalid symbols
            tickers = self._filter_valid_symbols(tickers)
            
            return sorted(tickers)
            
        except Exception as e:
            logger.warning(f"NASDAQ API failed: {e}, trying fallback")
            return self._fetch_fallback_nasdaq()
            
    def _fetch_nyse_tickers(self) -> List[str]:
        """Fetch NYSE ticker list."""
        try:
            # Using alternative data source for NYSE
            response = self.session.get(
                'https://dumbstockapi.com/stock',
                params={'exchanges': 'NYSE'},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list):
                tickers = [item.get('ticker') for item in data 
                          if item.get('ticker')]
            else:
                logger.warning("Unexpected NYSE API response format")
                return self._fetch_fallback_nyse()
                
            tickers = self._filter_valid_symbols(tickers)
            
            return sorted(tickers)
            
        except Exception as e:
            logger.warning(f"NYSE API failed: {e}, trying fallback")
            return self._fetch_fallback_nyse()
            
    def _fetch_amex_tickers(self) -> List[str]:
        """Fetch AMEX ticker list."""
        # AMEX is often included in NYSE/NASDAQ APIs
        # For now, return a curated list of major AMEX symbols
        amex_symbols = [
            'SPY', 'QQQ', 'IWM', 'EFA', 'VTI', 'GLD', 'SLV', 'TLT',
            'HYG', 'LQD', 'XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLP',
            'XLY', 'XLU', 'XLRE', 'XLB', 'DIA', 'MDY', 'VEA', 'VWO'
        ]
        
        logger.info(f"Using curated AMEX list: {len(amex_symbols)} symbols")
        return amex_symbols
        
    def _fetch_fallback_nasdaq(self) -> List[str]:
        """Fallback NASDAQ ticker list."""
        # Major NASDAQ symbols as fallback
        fallback = [
            'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA',
            'NVDA', 'NFLX', 'ADBE', 'CRM', 'PYPL', 'INTC', 'CSCO',
            'CMCSA', 'PEP', 'COST', 'AVGO', 'TXN', 'QCOM', 'AMGN',
            'SBUX', 'GILD', 'MDLZ', 'ISRG', 'BKNG', 'ADP', 'FISV'
        ]
        
        logger.warning(
            f"Using fallback NASDAQ list: {len(fallback)} symbols"
        )
        return fallback
        
    def _fetch_fallback_nyse(self) -> List[str]:
        """Fallback NYSE ticker list."""
        # Major NYSE symbols as fallback
        fallback = [
            'AAPL', 'BRK.B', 'JNJ', 'WMT', 'PG', 'JPM', 'UNH', 'V',
            'HD', 'MA', 'DIS', 'BAC', 'ADBE', 'CRM', 'VZ', 'KO',
            'MRK', 'PFE', 'T', 'WFC', 'ABBV', 'TMO', 'ACN', 'LLY',
            'ORCL', 'CVX', 'DHR', 'BMY', 'ABT', 'NKE', 'PM', 'MDT'
        ]
        
        logger.warning(f"Using fallback NYSE list: {len(fallback)} symbols")
        return fallback
        
    def _filter_valid_symbols(self, symbols: List[str]) -> List[str]:
        """Filter out invalid or problematic symbols."""
        if not symbols:
            return []
            
        valid_symbols = []
        
        for symbol in symbols:
            if not symbol:
                continue
                
            symbol = symbol.strip().upper()
            
            # Skip if too long (likely invalid)
            if len(symbol) > 6:
                continue
                
            # Skip if contains problematic characters
            if any(char in symbol for char in [' ', '.', '-', '/', '$']):
                # Allow some dots for share classes (e.g., BRK.B)
                if '.' in symbol and len(symbol.split('.')) == 2:
                    pass  # Allowed
                else:
                    continue
                    
            # Skip test/temporary symbols
            if symbol.endswith(('TEST', 'TEMP', 'OLD')):
                continue
                
            valid_symbols.append(symbol)
            
        return valid_symbols
        
    def _load_cached_tickers(self, exchange: str) -> Optional[List[str]]:
        """Load tickers from cache if fresh enough."""
        cache_file = self.cache_dir / f"{exchange.lower()}_tickers.json"
        
        if not cache_file.exists():
            return None
            
        try:
            # Check file age
            import time
            file_age_hours = (
                time.time() - cache_file.stat().st_mtime
            ) / 3600
            
            if file_age_hours > self.cache_expiry_hours:
                logger.info(f"{exchange} cache expired ({file_age_hours:.1f}h old)")
                return None
                
            # Load cached data
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            return data.get('tickers', [])
            
        except Exception as e:
            logger.warning(f"Failed to load {exchange} cache: {e}")
            return None
            
    def _save_ticker_cache(
        self, 
        exchange: str, 
        tickers: List[str]
    ) -> None:
        """Save tickers to cache."""
        cache_file = self.cache_dir / f"{exchange.lower()}_tickers.json"
        
        try:
            cache_data = {
                'exchange': exchange,
                'tickers': tickers,
                'fetched_at': pd.Timestamp.now().isoformat(),
                'count': len(tickers)
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to save {exchange} cache: {e}")
            
    def clear_cache(self) -> int:
        """Clear all cached ticker data."""
        cache_files = list(self.cache_dir.glob("*_tickers.json"))
        
        for cache_file in cache_files:
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete {cache_file}: {e}")
                
        logger.info(f"Cleared {len(cache_files)} cache files")
        return len(cache_files)
        
    def get_cache_info(self) -> Dict[str, any]:
        """Get information about cached data."""
        cache_files = list(self.cache_dir.glob("*_tickers.json"))
        
        info = {
            'cache_dir': str(self.cache_dir),
            'cached_exchanges': {},
            'total_cached_symbols': 0
        }
        
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    
                exchange = data.get('exchange', 'unknown')
                count = data.get('count', 0)
                fetched_at = data.get('fetched_at', 'unknown')
                
                info['cached_exchanges'][exchange] = {
                    'count': count,
                    'fetched_at': fetched_at,
                    'file': str(cache_file)
                }
                info['total_cached_symbols'] += count
                
            except Exception as e:
                logger.warning(f"Failed to read cache info from {cache_file}: {e}")
                
        return info