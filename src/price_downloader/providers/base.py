"""
Base Provider Interface for DOKKAEBI Price Data Sources

Defines the contract that all price data providers must implement.
Ensures consistent API across Yahoo Finance, IEX Cloud, Alpha Vantage, etc.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Union
import pandas as pd


class ProviderError(Exception):
    """Base exception for provider-related errors."""
    pass


class RateLimitError(ProviderError):
    """Raised when provider rate limits are exceeded."""
    pass


class AuthenticationError(ProviderError):
    """Raised when provider authentication fails."""
    pass


class DataUnavailableError(ProviderError):
    """Raised when requested data is not available from provider."""
    pass


class BaseProvider(ABC):
    """
    Abstract base class for all price data providers.
    
    Ensures consistent interface across different data sources
    so we can seamlessly switch between Yahoo Finance, IEX Cloud,
    Alpha Vantage, etc. when one gets rate limited.
    """
    
    def __init__(self, name: str):
        """
        Initialize the provider.
        
        Args:
            name: Human-readable name of the provider
        """
        self.name = name
        self.request_count = 0
        self.last_request_time = None
        
    @abstractmethod
    def download_symbol(
        self,
        symbol: str,
        period: Optional[str] = None,
        interval: str = "1d",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        """
        Download price data for a single symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', 
                               '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1d', '1h', '5m', etc.)
            start: Start date for data
            end: End date for data
            
        Returns:
            DataFrame with standardized OHLCV columns or None if failed
            
        Raises:
            RateLimitError: When rate limits are exceeded
            AuthenticationError: When API key is invalid
            DataUnavailableError: When data is not available
        """
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is currently available.
        
        Returns:
            True if provider can be used, False otherwise
        """
        pass
        
    @abstractmethod
    def get_rate_limit_info(self) -> Dict[str, Union[int, str]]:
        """
        Get current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        pass
        
    def standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize DataFrame column names and format.
        
        All providers should return DataFrames with these columns:
        - Open, High, Low, Close, Volume
        - DateTime index
        
        Args:
            df: Raw DataFrame from provider
            
        Returns:
            Standardized DataFrame
        """
        if df is None or df.empty:
            return df
            
        # Make a copy to avoid modifying original
        result = df.copy()
        
        # Standardize column names (case-insensitive mapping)
        column_mapping = {}
        for col in result.columns:
            col_lower = str(col).lower()
            if col_lower in ['open', 'o']:
                column_mapping[col] = 'Open'
            elif col_lower in ['high', 'h']:
                column_mapping[col] = 'High'
            elif col_lower in ['low', 'l']:
                column_mapping[col] = 'Low'
            elif col_lower in ['close', 'c', 'adj close', 'adj_close']:
                column_mapping[col] = 'Close'
            elif col_lower in ['volume', 'v', 'vol']:
                column_mapping[col] = 'Volume'
                
        result = result.rename(columns=column_mapping)
        
        # Ensure we have required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in result.columns]
        
        if missing_cols:
            raise DataUnavailableError(
                f"Missing required columns: {missing_cols}. "
                f"Available columns: {list(result.columns)}"
            )
            
        # Keep only the required columns in standard order
        result = result[required_cols]
        
        # Ensure index is datetime
        if not isinstance(result.index, pd.DatetimeIndex):
            try:
                result.index = pd.to_datetime(result.index)
            except Exception as e:
                raise DataUnavailableError(f"Cannot convert index to datetime: {e}")
                
        return result
        
    def __str__(self) -> str:
        """String representation of the provider."""
        return f"{self.name}Provider"
        
    def __repr__(self) -> str:
        """Detailed representation of the provider."""
        return f"{self.__class__.__name__}(name='{self.name}')"