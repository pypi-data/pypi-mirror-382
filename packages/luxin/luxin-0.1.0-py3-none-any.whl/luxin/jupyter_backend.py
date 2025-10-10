"""
Jupyter notebook backend for displaying interactive drill-down tables.
"""

import pandas as pd
from typing import Dict, Any, List
from IPython.display import display, HTML


def display_jupyter(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: Dict[Any, List[int]],
    groupby_cols: List[str],
    **kwargs
):
    """
    Display an interactive drill-down table in Jupyter notebook.
    
    Args:
        agg_df: The aggregated DataFrame to display
        detail_df: The detail DataFrame containing source rows
        source_mapping: Dictionary mapping aggregated row keys to detail row indices
        groupby_cols: List of column names used to group the data
        **kwargs: Additional options for display customization
    """
    from luxin.display import render_html
    
    # Render the HTML
    html = render_html(agg_df, detail_df, source_mapping, groupby_cols)
    
    # Display in notebook
    display(HTML(html))

