# -*- coding: utf-8 -*-
"""
Tests for the dataframing module
"""

import pytest
import pandas as pd
import numpy as np
from datashadric.dataframing import df_check_na_values, df_drop_dupes


def test_df_check_na_values(sample_dataframe):
    """test the na values checking function"""
    result = df_check_na_values(sample_dataframe)
    
    # should return a dataframe (same as input.isna())
    assert isinstance(result, pd.DataFrame)
    
    # should have the same shape as input
    assert result.shape == sample_dataframe.shape
    
    # should have the same columns as input
    assert list(result.columns) == list(sample_dataframe.columns)


def test_df_drop_dupes():
    """test the drop duplicates function"""
    # create dataframe with duplicates
    df_with_dupes = pd.DataFrame({
        'A': [1, 2, 2, 3],
        'B': [4, 5, 5, 6]
    })
    
    # test with col_dupes parameter (required)
    result = df_drop_dupes(df_with_dupes, 0)  # col_dupes=0 parameter
    
    # should return dataframe with no duplicates
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3  # one duplicate should be removed
    assert not result.duplicated().any()


def test_empty_dataframe():
    """test functions handle empty dataframes gracefully"""
    empty_df = pd.DataFrame()
    
    # these should not crash
    na_result = df_check_na_values(empty_df)
    assert isinstance(na_result, pd.DataFrame)
    
    dupe_result = df_drop_dupes(empty_df, 0)  # col_dupes=0 parameter
    assert isinstance(dupe_result, pd.DataFrame)
    assert len(dupe_result) == 0