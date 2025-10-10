"""Tests for manual API functions."""

import pytest
import pandas as pd
from luxin.drill_table import _build_source_mapping


def test_build_source_mapping_single_column():
    """Test building source mapping with single groupby column."""
    detail_df = pd.DataFrame({
        'category': ['A', 'A', 'B', 'B', 'C'],
        'value': [10, 20, 30, 40, 50]
    })
    
    agg_df = detail_df.groupby('category').sum()
    
    mapping = _build_source_mapping(agg_df, detail_df, ['category'])
    
    assert len(mapping) == 3
    assert set(mapping[('A',)]) == {0, 1}
    assert set(mapping[('B',)]) == {2, 3}
    assert set(mapping[('C',)]) == {4}


def test_build_source_mapping_multi_column():
    """Test building source mapping with multiple groupby columns."""
    detail_df = pd.DataFrame({
        'cat1': ['A', 'A', 'B', 'B', 'A'],
        'cat2': ['X', 'Y', 'X', 'Y', 'X'],
        'value': [10, 20, 30, 40, 50]
    })
    
    agg_df = detail_df.groupby(['cat1', 'cat2']).sum()
    
    mapping = _build_source_mapping(agg_df, detail_df, ['cat1', 'cat2'])
    
    assert len(mapping) == 4
    assert set(mapping[('A', 'X')]) == {0, 4}
    assert set(mapping[('A', 'Y')]) == {1}
    assert set(mapping[('B', 'X')]) == {2}
    assert set(mapping[('B', 'Y')]) == {3}


def test_build_source_mapping_empty_groups():
    """Test source mapping handles DataFrames with some empty groups."""
    detail_df = pd.DataFrame({
        'category': ['A', 'A', 'B'],
        'value': [10, 20, 30]
    })
    
    agg_df = detail_df.groupby('category').sum()
    
    mapping = _build_source_mapping(agg_df, detail_df, ['category'])
    
    assert len(mapping) == 2
    assert set(mapping[('A',)]) == {0, 1}
    assert set(mapping[('B',)]) == {2}

