"""Tests for display module."""

import pytest
import pandas as pd
from luxin.display import render_html, _detect_environment


def test_detect_environment():
    """Test environment detection."""
    env = _detect_environment()
    # Should return one of the valid environment types
    assert env in ['jupyter', 'streamlit', 'unknown']


def test_render_html_basic():
    """Test basic HTML rendering."""
    detail_df = pd.DataFrame({
        'category': ['A', 'A', 'B', 'B'],
        'value': [10, 20, 30, 40]
    })
    
    agg_df = detail_df.groupby('category').sum()
    
    source_mapping = {
        ('A',): [0, 1],
        ('B',): [2, 3]
    }
    
    html = render_html(agg_df, detail_df, source_mapping, ['category'])
    
    # Check that HTML contains expected elements
    assert '<html>' in html
    assert '<style>' in html
    assert '<script>' in html
    assert 'luxin-container' in html
    assert 'detail-panel' in html


def test_render_html_with_multiindex():
    """Test HTML rendering with multi-index aggregation."""
    detail_df = pd.DataFrame({
        'cat1': ['A', 'A', 'B', 'B'],
        'cat2': ['X', 'Y', 'X', 'Y'],
        'value': [10, 20, 30, 40]
    })
    
    agg_df = detail_df.groupby(['cat1', 'cat2']).sum()
    
    source_mapping = {
        ('A', 'X'): [0],
        ('A', 'Y'): [1],
        ('B', 'X'): [2],
        ('B', 'Y'): [3]
    }
    
    html = render_html(agg_df, detail_df, source_mapping, ['cat1', 'cat2'])
    
    # Check that HTML is generated
    assert '<html>' in html
    assert len(html) > 0

