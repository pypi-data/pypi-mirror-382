"""Tests for TrackedDataFrame class."""

import pytest
import pandas as pd
from luxin import TrackedDataFrame


def test_tracked_dataframe_creation():
    """Test creating a TrackedDataFrame."""
    data = {'a': [1, 2, 3], 'b': [4, 5, 6]}
    df = TrackedDataFrame(data)
    
    assert isinstance(df, TrackedDataFrame)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3


def test_tracked_dataframe_groupby():
    """Test groupby on TrackedDataFrame."""
    data = {
        'category': ['A', 'A', 'B', 'B', 'C'],
        'value': [10, 20, 30, 40, 50]
    }
    df = TrackedDataFrame(data)
    
    grouped = df.groupby('category')
    assert grouped is not None


def test_tracked_dataframe_agg():
    """Test aggregation tracking."""
    data = {
        'category': ['A', 'A', 'B', 'B', 'C'],
        'value': [10, 20, 30, 40, 50]
    }
    df = TrackedDataFrame(data)
    
    result = df.groupby('category').agg({'value': 'sum'})
    
    assert isinstance(result, TrackedDataFrame)
    assert result._is_aggregated
    assert len(result._source_mapping) == 3
    assert result._groupby_cols == ['category']


def test_source_mapping_accuracy():
    """Test that source mapping correctly tracks indices."""
    data = {
        'category': ['A', 'A', 'B', 'B', 'C'],
        'value': [10, 20, 30, 40, 50]
    }
    df = TrackedDataFrame(data)
    
    result = df.groupby('category').agg({'value': 'sum'})
    
    # Check that category A maps to indices 0 and 1
    assert ('A',) in result._source_mapping
    assert set(result._source_mapping[('A',)]) == {0, 1}
    
    # Check that category B maps to indices 2 and 3
    assert ('B',) in result._source_mapping
    assert set(result._source_mapping[('B',)]) == {2, 3}
    
    # Check that category C maps to index 4
    assert ('C',) in result._source_mapping
    assert set(result._source_mapping[('C',)]) == {4}


def test_multi_column_groupby():
    """Test groupby with multiple columns."""
    data = {
        'cat1': ['A', 'A', 'B', 'B', 'A'],
        'cat2': ['X', 'Y', 'X', 'Y', 'X'],
        'value': [10, 20, 30, 40, 50]
    }
    df = TrackedDataFrame(data)
    
    result = df.groupby(['cat1', 'cat2']).agg({'value': 'sum'})
    
    assert result._is_aggregated
    assert len(result._source_mapping) == 4
    assert result._groupby_cols == ['cat1', 'cat2']


def test_show_drill_table_requires_aggregation():
    """Test that show_drill_table raises error on non-aggregated DataFrame."""
    data = {'a': [1, 2, 3], 'b': [4, 5, 6]}
    df = TrackedDataFrame(data)
    
    with pytest.raises(ValueError, match="can only be called on aggregated DataFrames"):
        df.show_drill_table()

