"""
Base Filter Classes - DOKKAEBI Filtering Framework

Abstract base classes for implementing market data filters.
Clean architecture for extensible filtering system.

Viper's foundation for bulletproof filtering logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import pandas as pd


class BaseFilter(ABC):
    """
    Abstract base class for all market data filters.
    
    Provides common interface for filtering operations across
    price data, volume data, and metadata.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize filter with a descriptive name.
        
        Args:
            name: Human-readable filter name
        """
        self.name = name
        self.filter_count = 0
        self.total_processed = 0
        
    @abstractmethod
    def apply(
        self, 
        data: Union[pd.DataFrame, Dict[str, Any], List[str]]
    ) -> Union[pd.DataFrame, Dict[str, Any], List[str]]:
        """
        Apply filter to data.
        
        Args:
            data: Input data to filter
            
        Returns:
            Filtered data in same format as input
        """
        pass
        
    @abstractmethod
    def matches(self, item: Any) -> bool:
        """
        Check if a single item matches filter criteria.
        
        Args:
            item: Single data item to test
            
        Returns:
            True if item passes filter, False otherwise
        """
        pass
        
    def get_stats(self) -> Dict[str, Union[int, float, str]]:
        """
        Get filter statistics.
        
        Returns:
            Dictionary with filter performance metrics
        """
        filter_rate = (
            (self.filter_count / self.total_processed * 100)
            if self.total_processed > 0 else 0
        )
        
        return {
            'name': self.name,
            'total_processed': self.total_processed,
            'items_filtered': self.filter_count,
            'filter_rate_percent': round(filter_rate, 2),
            'items_passed': self.total_processed - self.filter_count
        }
        
    def reset_stats(self) -> None:
        """Reset filter statistics."""
        self.filter_count = 0
        self.total_processed = 0
        
    def __str__(self) -> str:
        """String representation of filter."""
        return f"{self.__class__.__name__}(name='{self.name}')"
        
    def __repr__(self) -> str:
        """Detailed string representation."""
        stats = self.get_stats()
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"processed={stats['total_processed']}, "
            f"filtered={stats['items_filtered']}"
            f")"
        )


class NumericRangeFilter(BaseFilter):
    """
    Base class for numeric range filtering.
    
    Handles min/max value filtering with optional null handling.
    """

    def __init__(
        self,
        name: str,
        field_name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_null: bool = False
    ) -> None:
        """
        Initialize numeric range filter.
        
        Args:
            name: Filter name
            field_name: Name of field to filter on
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)
            allow_null: Whether to allow null/NaN values
        """
        super().__init__(name)
        self.field_name = field_name
        self.min_value = min_value
        self.max_value = max_value
        self.allow_null = allow_null
        
        # Validation
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise ValueError(
                    f"min_value ({min_value}) cannot be greater than "
                    f"max_value ({max_value})"
                )
                
    def matches(self, item: Any) -> bool:
        """
        Check if item value is within range.
        
        Args:
            item: Item to test (dict, Series, or scalar)
            
        Returns:
            True if value is within range
        """
        self.total_processed += 1
        
        # Extract value from item
        if hasattr(item, 'get'):  # Dict-like
            value = item.get(self.field_name)
        elif hasattr(item, self.field_name):  # Object with attribute
            value = getattr(item, self.field_name)
        else:  # Assume item is the value itself
            value = item
            
        # Handle null values
        if pd.isna(value) or value is None:
            if self.allow_null:
                return True
            else:
                self.filter_count += 1
                return False
                
        # Convert to float for comparison
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            self.filter_count += 1
            return False
            
        # Check range
        if self.min_value is not None and numeric_value < self.min_value:
            self.filter_count += 1
            return False
            
        if self.max_value is not None and numeric_value > self.max_value:
            self.filter_count += 1
            return False
            
        return True
        
    def apply(
        self, 
        data: Union[pd.DataFrame, List[Dict]]
    ) -> Union[pd.DataFrame, List[Dict]]:
        """
        Apply range filter to dataset.
        
        Args:
            data: DataFrame or list of dicts to filter
            
        Returns:
            Filtered data
        """
        if isinstance(data, pd.DataFrame):
            if self.field_name not in data.columns:
                raise ValueError(
                    f"Field '{self.field_name}' not found in DataFrame"
                )
                
            mask = data[self.field_name].apply(lambda x: self.matches(x))
            return data[mask]
            
        elif isinstance(data, list):
            return [item for item in data if self.matches(item)]
            
        else:
            raise TypeError(
                f"Unsupported data type: {type(data)}. "
                "Expected DataFrame or list."
            )


class StringMatchFilter(BaseFilter):
    """
    Base class for string matching filters.
    
    Supports exact match, contains, starts with, ends with operations.
    """

    def __init__(
        self,
        name: str,
        field_name: str,
        values: Union[str, List[str]],
        match_type: str = "exact",
        case_sensitive: bool = False
    ) -> None:
        """
        Initialize string match filter.
        
        Args:
            name: Filter name
            field_name: Name of field to filter on
            values: String or list of strings to match
            match_type: 'exact', 'contains', 'starts_with', 'ends_with'
            case_sensitive: Whether matching is case sensitive
        """
        super().__init__(name)
        self.field_name = field_name
        self.case_sensitive = case_sensitive
        
        # Normalize values to list
        if isinstance(values, str):
            self.values = [values]
        else:
            self.values = list(values)
            
        # Normalize case if needed
        if not case_sensitive:
            self.values = [v.lower() for v in self.values]
            
        # Validate match type
        valid_types = ['exact', 'contains', 'starts_with', 'ends_with']
        if match_type not in valid_types:
            raise ValueError(
                f"Invalid match_type: {match_type}. "
                f"Must be one of: {valid_types}"
            )
        self.match_type = match_type
        
    def matches(self, item: Any) -> bool:
        """
        Check if item string matches criteria.
        
        Args:
            item: Item to test
            
        Returns:
            True if string matches criteria
        """
        self.total_processed += 1
        
        # Extract value
        if hasattr(item, 'get'):
            value = item.get(self.field_name)
        elif hasattr(item, self.field_name):
            value = getattr(item, self.field_name)
        else:
            value = item
            
        # Handle null values
        if pd.isna(value) or value is None:
            self.filter_count += 1
            return False
            
        # Convert to string and normalize case
        str_value = str(value)
        if not self.case_sensitive:
            str_value = str_value.lower()
            
        # Apply matching logic
        for target in self.values:
            if self.match_type == "exact":
                if str_value == target:
                    return True
            elif self.match_type == "contains":
                if target in str_value:
                    return True
            elif self.match_type == "starts_with":
                if str_value.startswith(target):
                    return True
            elif self.match_type == "ends_with":
                if str_value.endswith(target):
                    return True
                    
        # No match found
        self.filter_count += 1
        return False
        
    def apply(
        self, 
        data: Union[pd.DataFrame, List[Dict]]
    ) -> Union[pd.DataFrame, List[Dict]]:
        """
        Apply string filter to dataset.
        
        Args:
            data: DataFrame or list of dicts to filter
            
        Returns:
            Filtered data
        """
        if isinstance(data, pd.DataFrame):
            if self.field_name not in data.columns:
                raise ValueError(
                    f"Field '{self.field_name}' not found in DataFrame"
                )
                
            mask = data[self.field_name].apply(lambda x: self.matches(x))
            return data[mask]
            
        elif isinstance(data, list):
            return [item for item in data if self.matches(item)]
            
        else:
            raise TypeError(
                f"Unsupported data type: {type(data)}. "
                "Expected DataFrame or list."
            )