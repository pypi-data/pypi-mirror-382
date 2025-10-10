"""
TrackedDataFrame - A pandas DataFrame subclass that tracks source rows during aggregations.
"""

import pandas as pd
from typing import Any, Dict, List, Optional
import uuid


class TrackedDataFrame(pd.DataFrame):
    """
    A pandas DataFrame subclass that automatically tracks which source rows
    contribute to each aggregated row during groupby operations.
    
    Attributes:
        _source_mapping: Dictionary mapping aggregated row IDs to lists of source row indices
        _is_aggregated: Boolean indicating if this DataFrame is an aggregation result
        _groupby_cols: List of column names used in the groupby operation
    """
    
    _metadata = ['_source_mapping', '_is_aggregated', '_groupby_cols', '_source_df']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._source_mapping: Dict[Any, List[int]] = {}
        self._is_aggregated = False
        self._groupby_cols: List[str] = []
        self._source_df: Optional[pd.DataFrame] = None
    
    @property
    def _constructor(self):
        return TrackedDataFrame
    
    def groupby(self, by=None, **kwargs):
        """Override groupby to return a TrackedGroupBy object."""
        return TrackedGroupBy(self, by, **kwargs)
    
    def show_drill_table(self):
        """Display the interactive drill-down table."""
        if not self._is_aggregated:
            raise ValueError(
                "show_drill_table() can only be called on aggregated DataFrames. "
                "Use groupby().agg() first, or use create_drill_table() for manual setup."
            )
        
        from luxin.display import display_drill_table
        display_drill_table(self, self._source_df, self._source_mapping, self._groupby_cols)


class TrackedGroupBy:
    """
    A wrapper around pandas GroupBy that tracks source row indices during aggregation.
    """
    
    def __init__(self, df: TrackedDataFrame, by, **kwargs):
        self.tracked_df = df
        self.by = by if isinstance(by, list) else [by]
        self.groupby_obj = pd.DataFrame(df).groupby(by, **kwargs)
    
    def agg(self, func=None, *args, **kwargs):
        """
        Perform aggregation while tracking source row indices.
        """
        # Perform the actual aggregation on the underlying DataFrame
        result = self.groupby_obj.agg(func, *args, **kwargs)
        
        # Create a TrackedDataFrame from the result
        tracked_result = TrackedDataFrame(result)
        tracked_result._is_aggregated = True
        tracked_result._groupby_cols = self.by
        tracked_result._source_df = pd.DataFrame(self.tracked_df)
        
        # Build the source mapping
        source_mapping = {}
        
        # Get the groups and their indices
        for group_key, group_indices in self.groupby_obj.groups.items():
            # Convert group_key to a tuple if it's not already
            if not isinstance(group_key, tuple):
                group_key = (group_key,)
            
            # Store the mapping using the group key
            # The result index will match the group keys
            source_mapping[group_key] = list(group_indices)
        
        tracked_result._source_mapping = source_mapping
        
        return tracked_result
    
    def sum(self, *args, **kwargs):
        """Sum aggregation with tracking."""
        return self.agg('sum', *args, **kwargs)
    
    def mean(self, *args, **kwargs):
        """Mean aggregation with tracking."""
        return self.agg('mean', *args, **kwargs)
    
    def count(self, *args, **kwargs):
        """Count aggregation with tracking."""
        return self.agg('count', *args, **kwargs)
    
    def min(self, *args, **kwargs):
        """Min aggregation with tracking."""
        return self.agg('min', *args, **kwargs)
    
    def max(self, *args, **kwargs):
        """Max aggregation with tracking."""
        return self.agg('max', *args, **kwargs)
    
    def std(self, *args, **kwargs):
        """Standard deviation with tracking."""
        return self.agg('std', *args, **kwargs)
    
    def var(self, *args, **kwargs):
        """Variance with tracking."""
        return self.agg('var', *args, **kwargs)
    
    def median(self, *args, **kwargs):
        """Median with tracking."""
        return self.agg('median', *args, **kwargs)
    
    def __getattr__(self, name):
        """Delegate other methods to the underlying GroupBy object."""
        return getattr(self.groupby_obj, name)

