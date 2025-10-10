"""
Manual API for creating drill-down tables from existing DataFrames.
"""

import pandas as pd
from typing import List, Dict, Any, Optional


def create_drill_table(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    groupby_cols: List[str],
    **kwargs
):
    """
    Create an interactive drill-down table from aggregated and detail DataFrames.
    
    Args:
        agg_df: The aggregated DataFrame to display
        detail_df: The detail DataFrame containing source rows
        groupby_cols: List of column names used to group the data
        **kwargs: Additional options for display customization
        
    Example:
        >>> import pandas as pd
        >>> from luxin import create_drill_table
        >>> 
        >>> df = pd.DataFrame({
        ...     'category': ['A', 'A', 'B', 'B'],
        ...     'sales': [100, 200, 150, 250]
        ... })
        >>> agg_df = df.groupby('category').sum()
        >>> create_drill_table(agg_df, df, groupby_cols=['category'])
    """
    # Build the source mapping by matching groupby column values
    source_mapping = _build_source_mapping(agg_df, detail_df, groupby_cols)
    
    from luxin.display import display_drill_table
    display_drill_table(agg_df, detail_df, source_mapping, groupby_cols, **kwargs)


def _build_source_mapping(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    groupby_cols: List[str]
) -> Dict[Any, List[int]]:
    """
    Build a mapping from aggregated row keys to detail row indices.
    
    Args:
        agg_df: The aggregated DataFrame
        detail_df: The detail DataFrame
        groupby_cols: List of column names used to group the data
        
    Returns:
        Dictionary mapping aggregated row keys to lists of detail row indices
    """
    source_mapping = {}
    
    # Handle single vs multi-index
    if isinstance(agg_df.index, pd.MultiIndex):
        # Multi-index case
        for idx in agg_df.index:
            # idx is already a tuple
            group_key = idx
            
            # Build filter condition
            mask = pd.Series([True] * len(detail_df))
            for col, val in zip(groupby_cols, group_key):
                mask &= (detail_df[col] == val)
            
            # Get matching indices
            matching_indices = detail_df[mask].index.tolist()
            source_mapping[group_key] = matching_indices
    else:
        # Single column groupby
        for idx in agg_df.index:
            group_key = (idx,)
            
            # Build filter condition
            mask = (detail_df[groupby_cols[0]] == idx)
            
            # Get matching indices
            matching_indices = detail_df[mask].index.tolist()
            source_mapping[group_key] = matching_indices
    
    return source_mapping

