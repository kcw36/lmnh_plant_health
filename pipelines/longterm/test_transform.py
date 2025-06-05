# pylint: skip-file

"""Module for testing transform methods."""

from pandas.api.typing import DataFrameGroupBy
from pandas import DataFrame

from transform import (get_grouped_data, get_summary_from_df,
                       get_summary_stats)


def test_get_grouped_data(test_ungrouped_dataframe):
    """Test get grouped data groups."""
    actual = get_grouped_data(test_ungrouped_dataframe)
    assert isinstance(actual, DataFrameGroupBy)


def test_get_summary_stats(test_grouper, test_summary_dataframe):
    """Test get summary stats creates expected DataFrame."""
    actual = get_summary_stats(test_grouper)
    assert isinstance(actual, DataFrame)
    assert actual.equals(test_summary_dataframe)


def test_get_summary_from_df(test_ungrouped_dataframe, test_summary_dataframe):
    """Test get summary from df returns grouped Dataframe from raw Dataframe."""
    actual = get_summary_from_df(test_ungrouped_dataframe)
    assert actual.equals(test_summary_dataframe)
