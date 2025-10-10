"""
Main display module that detects the environment and routes to the appropriate backend.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
import json
import os


def display_drill_table(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: Dict[Any, List[int]],
    groupby_cols: List[str],
    **kwargs
):
    """
    Display an interactive drill-down table.
    
    Detects the current environment (Jupyter or Streamlit) and uses
    the appropriate backend for rendering.
    
    Args:
        agg_df: The aggregated DataFrame to display
        detail_df: The detail DataFrame containing source rows
        source_mapping: Dictionary mapping aggregated row keys to detail row indices
        groupby_cols: List of column names used to group the data
        **kwargs: Additional options for display customization
    """
    # Detect environment
    env = _detect_environment()
    
    if env == 'jupyter':
        from luxin.jupyter_backend import display_jupyter
        display_jupyter(agg_df, detail_df, source_mapping, groupby_cols, **kwargs)
    elif env == 'streamlit':
        from luxin.streamlit_backend import display_streamlit
        display_streamlit(agg_df, detail_df, source_mapping, groupby_cols, **kwargs)
    else:
        # Fallback to Jupyter-style display
        from luxin.jupyter_backend import display_jupyter
        display_jupyter(agg_df, detail_df, source_mapping, groupby_cols, **kwargs)


def _detect_environment() -> str:
    """
    Detect the current execution environment.
    
    Returns:
        'jupyter', 'streamlit', or 'unknown'
    """
    # Check for Streamlit
    try:
        import streamlit as st
        # Streamlit sets this environment variable
        if hasattr(st, 'session_state'):
            return 'streamlit'
    except ImportError:
        pass
    
    # Check for Jupyter/IPython
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            return 'jupyter'
    except ImportError:
        pass
    
    return 'unknown'


def render_html(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: Dict[Any, List[int]],
    groupby_cols: List[str]
) -> str:
    """
    Render the HTML for the drill-down table.
    
    Args:
        agg_df: The aggregated DataFrame to display
        detail_df: The detail DataFrame containing source rows
        source_mapping: Dictionary mapping aggregated row keys to detail row indices
        groupby_cols: List of column names used to group the data
        
    Returns:
        Complete HTML string for the interactive table
    """
    import random
    import string
    
    # Generate unique ID for this table instance
    unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    # Load templates
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'table.html')
    css_path = os.path.join(os.path.dirname(__file__), 'static', 'table.css')
    js_path = os.path.join(os.path.dirname(__file__), 'static', 'table.js')
    
    with open(template_path, 'r') as f:
        template = f.read()
    
    with open(css_path, 'r') as f:
        css = f.read()
    
    with open(js_path, 'r') as f:
        javascript = f.read()
    
    # Convert aggregated DataFrame to HTML table
    agg_table_html = agg_df.to_html(classes='luxin-table', border=0)
    
    # Prepare detail data as JSON (convert to dict of dicts)
    detail_data = detail_df.to_dict(orient='index')
    # Convert index to string keys for JSON serialization
    detail_data = {str(k): v for k, v in detail_data.items()}
    
    # Prepare source mapping for JSON (convert keys to strings)
    json_mapping = {}
    for key, indices in source_mapping.items():
        # Convert tuple keys to strings
        if isinstance(key, tuple):
            str_key = '|'.join(str(k) for k in key)
        else:
            str_key = str(key)
        json_mapping[str_key] = [str(idx) for idx in indices]
    
    # Inject data into JavaScript
    javascript = javascript.replace(
        '{source_mapping}',
        json.dumps(json_mapping, indent=2)
    )
    javascript = javascript.replace(
        '{detail_data}',
        json.dumps(detail_data, indent=2, default=str)
    )
    javascript = javascript.replace(
        '{groupby_cols}',
        json.dumps(groupby_cols)
    )
    javascript = javascript.replace(
        '{unique_id}',
        unique_id
    )
    
    # Assemble final HTML
    html = template.replace('{css}', css)
    html = html.replace('{agg_table}', agg_table_html)
    html = html.replace('{javascript}', javascript)
    html = html.replace('{unique_id}', unique_id)
    
    return html

