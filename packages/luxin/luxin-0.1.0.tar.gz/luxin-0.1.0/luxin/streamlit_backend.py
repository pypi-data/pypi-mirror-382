"""
Streamlit backend for displaying interactive drill-down tables.
"""

import pandas as pd
from typing import Dict, Any, List


def display_streamlit(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: Dict[Any, List[int]],
    groupby_cols: List[str],
    **kwargs
):
    """
    Display an interactive drill-down table in Streamlit.
    
    Args:
        agg_df: The aggregated DataFrame to display
        detail_df: The detail DataFrame containing source rows
        source_mapping: Dictionary mapping aggregated row keys to detail row indices
        groupby_cols: List of column names used to group the data
        **kwargs: Additional options for display customization
    """
    try:
        import streamlit as st
        import streamlit.components.v1 as components
    except ImportError:
        raise ImportError(
            "Streamlit is required for Streamlit backend. "
            "Install with: pip install luxin[streamlit]"
        )
    
    from luxin.display import render_html
    
    # Render the HTML
    html = render_html(agg_df, detail_df, source_mapping, groupby_cols)
    
    # Get height from kwargs or use default
    height = kwargs.get('height', 600)
    
    # Display in Streamlit using components
    components.html(html, height=height, scrolling=True)

