"""
DOKKAEBI Price Downloader V2 - Multi-Provider Engine

Enhanced price data downloader with multiple data source providers
and automatic fallback when providers get rate limited.

Yahoo Finance rate limiting us? No problem! 
IEX Cloud to the rescue with 500k free messages per month!

Viper's RESILIENT implementation - because HebbNet deserves 
bulletproof data pipelines that NEVER fail.
"""

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union, Set

import pandas as pd
from tqdm.auto import tqdm

from ..storage.cache import PriceCache
from ..providers import BaseProvider, YahooProvider, IEXCloudProvider
from ..providers.base import RateLimitError, AuthenticationError, DataUnavailableError

logger = logging.getLogger(__name__)


class PriceDownloadError(Exception):
    """Custom exception for price download failures."""
    pass


class PriceDownloaderV2:
    """
    Multi-provider price data downloader for DOKKAEBI.
    
    Features:
    - Multiple data source providers (Yahoo Finance, IEX Cloud, etc.)
    - Automatic failover when providers get rate limited
    - Intelligent caching with DuckDB
    - Concurrent downloads for maximum throughput
    - Provider health monitoring and statistics
    - Bulletproof error handling and recovery
    """

    def __init__(
        self,
        cache_path: str = "data/price_cache.duckdb",
        max_workers: int = 4,
        providers: Optional[List[BaseProvider]] = None,
        iex_token: Optional[str] = None
    ) -> None:
        """
        Initialize the multi-provider price downloader.
        
        Args:
            cache_path: Path to DuckDB cache database
            max_workers: Number of concurrent download threads
            providers: List of data providers (auto-configured if None)
            iex_token: IEX Cloud API token (optional)
        """
        self.cache = PriceCache(cache_path)
        self.max_workers = max_workers
        
        # Initialize providers
        if providers is None:
            self.providers = self._initialize_default_providers(iex_token)
        else:
            self.providers = providers
            
        # Track download statistics per provider
        self.stats = {
            'total_requests': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'cache_hits': 0,
            'provider_stats': {p.name: {'used': 0, 'failed': 0} for p in self.providers}
        }
        
    def _initialize_default_providers(self, iex_token: Optional[str] = None) -> List[BaseProvider]:
        """Initialize default providers in order of preference."""
        providers = []
        
        # Primary: Yahoo Finance (free but rate limited)
        try:
            yahoo = YahooProvider(request_delay=0.1, max_retries=2)
            providers.append(yahoo)
            logger.info("✓ Yahoo Finance provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Yahoo Finance: {e}")
            
        # Backup: IEX Cloud (generous free tier)
        try:
            iex = IEXCloudProvider(token=iex_token)
            providers.append(iex)
            logger.info("✓ IEX Cloud provider initialized")
        except AuthenticationError as e:
            logger.warning(f"IEX Cloud authentication failed: {e}")
        except Exception as e:
            logger.warning(f"Failed to initialize IEX Cloud: {e}")
            
        if not providers:
            raise PriceDownloadError("No data providers available!")
            
        logger.info(f"Initialized {len(providers)} data providers: {[p.name for p in providers]}")
        return providers
        
    def download_symbol(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        force_refresh: bool = False,
        preferred_provider: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Download price data for a single symbol with provider fallback.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', 
                               '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1d', '1h', '5m', etc.)
            start: Start date for data
            end: End date for data
            force_refresh: Skip cache and download fresh data
            preferred_provider: Try this provider first
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        symbol = symbol.upper().strip().replace('$', '')
        self.stats['total_requests'] += 1
        
        # Check cache first unless forced refresh
        if not force_refresh:
            cached_data = self._check_cache(symbol, start, end)
            if cached_data is not None:
                self.stats['cache_hits'] += 1
                return cached_data
                
        # Try providers in order (preferred first if specified)
        providers_to_try = self._get_provider_order(preferred_provider)
        
        for provider in providers_to_try:
            try:
                logger.debug(f"Trying {provider.name} for {symbol}")
                
                # Check if provider is available
                if not provider.is_available():
                    logger.warning(f"{provider.name} is not available, skipping")
                    continue
                    
                # Download data using this provider
                data = provider.download_symbol(
                    symbol=symbol,
                    period=period,
                    interval=interval,
                    start=start,
                    end=end
                )
                
                if data is not None and not data.empty:
                    # Success! Store in cache
                    rows_stored = self.cache.store_tick_data(
                        data, symbol, show_progress=False
                    )
                    
                    # Update statistics
                    self.stats['successful_downloads'] += 1
                    self.stats['provider_stats'][provider.name]['used'] += 1
                    
                    logger.info(
                        f"✓ Downloaded {len(data)} rows for {symbol} "
                        f"using {provider.name}"
                    )
                    
                    return data
                else:
                    logger.warning(f"{provider.name} returned no data for {symbol}")
                    
            except RateLimitError as e:
                logger.warning(f"{provider.name} rate limited: {e}")
                self.stats['provider_stats'][provider.name]['failed'] += 1
                continue  # Try next provider
                
            except AuthenticationError as e:
                logger.error(f"{provider.name} authentication error: {e}")
                self.stats['provider_stats'][provider.name]['failed'] += 1
                continue  # Try next provider
                
            except Exception as e:
                logger.warning(f"{provider.name} failed for {symbol}: {e}")
                self.stats['provider_stats'][provider.name]['failed'] += 1
                continue  # Try next provider
                
        # All providers failed
        logger.error(f"All providers failed for {symbol}")
        self.stats['failed_downloads'] += 1
        return None
        
    def download_batch(
        self,
        symbols: List[str],
        period: str = "1y", 
        interval: str = "1d",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        force_refresh: bool = False,
        show_progress: bool = True,
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Download price data for multiple symbols with provider fallback.
        
        Args:
            symbols: List of stock symbols
            period: Data period for all symbols
            interval: Data interval for all symbols
            start: Start date for data
            end: End date for data  
            force_refresh: Skip cache and download fresh data
            show_progress: Show progress bar
            preferred_provider: Try this provider first for all symbols
            
        Returns:
            Dictionary mapping symbols to DataFrames (or None if failed)
        """
        symbols = [s.upper().strip() for s in symbols]
        unique_symbols = list(dict.fromkeys(symbols))  # Preserve order
        
        results = {}
        
        # Use ThreadPoolExecutor for concurrent downloads
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_symbol = {
                executor.submit(
                    self.download_symbol,
                    symbol, period, interval, start, end, force_refresh, preferred_provider
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
                    
                except Exception as e:
                    logger.error(f"Unexpected error for {symbol}: {e}")
                    results[symbol] = None
                    
                if show_progress:
                    progress.update(1)
                    progress.set_postfix({
                        'Success': self.stats['successful_downloads'],
                        'Failed': self.stats['failed_downloads'],
                        'Cache hits': self.stats['cache_hits']
                    })
                    
            if show_progress:
                progress.close()
                
        self._log_batch_summary()
        return results
        
    def get_provider_stats(self) -> Dict[str, any]:
        """Get comprehensive statistics for all providers."""
        provider_info = {}
        
        for provider in self.providers:
            provider_info[provider.name] = {
                'available': provider.is_available(),
                'rate_limit_info': provider.get_rate_limit_info(),
                'usage_stats': self.stats['provider_stats'][provider.name]
            }
            
        return {
            'overall_stats': {
                'total_requests': self.stats['total_requests'],
                'successful_downloads': self.stats['successful_downloads'], 
                'failed_downloads': self.stats['failed_downloads'],
                'cache_hits': self.stats['cache_hits'],
                'success_rate': (
                    self.stats['successful_downloads'] / self.stats['total_requests'] * 100
                    if self.stats['total_requests'] > 0 else 0
                )
            },
            'providers': provider_info
        }
        
    def _get_provider_order(self, preferred_provider: Optional[str] = None) -> List[BaseProvider]:
        """Get providers in order of preference."""
        if preferred_provider:
            # Put preferred provider first
            preferred = [p for p in self.providers if p.name == preferred_provider]
            others = [p for p in self.providers if p.name != preferred_provider]
            return preferred + others
        else:
            # Use default order
            return self.providers
            
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
            
    def _log_batch_summary(self) -> None:
        """Log summary of batch download results."""
        total = self.stats['total_requests']
        success = self.stats['successful_downloads']
        failed = self.stats['failed_downloads']
        cache_hits = self.stats['cache_hits']
        
        success_rate = (success / total * 100) if total > 0 else 0
        
        logger.info(
            f"Batch complete: {success}/{total} successful ({success_rate:.1f}%), "
            f"{failed} failed, {cache_hits} cache hits"
        )
        
        # Log provider usage
        for provider_name, stats in self.stats['provider_stats'].items():
            if stats['used'] > 0 or stats['failed'] > 0:
                logger.info(
                    f"  {provider_name}: {stats['used']} used, {stats['failed']} failed"
                )
                
    # Delegate cache methods to maintain compatibility
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
        """Clear cache data."""
        if older_than_days:
            return self.cache.cleanup_old_data(older_than_days)
        else:
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