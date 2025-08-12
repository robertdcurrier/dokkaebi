"""
Market Data Filters - DOKKAEBI Trading Universe Selection

Specialized filters for price, volume, market cap, and exchange filtering.
Designed to create optimal ticker universes for HebbNet training.

Viper's precision filtering - because HebbNet deserves quality data.
"""

import logging
from typing import Dict, List, Optional, Union, Any

import pandas as pd

from .base import BaseFilter, NumericRangeFilter, StringMatchFilter


logger = logging.getLogger(__name__)


class PriceFilter(NumericRangeFilter):
    """
    Filter stocks by price range.
    
    Useful for focusing on penny stocks, mid-range stocks, or 
    high-priced equities based on trading strategy.
    """

    def __init__(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        allow_null: bool = False
    ) -> None:
        """
        Initialize price filter.
        
        Args:
            min_price: Minimum stock price (inclusive)
            max_price: Maximum stock price (inclusive)
            allow_null: Allow stocks with null/missing prices
        """
        name = f"Price Filter"
        if min_price is not None and max_price is not None:
            name += f" (${min_price:.2f} - ${max_price:.2f})"
        elif min_price is not None:
            name += f" (>= ${min_price:.2f})"
        elif max_price is not None:
            name += f" (<= ${max_price:.2f})"
            
        super().__init__(
            name=name,
            field_name='close',  # Default to closing price
            min_value=min_price,
            max_value=max_price,
            allow_null=allow_null
        )


class VolumeFilter(NumericRangeFilter):
    """
    Filter stocks by trading volume.
    
    Essential for ensuring adequate liquidity for HebbNet 
    trading strategies.
    """

    def __init__(
        self,
        min_volume: Optional[int] = None,
        max_volume: Optional[int] = None,
        allow_null: bool = False
    ) -> None:
        """
        Initialize volume filter.
        
        Args:
            min_volume: Minimum daily volume
            max_volume: Maximum daily volume  
            allow_null: Allow stocks with null/missing volume
        """
        name = f"Volume Filter"
        if min_volume is not None and max_volume is not None:
            name += f" ({min_volume:,} - {max_volume:,})"
        elif min_volume is not None:
            name += f" (>= {min_volume:,})"
        elif max_volume is not None:
            name += f" (<= {max_volume:,})"
            
        super().__init__(
            name=name,
            field_name='volume',
            min_value=min_volume,
            max_value=max_volume,
            allow_null=allow_null
        )


class MarketCapFilter(NumericRangeFilter):
    """
    Filter stocks by market capitalization.
    
    Enables focus on large-cap, mid-cap, small-cap, or micro-cap
    stocks based on HebbNet strategy requirements.
    """

    # Market cap classification thresholds (in millions)
    MICRO_CAP_MAX = 300
    SMALL_CAP_MAX = 2000
    MID_CAP_MAX = 10000
    LARGE_CAP_MIN = 10000

    def __init__(
        self,
        min_market_cap: Optional[float] = None,
        max_market_cap: Optional[float] = None,
        cap_category: Optional[str] = None,
        allow_null: bool = False
    ) -> None:
        """
        Initialize market cap filter.
        
        Args:
            min_market_cap: Minimum market cap (in millions)
            max_market_cap: Maximum market cap (in millions)
            cap_category: Predefined category ('micro', 'small', 
                         'mid', 'large')
            allow_null: Allow stocks with null/missing market cap
        """
        # Handle predefined categories
        if cap_category:
            min_market_cap, max_market_cap = self._get_category_range(
                cap_category
            )
            
        name = f"Market Cap Filter"
        if min_market_cap is not None and max_market_cap is not None:
            name += f" (${min_market_cap:.0f}M - ${max_market_cap:.0f}M)"
        elif min_market_cap is not None:
            name += f" (>= ${min_market_cap:.0f}M)"
        elif max_market_cap is not None:
            name += f" (<= ${max_market_cap:.0f}M)"
            
        # Convert millions to actual values
        min_value = (
            min_market_cap * 1_000_000 if min_market_cap else None
        )
        max_value = (
            max_market_cap * 1_000_000 if max_market_cap else None
        )
        
        super().__init__(
            name=name,
            field_name='market_cap',
            min_value=min_value,
            max_value=max_value,
            allow_null=allow_null
        )

    def _get_category_range(self, category: str) -> tuple:
        """Get market cap range for predefined category."""
        category = category.lower()
        
        if category == 'micro':
            return (0, self.MICRO_CAP_MAX)
        elif category == 'small':
            return (self.MICRO_CAP_MAX, self.SMALL_CAP_MAX)
        elif category == 'mid':
            return (self.SMALL_CAP_MAX, self.MID_CAP_MAX)
        elif category == 'large':
            return (self.LARGE_CAP_MIN, None)
        else:
            raise ValueError(
                f"Invalid cap_category: {category}. "
                "Must be 'micro', 'small', 'mid', or 'large'"
            )


class ExchangeFilter(StringMatchFilter):
    """
    Filter stocks by exchange.
    
    Allows focusing on specific exchanges (NYSE, NASDAQ, AMEX)
    for HebbNet training and trading.
    """

    # Common exchange mappings
    EXCHANGE_ALIASES = {
        'nasdaq': ['NASDAQ', 'NAS', 'XNAS'],
        'nyse': ['NYSE', 'NYQ', 'XNYS'],
        'amex': ['AMEX', 'ASE', 'XASE'],
        'arca': ['ARCA', 'PSE', 'ARCX']
    }

    def __init__(
        self,
        exchanges: Union[str, List[str]],
        case_sensitive: bool = False
    ) -> None:
        """
        Initialize exchange filter.
        
        Args:
            exchanges: Exchange name(s) to include
            case_sensitive: Whether matching is case sensitive
        """
        # Normalize exchange names
        if isinstance(exchanges, str):
            exchanges = [exchanges]
            
        # Expand aliases
        expanded_exchanges = []
        for exchange in exchanges:
            exchange_lower = exchange.lower()
            if exchange_lower in self.EXCHANGE_ALIASES:
                expanded_exchanges.extend(
                    self.EXCHANGE_ALIASES[exchange_lower]
                )
            else:
                expanded_exchanges.append(exchange)
                
        # Remove duplicates while preserving order
        unique_exchanges = list(dict.fromkeys(expanded_exchanges))
        
        name = f"Exchange Filter ({', '.join(unique_exchanges)})"
        
        super().__init__(
            name=name,
            field_name='exchange',
            values=unique_exchanges,
            match_type='exact',
            case_sensitive=case_sensitive
        )


class SectorFilter(StringMatchFilter):
    """
    Filter stocks by sector.
    
    Enables sector-specific HebbNet training and analysis.
    """

    # Common sector names (GICS classification)
    SECTORS = {
        'technology': 'Information Technology',
        'healthcare': 'Health Care', 
        'financials': 'Financials',
        'energy': 'Energy',
        'industrials': 'Industrials',
        'materials': 'Materials',
        'utilities': 'Utilities',
        'real_estate': 'Real Estate',
        'consumer_discretionary': 'Consumer Discretionary',
        'consumer_staples': 'Consumer Staples',
        'communication': 'Communication Services'
    }

    def __init__(
        self,
        sectors: Union[str, List[str]],
        case_sensitive: bool = False
    ) -> None:
        """
        Initialize sector filter.
        
        Args:
            sectors: Sector name(s) to include
            case_sensitive: Whether matching is case sensitive
        """
        # Normalize sector names
        if isinstance(sectors, str):
            sectors = [sectors]
            
        # Expand common sector aliases
        expanded_sectors = []
        for sector in sectors:
            sector_lower = sector.lower()
            if sector_lower in self.SECTORS:
                expanded_sectors.append(self.SECTORS[sector_lower])
            else:
                expanded_sectors.append(sector)
                
        name = f"Sector Filter ({', '.join(expanded_sectors)})"
        
        super().__init__(
            name=name,
            field_name='sector',
            values=expanded_sectors,
            match_type='exact',
            case_sensitive=case_sensitive
        )


class LiquidityFilter(BaseFilter):
    """
    Advanced liquidity filter combining volume and price.
    
    Ensures stocks meet minimum liquidity requirements for
    safe HebbNet trading execution.
    """

    def __init__(
        self,
        min_dollar_volume: float = 1_000_000,
        min_volume: int = 100_000,
        min_price: float = 1.0,
        max_spread_percent: Optional[float] = None
    ) -> None:
        """
        Initialize liquidity filter.
        
        Args:
            min_dollar_volume: Minimum daily dollar volume
            min_volume: Minimum daily share volume
            min_price: Minimum stock price
            max_spread_percent: Maximum bid-ask spread percentage
        """
        self.min_dollar_volume = min_dollar_volume
        self.min_volume = min_volume
        self.min_price = min_price
        self.max_spread_percent = max_spread_percent
        
        name = f"Liquidity Filter (${min_dollar_volume:,.0f} daily volume)"
        super().__init__(name)

    def matches(self, item: Any) -> bool:
        """
        Check if item meets liquidity requirements.
        
        Args:
            item: Stock data (dict or Series)
            
        Returns:
            True if stock meets liquidity criteria
        """
        self.total_processed += 1
        
        try:
            # Extract required fields
            if hasattr(item, 'get'):  # Dict-like
                price = item.get('close') or item.get('price')
                volume = item.get('volume')
                bid = item.get('bid')
                ask = item.get('ask')
            else:  # Assume pandas Series or similar
                price = getattr(item, 'close', None) or getattr(
                    item, 'price', None
                )
                volume = getattr(item, 'volume', None)
                bid = getattr(item, 'bid', None)
                ask = getattr(item, 'ask', None)
                
            # Check minimum price
            if not price or price < self.min_price:
                self.filter_count += 1
                return False
                
            # Check minimum volume
            if not volume or volume < self.min_volume:
                self.filter_count += 1
                return False
                
            # Check minimum dollar volume
            dollar_volume = price * volume
            if dollar_volume < self.min_dollar_volume:
                self.filter_count += 1
                return False
                
            # Check bid-ask spread if available
            if (self.max_spread_percent and bid and ask and 
                bid > 0 and ask > 0):
                
                spread_percent = ((ask - bid) / bid) * 100
                if spread_percent > self.max_spread_percent:
                    self.filter_count += 1
                    return False
                    
            return True
            
        except Exception as e:
            logger.warning(f"Liquidity filter error: {e}")
            self.filter_count += 1
            return False

    def apply(
        self, 
        data: Union[pd.DataFrame, List[Dict]]
    ) -> Union[pd.DataFrame, List[Dict]]:
        """
        Apply liquidity filter to dataset.
        
        Args:
            data: DataFrame or list of dicts to filter
            
        Returns:
            Filtered data meeting liquidity requirements
        """
        if isinstance(data, pd.DataFrame):
            mask = data.apply(lambda row: self.matches(row), axis=1)
            return data[mask]
            
        elif isinstance(data, list):
            return [item for item in data if self.matches(item)]
            
        else:
            raise TypeError(
                f"Unsupported data type: {type(data)}. "
                "Expected DataFrame or list."
            )


class CompositeFilter(BaseFilter):
    """
    Combines multiple filters with AND/OR logic.
    
    Enables complex filtering strategies for HebbNet ticker selection.
    """

    def __init__(
        self,
        filters: List[BaseFilter],
        logic: str = "AND",
        name: Optional[str] = None
    ) -> None:
        """
        Initialize composite filter.
        
        Args:
            filters: List of filters to combine
            logic: 'AND' or 'OR' logic for combining filters
            name: Optional custom name for the composite filter
        """
        if not filters:
            raise ValueError("At least one filter is required")
            
        if logic.upper() not in ['AND', 'OR']:
            raise ValueError("Logic must be 'AND' or 'OR'")
            
        self.filters = filters
        self.logic = logic.upper()
        
        if name is None:
            filter_names = [f.name for f in filters]
            name = f"Composite Filter ({self.logic}: {', '.join(filter_names)})"
            
        super().__init__(name)

    def matches(self, item: Any) -> bool:
        """
        Check if item matches composite filter criteria.
        
        Args:
            item: Item to test against all filters
            
        Returns:
            True if item passes composite filter
        """
        self.total_processed += 1
        
        if self.logic == 'AND':
            # All filters must pass
            for filter_obj in self.filters:
                if not filter_obj.matches(item):
                    self.filter_count += 1
                    return False
            return True
            
        else:  # OR logic
            # At least one filter must pass
            for filter_obj in self.filters:
                if filter_obj.matches(item):
                    return True
            self.filter_count += 1
            return False

    def apply(
        self, 
        data: Union[pd.DataFrame, List[Dict]]
    ) -> Union[pd.DataFrame, List[Dict]]:
        """
        Apply composite filter to dataset.
        
        Args:
            data: Data to filter
            
        Returns:
            Filtered data
        """
        if isinstance(data, pd.DataFrame):
            mask = data.apply(lambda row: self.matches(row), axis=1)
            return data[mask]
            
        elif isinstance(data, list):
            return [item for item in data if self.matches(item)]
            
        else:
            raise TypeError(
                f"Unsupported data type: {type(data)}. "
                "Expected DataFrame or list."
            )

    def get_filter_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all component filters.
        
        Returns:
            Dictionary with stats for each filter
        """
        stats = {}
        for i, filter_obj in enumerate(self.filters):
            stats[f"filter_{i}_{filter_obj.name}"] = filter_obj.get_stats()
        return stats