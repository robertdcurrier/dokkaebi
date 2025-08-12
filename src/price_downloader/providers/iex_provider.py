"""
IEX Cloud Provider for DOKKAEBI

High-quality financial data from IEX Cloud with generous free tier.
Our backup when Yahoo Finance decides to rate limit us into oblivion.

Free tier: 500,000 messages/month - perfect for HebbNet data feeding!
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from iexfinance.stocks import get_historical_data, Stock

from .base import BaseProvider, RateLimitError, AuthenticationError, DataUnavailableError

logger = logging.getLogger(__name__)


class IEXCloudProvider(BaseProvider):
    """
    IEX Cloud data provider with generous free tier.
    
    Features:
    - 500,000 messages per month FREE
    - High-quality, reliable data
    - No rate limiting within message quota
    - Excellent for daily OHLCV data
    """
    
    def __init__(self, token: Optional[str] = None, sandbox: bool = False):
        """
        Initialize IEX Cloud provider.
        
        Args:
            token: IEX Cloud API token (or use IEX_TOKEN env var)
            sandbox: Use sandbox environment for testing
        """
        super().__init__("IEX Cloud")
        
        # Get token from parameter or environment
        self.token = token or os.getenv('IEX_TOKEN')
        self.sandbox = sandbox
        
        if not self.token:
            raise AuthenticationError(
                "IEX Cloud token required. Set IEX_TOKEN environment variable "
                "or pass token parameter. Get free token at https://iexcloud.io/"
            )
            
        # Set token for iexfinance library
        os.environ['IEX_TOKEN'] = self.token
        
        if sandbox:
            os.environ['IEX_API_VERSION'] = 'sandbox'
            
        self.messages_used = 0
        self.monthly_limit = 500000  # Free tier limit
        
    def download_symbol(
        self,
        symbol: str,
        period: Optional[str] = None,
        interval: str = "1d",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        """
        Download price data for a single symbol from IEX Cloud.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
            period: Data period (converted to date range)
            interval: Data interval ('1d' only for IEX historical)
            start: Start date for data
            end: End date for data
            
        Returns:
            Standardized DataFrame with OHLCV data or None if failed
        """
        symbol = symbol.upper().strip().replace('$', '')
        
        # IEX only supports daily intervals for historical data
        if interval != "1d":
            logger.warning(f"IEX Cloud only supports daily data, got interval: {interval}")
            interval = "1d"
            
        try:
            # Convert period to date range if needed
            if period and not (start and end):
                start, end = self._period_to_dates(period)
                
            # Default to 1 year if no dates specified
            if not start or not end:
                end = datetime.now() - timedelta(days=1)  # Yesterday
                start = end - timedelta(days=365)         # 1 year ago
                
            # Ensure dates are valid for IEX (no future dates)
            today = datetime.now().date()
            if end.date() >= today:
                end = datetime.combine(today - timedelta(days=1), datetime.min.time())
                
            logger.debug(f"Fetching {symbol} from {start.date()} to {end.date()}")
            
            # Download data from IEX Cloud
            data = get_historical_data(
                symbol,
                start,
                end,
                output_format='pandas'
            )
            
            if data is None or data.empty:
                logger.warning(f"No data returned for {symbol}")
                return None
                
            # Track message usage (estimate)
            days_requested = (end - start).days
            self.messages_used += max(1, days_requested)  # Rough estimate
            self.request_count += 1
            self.last_request_time = time.time()
            
            logger.info(f"Downloaded {len(data)} rows for {symbol}")
            
            # Standardize the DataFrame format
            return self.standardize_dataframe(data)
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for authentication errors
            if "unauthorized" in error_msg or "api key" in error_msg:
                raise AuthenticationError(f"IEX Cloud authentication failed: {e}")
                
            # Check for rate limiting (though rare on free tier)
            if "rate limit" in error_msg or "429" in error_msg:
                raise RateLimitError(f"IEX Cloud rate limit exceeded: {e}")
                
            # Check for quota exceeded
            if "quota" in error_msg or "limit" in error_msg:
                raise RateLimitError(f"IEX Cloud message quota exceeded: {e}")
                
            logger.error(f"Failed to download {symbol} from IEX Cloud: {e}")
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
        Download price data for multiple symbols from IEX Cloud.
        
        Args:
            symbols: List of stock symbols
            period: Data period for all symbols
            interval: Data interval (only '1d' supported)
            start: Start date for data
            end: End date for data
            
        Returns:
            Dictionary mapping symbols to DataFrames (or None if failed)
        """
        results = {}
        
        # Check if we have enough messages left
        estimated_messages = len(symbols) * 30  # Rough estimate for 1 month data
        if self.messages_used + estimated_messages > self.monthly_limit:
            logger.warning(
                f"Estimated {estimated_messages} messages would exceed "
                f"monthly limit of {self.monthly_limit}"
            )
            
        for symbol in symbols:
            try:
                data = self.download_symbol(symbol, period, interval, start, end)
                results[symbol] = data
                
                # Small delay to be respectful (even though not required)
                time.sleep(0.05)
                
            except (RateLimitError, AuthenticationError):
                logger.error(f"Critical error on {symbol}, stopping batch download")
                raise
            except Exception as e:
                logger.error(f"Error downloading {symbol}: {e}")
                results[symbol] = None
                
        return results
        
    def is_available(self) -> bool:
        """
        Check if IEX Cloud is currently available.
        
        Returns:
            True if provider can be used, False otherwise
        """
        try:
            # Quick test with a popular symbol
            test_stock = Stock("AAPL")
            quote = test_stock.get_quote()
            return bool(quote)
        except Exception as e:
            error_msg = str(e).lower()
            if any(word in error_msg for word in ["unauthorized", "api key", "token"]):
                logger.error("IEX Cloud authentication failed")
                return False
            if any(word in error_msg for word in ["quota", "limit", "rate"]):
                logger.error("IEX Cloud quota/rate limit exceeded")
                return False
            # Other errors might be temporary
            logger.warning(f"IEX Cloud availability check failed: {e}")
            return True
            
    def get_rate_limit_info(self) -> Dict[str, any]:
        """
        Get current rate limit status for IEX Cloud.
        
        Returns:
            Dictionary with rate limit information
        """
        return {
            'provider': self.name,
            'requests_made': self.request_count,
            'messages_used': self.messages_used,
            'monthly_limit': self.monthly_limit,
            'messages_remaining': self.monthly_limit - self.messages_used,
            'last_request': self.last_request_time,
            'available': self.is_available(),
            'token_set': bool(self.token),
            'sandbox_mode': self.sandbox
        }
        
    def _period_to_dates(self, period: str) -> tuple[datetime, datetime]:
        """
        Convert period string to start/end dates.
        
        Args:
            period: Period string like '1y', '6mo', '3mo', etc.
            
        Returns:
            Tuple of (start_date, end_date)
        """
        end = datetime.now() - timedelta(days=1)  # Yesterday
        
        # Parse period string
        if period == '1d':
            start = end - timedelta(days=1)
        elif period == '5d':
            start = end - timedelta(days=5)
        elif period == '1mo':
            start = end - timedelta(days=30)
        elif period == '3mo':
            start = end - timedelta(days=90)
        elif period == '6mo':
            start = end - timedelta(days=180)
        elif period == '1y':
            start = end - timedelta(days=365)
        elif period == '2y':
            start = end - timedelta(days=730)
        elif period == '5y':
            start = end - timedelta(days=1825)
        elif period == '10y':
            start = end - timedelta(days=3650)
        elif period == 'ytd':
            # Year to date
            start = datetime(end.year, 1, 1)
        elif period == 'max':
            # Maximum available (20 years for IEX)
            start = end - timedelta(days=7300)  # ~20 years
        else:
            logger.warning(f"Unknown period '{period}', defaulting to 1 year")
            start = end - timedelta(days=365)
            
        return start, end