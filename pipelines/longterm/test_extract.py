# pylint: skip-file
"""Tests for extract module."""

from os import environ

from pandas import DataFrame
from pytest import mark, raises
from unittest.mock import MagicMock, patch

from extract import (get_dataframe_from_dict, get_dict_from_rows,
                     get_full_data, get_schema,
                     truncate_record)


def test_get_dataframe_from_dict(test_dictionary, test_sample_dataframe):
    """Test get dataframe from dict handles positive case."""
    actual = get_dataframe_from_dict(
        test_dictionary)

    assert isinstance(actual, DataFrame)
    assert actual.equals(test_sample_dataframe)


@mark.parametrize("case", (True, False))
def test_get_dict_from_rows(case, test_bad_rows, test_good_rows, test_empty_dictionary, test_dictionary):
    """Test get dictionary from rows handles expected cases."""
    test_in = test_good_rows if case else test_bad_rows
    expected = test_dictionary if case else test_empty_dictionary

    actual = get_dict_from_rows(test_in)

    assert isinstance(actual, dict)
    assert actual == expected


@mark.parametrize("sql_response", ("some data", ""))
def test_get_full_data(sql_response):
    """Test get full data handles expected cases correctly."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = sql_response
    mock_cursor.execute.return_value = None

    actual = get_full_data(mock_connection, "test-schema")

    assert actual == sql_response


def test_valid_schema_identifier():
    """Tests that get schema handles correct input."""
    with patch.dict(environ, {"DB_SCHEMA": "valid_schema_1"}):
        assert get_schema() == "valid_schema_1"


def test_invalid_schema_identifier_raises():
    """Tests that get schema raises error on incorrect input."""
    with patch.dict(environ, {"DB_SCHEMA": "123-invalid-schema"}):
        with raises(ValueError, match="Invalid schema name: 123-invalid-schema"):
            get_schema()


def test_truncate_record():
    """Tests that truncate record sends ecpected request."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    truncate_record(mock_conn, "test_schema")

    mock_cursor.execute.assert_called_once_with(
        "TRUNCATE TABLE test_schema.record;")
    mock_cursor.commit.assert_called_once()
