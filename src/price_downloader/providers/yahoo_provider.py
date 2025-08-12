"""
Yahoo Finance Provider for DOKKAEBI

Wraps our existing yfinance implementation in the new provider interface.
This is our primary data source, but prone to rate limiting.
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import yfinance as yf

from .base import BaseProvider, RateLimitError, DataUnavailableError

logger = logging.getLogger(__name__)


class YahooProvider(BaseProvider):
    """
    Yahoo Finance data provider using yfinance library.
    
    Free but heavily rate limited. When Yahoo says "Too Many Requests",
    we'll switch to our backup providers.
    """
    
    def __init__(self, request_delay: float = 0.1, max_retries: int = 3):
        """
        Initialize Yahoo Finance provider.
        
        Args:
            request_delay: Delay between requests (seconds)
            max_retries: Maximum retry attempts per symbol
        """
        super().__init__("Yahoo Finance")
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.last_request_time = None
        
    def download_symbol(
        self,
        symbol: str,
        period: Optional[str] = None,
        interval: str = "1d",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        """
        Download price data for a single symbol using yfinance.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', 
                               '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1d', '1h', '5m', etc.)
            start: Start date for data
            end: End date for data
            
        Returns:
            Standardized DataFrame with OHLCV data or None if failed
        """
        symbol = symbol.upper().strip().replace('$', '')
        
        # Rate limiting
        self._enforce_rate_limit()
        
        # Download with retry logic
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
                elif period:
                    data = ticker.history(
                        period=period,
                        interval=interval,
                        auto_adjust=True,
                        prepost=True
                    )
                else:
                    data = ticker.history(
                        period="1y",  # Default period
                        interval=interval,
                        auto_adjust=True,
                        prepost=True
                    )
                    
                if data.empty:
                    logger.warning(f"No data returned for {symbol}")
                    return None
                    
                # Track successful request
                self.request_count += 1
                self.last_request_time = time.time()
                
                # Standardize the DataFrame format
                return self.standardize_dataframe(data)
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for rate limiting
                if "too many requests" in error_msg or "429" in error_msg:
                    raise RateLimitError(f"Yahoo Finance rate limit exceeded: {e}")
                    
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {e}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = (2 ** attempt) * self.request_delay
                    time.sleep(delay)
                    
        logger.error(f"Failed to download {symbol} after {self.max_retries} attempts")
        return None
        
    def download_batch(
        self,
        symbols: List[str],
        period: Optional[str] = None,
        interval: str = "1d",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Download price data for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            period: Data period for all symbols
            interval: Data interval for all symbols
            start: Start date for data
            end: End date for data
            
        Returns:
            Dictionary mapping symbols to DataFrames (or None if failed)
        """
        results = {}
        
        for symbol in symbols:
            try:
                data = self.download_symbol(symbol, period, interval, start, end)
                results[symbol] = data
                
                # Add delay between symbols to avoid rate limiting
                if len(symbols) > 1:
                    time.sleep(self.request_delay)
                    
            except RateLimitError:
                logger.error(f"Rate limited on {symbol}, stopping batch download")
                # Don't continue if we hit rate limits
                raise
            except Exception as e:
                logger.error(f"Error downloading {symbol}: {e}")
                results[symbol] = None
                
        return results
        
    def is_available(self) -> bool:
        """
        Check if Yahoo Finance is currently available.
        
        Returns:
            True if provider can be used, False if rate limited
        """
        try:
            # Quick test with a popular symbol
            test_ticker = yf.Ticker("AAPL")
            info = test_ticker.info
            return bool(info.get('symbol'))
        except Exception as e:
            error_msg = str(e).lower()
            if "too many requests" in error_msg or "429" in error_msg:
                return False
            # Other errors might be temporary
            return True
            
    def get_rate_limit_info(self) -> Dict[str, any]:
        """
        Get current rate limit status for Yahoo Finance.
        
        Returns:
            Dictionary with rate limit information
        """
        return {
            'provider': self.name,
            'requests_made': self.request_count,
            'last_request': self.last_request_time,
            'rate_limit': 'Unknown (Yahoo doesn\'t publish limits)',
            'available': self.is_available()
        }
        
    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests."""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.request_delay:
                sleep_time = self.request_delay - elapsed
                time.sleep(sleep_time)