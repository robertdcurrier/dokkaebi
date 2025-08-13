"""
DOKKAEBI Price Downloader - Main Engine

High-performance price data downloader with intelligent caching and 
retry logic. Built to feed HebbNet with clean, reliable market data.

Viper's fucking flawless implementation - because HebbNet deserves 
the best data pipeline in the game.
"""

import asyncio
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union, Set

import pandas as pd
from tqdm.auto import tqdm

from ..storage.cache import PriceCache


logger = logging.getLogger(__name__)


class PriceDownloadError(Exception):
    """Custom exception for price download failures."""
    pass


class PriceDownloader:
    """
    Bulletproof price data downloader for DOKKAEBI.
    
    Features:
    - Batch downloading with progress tracking
    - Intelligent retry logic with exponential backoff
    - DuckDB caching for lightning-fast HebbNet queries
    - Concurrent downloads for maximum throughput
    - Robust error handling and logging
    """

    def __init__(
        self,
        cache_path: str = "data/price_cache.duckdb",
        max_workers: int = 4,
        request_delay: float = 0.1,
        max_retries: int = 3
    ) -> None:
        """
        Initialize the price downloader.
        
        Args:
            cache_path: Path to DuckDB cache database
            max_workers: Number of concurrent download threads
            request_delay: Delay between requests (seconds)
            max_retries: Maximum retry attempts per symbol
        """
        self.cache = PriceCache(cache_path)
        self.max_workers = max_workers
        self.request_delay = request_delay
        self.max_retries = max_retries
        
        # Track download statistics
        self.stats = {
            'symbols_requested': 0,
            'symbols_downloaded': 0,
            'symbols_failed': 0,
            'total_rows': 0,
            'cache_hits': 0
        }
        
    def download_symbol(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        force_refresh: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        Download price data for a single symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', 
                               '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', 
                                   '60m', '90m', '1h', '1d', '5d', 
                                   '1wk', '1mo', '3mo')
            start: Start date for data
            end: End date for data
            force_refresh: Skip cache and download fresh data
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        symbol = symbol.upper().strip().replace('$', '')
        
        # Check cache first unless forced refresh
        if not force_refresh:
            cached_data = self._check_cache(symbol, start, end)
            if cached_data is not None:
                self.stats['cache_hits'] += 1
                return cached_data
                
        # Download fresh data with retry logic
        for attempt in range(self.max_retries):
            try:
                ticker = yf.Ticker(symbol)
                
                # Use period or date range
                if start and end:
                    data = ticker.history(
                        start=start, 
                        end=end, 
                        interval=interval,
                        auto_adjust=True,
                        prepost=True
                    )
                else:
                    data = ticker.history(
                        period=period,
                        interval=interval, 
                        auto_adjust=True,
                        prepost=True
                    )
                    
                if data.empty:
                    logger.warning(f"No data returned for {symbol}")
                    continue
                    
                # Store in cache for future use
                rows_stored = self.cache.store_tick_data(
                    data, symbol, show_progress=False
                )
                self.stats['total_rows'] += rows_stored
                
                # Store metadata if available
                self._store_ticker_metadata(ticker, symbol)
                
                logger.info(
                    f"Downloaded {len(data)} rows for {symbol} "
                    f"(attempt {attempt + 1})"
                )
                return data
                
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1} failed for {symbol}: {e}"
                )
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = (2 ** attempt) * self.request_delay
                    time.sleep(delay)
                    
        logger.error(f"Failed to download {symbol} after {self.max_retries} attempts")
        return None
        
    def download_batch(
        self,
        symbols: List[str],
        period: str = "1y", 
        interval: str = "1d",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        force_refresh: bool = False,
        show_progress: bool = True
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Download price data for multiple symbols concurrently.
        
        Args:
            symbols: List of stock symbols
            period: Data period for all symbols
            interval: Data interval for all symbols
            start: Start date for data
            end: End date for data  
            force_refresh: Skip cache and download fresh data
            show_progress: Show progress bar
            
        Returns:
            Dictionary mapping symbols to DataFrames (or None if failed)
        """
        symbols = [s.upper().strip() for s in symbols]
        unique_symbols = list(dict.fromkeys(symbols))  # Preserve order
        
        self.stats['symbols_requested'] = len(unique_symbols)
        results = {}
        
        # Use ThreadPoolExecutor for concurrent downloads
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_symbol = {
                executor.submit(
                    self.download_symbol,
                    symbol, period, interval, start, end, force_refresh
                ): symbol
                for symbol in unique_symbols
            }
            
            # Process completed downloads with progress tracking
            if show_progress:
                progress = tqdm(
                    total=len(unique_symbols),
                    desc="Downloading prices",
                    unit="symbol"
                )
                
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                
                try:
                    data = future.result()
                    results[symbol] = data
                    
                    if data is not None:
                        self.stats['symbols_downloaded'] += 1
                    else:
                        self.stats['symbols_failed'] += 1
                        
                except Exception as e:
                    logger.error(f"Unexpected error for {symbol}: {e}")
                    results[symbol] = None
                    self.stats['symbols_failed'] += 1
                    
                if show_progress:
                    progress.update(1)
                    progress.set_postfix({
                        'Downloaded': self.stats['symbols_downloaded'],
                        'Failed': self.stats['symbols_failed'],
                        'Cache hits': self.stats['cache_hits']
                    })
                    
            if show_progress:
                progress.close()
                
        self._log_batch_summary()
        return results
        
    def _check_cache(
        self,
        symbol: str,
        start: Optional[datetime],
        end: Optional[datetime]
    ) -> Optional[pd.DataFrame]:
        """Check if symbol data exists in cache and is recent enough."""
        try:
            cache_start, cache_end = self.cache.get_date_range(symbol)
            
            if not cache_start:
                return None  # No data in cache
                
            # Check if cache covers requested date range
            if start and start < cache_start:
                return None  # Need earlier data
                
            if end and end > cache_end:
                return None  # Need more recent data
                
            # For daily data, check if cache is fresh enough
            if not end:  # Real-time request
                now = datetime.now(timezone.utc)
                if cache_end < now - timedelta(hours=4):
                    return None  # Cache too old for real-time
                    
            # Retrieve from cache
            return self.cache.get_price_data(symbol, start, end)
            
        except Exception as e:
            logger.warning(f"Cache check failed for {symbol}: {e}")
            return None
            
    def _store_ticker_metadata(
        self, 
        ticker: yf.Ticker, 
        symbol: str
    ) -> None:
        """Store ticker metadata for filtering and analysis."""
        try:
            info = ticker.info
            
            metadata = {
                'symbol': symbol,
                'exchange': info.get('exchange'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'shares_outstanding': info.get('sharesOutstanding')
            }
            
            self.cache.store_symbol_metadata(metadata)
            
        except Exception as e:
            logger.debug(f"Failed to store metadata for {symbol}: {e}")
            
    def _log_batch_summary(self) -> None:
        """Log summary of batch download results."""
        total = self.stats['symbols_requested']
        downloaded = self.stats['symbols_downloaded']
        failed = self.stats['symbols_failed']
        cache_hits = self.stats['cache_hits']
        
        success_rate = (downloaded / total * 100) if total > 0 else 0
        
        logger.info(
            f"Batch download complete: {downloaded}/{total} symbols "
            f"({success_rate:.1f}% success), {failed} failed, "
            f"{cache_hits} cache hits, {self.stats['total_rows']} total rows"
        )
        
    def get_cached_symbols(self) -> List[str]:
        """Get list of all symbols in cache."""
        latest_prices = self.cache.get_latest_prices()
        return sorted(latest_prices['symbol'].tolist())
        
    def get_cache_stats(self) -> Dict[str, Union[int, str]]:
        """Get cache statistics."""
        symbol_count = self.cache.get_symbol_count()
        
        return {
            'cached_symbols': symbol_count,
            'download_stats': self.stats.copy(),
            'cache_path': str(self.cache.db_path)
        }
        
    def clear_cache(self, older_than_days: Optional[int] = None) -> int:
        """
        Clear cache data.
        
        Args:
            older_than_days: Only clear data older than N days,
                           None to clear all
                           
        Returns:
            Number of rows deleted
        """
        if older_than_days:
            return self.cache.cleanup_old_data(older_than_days)
        else:
            # This would require a full recreate - implement if needed
            logger.warning("Full cache clear not implemented yet")
            return 0
            
    def close(self) -> None:
        """Clean up resources."""
        self.cache.close()
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()