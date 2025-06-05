# pylint: skip-file
"""Script to test functionality of the `load_short.py` script."""
from unittest.mock import MagicMock, patch
import pandas as pd
from load_short import insert_origin_country


@patch("load_short.getLogger")
@patch("pandas.read_sql")
def test_insert_origin_country_with_new_data(mock_read_sql, mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    mock_read_sql.return_value = pd.DataFrame({"name": ["France"]})

    test_data = pd.DataFrame({"origin_country": ["France", "Germany"]})

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    insert_origin_country(test_data, mock_conn)

    mock_cursor.executemany.assert_called_once_with(
        "INSERT INTO gamma.origin_country (name) VALUES (?);",
        [("Germany",)]
    )
    mock_conn.commit.assert_called_once()
    mock_logger.info.assert_any_call("Inserted %d new countries.", 1)


@patch("load_short.getLogger")
@patch("pandas.read_sql")
def test_insert_origin_country_with_no_new_data(mock_read_sql, mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    mock_read_sql.return_value = pd.DataFrame({"name": ["France", "Germany"]})

    test_data = pd.DataFrame({"origin_country": ["France", "Germany"]})

    mock_conn = MagicMock()

    insert_origin_country(test_data, mock_conn)

    mock_conn.cursor.assert_not_called()
    mock_logger.info.assert_any_call("No new countries to insert.")
