# pylint: skip-file
"""Script to test functionality of the `load_short.py` script."""
from unittest.mock import MagicMock, patch
import pandas as pd
from load_short import insert_origin_country, insert_botanist, insert_origin_city, load_data


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


@patch("load_short.getLogger")
@patch("pandas.read_sql")
def test_insert_botanist_with_new_data(mock_read_sql, mock_get_logger):

    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    mock_read_sql.return_value = pd.DataFrame({"name": ["Kenneth Buckridge"],
                                               "email": ["kenneth.buckridge@lnhm.co.uk"],
                                               "phone": ["+447639148635"]})

    test_data = pd.DataFrame({
        "botanist_name": ["Kenneth Buckridge", "Wilson Welch"],
        "botanist_email": ["kenneth.buckridge@lnhm.co.uk", "wilson.welch@lnhm.co.uk"],
        "botanist_phone": ["+447639148635", "+449536074239"]

    })
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    insert_botanist(test_data, mock_conn)

    mock_cursor.executemany.assert_called_once_with(
        "INSERT INTO gamma.botanist (name, email, phone) VALUES (?, ?, ?);",
        [("Wilson Welch", "wilson.welch@lnhm.co.uk", "+449536074239")]
    )

    mock_conn.commit.assert_called_once()
    mock_logger.info.assert_any_call("Inserted %d new botanists.", 1)


@patch("load_short.getLogger")
@patch("pandas.read_sql")
def test_insert_botanist_with_no_new_data(mock_read_sql, mock_get_logger):

    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    mock_read_sql.return_value = pd.DataFrame(
        {"name": ["Kenneth Buckridge", "Wilson Welch"],
         "email": ["kenneth.buckridge@lnhm.co.uk", "wilson.welch@lnhm.co.uk"],
         "phone": ["+447639148635", "+449536074239"]})

    test_data = pd.DataFrame({
        "botanist_name": ["Kenneth Buckridge", "Wilson Welch"],
        "botanist_email": ["kenneth.buckridge@lnhm.co.uk", "wilson.welch@lnhm.co.uk"],
        "botanist_phone": ["+447639148635", "+449536074239"]

    })
    mock_conn = MagicMock()

    insert_botanist(test_data, mock_conn)

    mock_conn.commit.assert_not_called()
    mock_logger.info.assert_any_call("No new botanists to insert.")


@patch("load_short.getLogger")
@patch("pandas.read_sql")
def test_insert_origin_city_with_new_data(mock_read_sql, mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    mock_country = pd.DataFrame({
        "name": ["Albania", "American Samoa"],
        "country_id": [1, 2]
    })

    mock_city = pd.DataFrame({
        "name": ["Stammside"],
        "country_id": [1]
    })

    mock_read_sql.side_effect = [mock_country, mock_city]

    test_data = pd.DataFrame({"origin_city": ["Stammside", "Floshire"],
                              "origin_country": ["Albania", "American Samoa"]})

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    insert_origin_city(test_data, mock_conn)

    mock_cursor.executemany.assert_called_once_with(
        "INSERT INTO gamma.origin_city (name, country_id) VALUES (?, ?)",
        [("Floshire", 2)]
    )

    mock_conn.commit.assert_called_once()
    mock_logger.info.assert_any_call("Inserted %d new cities.", 1)


@patch("load_short.getLogger")
@patch("pandas.read_sql")
def test_insert_origin_city_with_no_new_data(mock_read_sql, mock_get_logger):

    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    mock_read_sql.return_value = pd.DataFrame(
        {"name": ["Stammside", "Floshire"],
         "country_id": [1, 2]})

    test_data = pd.DataFrame({"origin_city": ["Stammside", "Floshire"],
                              "origin_country": ["Albania", "American Samoa"]})

    mock_conn = MagicMock()

    insert_origin_city(test_data, mock_conn)

    mock_conn.cursor.assert_not_called()
    mock_logger.info.assert_any_call("No new cities to insert.")


@patch("load_short.insert_origin_country")
@patch("load_short.insert_origin_city")
@patch("load_short.insert_botanist")
@patch("load_short.insert_plant")
@patch("load_short.insert_botanist_plant")
@patch("load_short.insert_record")
@patch("load_short.getLogger")
def test_load_data(mock_logger, mock_record, mock_bp, mock_plant, mock_botanist, mock_city, mock_country):

    mock_data = pd.DataFrame({
        "plant_id": [1],
        "name": ["Venus flytrap"],
        "origin_city": ["Stammside"],
        "origin_country": ["Albania"],
        "temperature": [14.77],
        "last_watered": ['2025-06-04 13: 51: 41+00: 00'],
        "soil_moisture": [19.24],
        "recording_taken": ['2025-06-05 12: 35: 06.588000+00: 00'],
        "botanist_name": ["Kenneth Buckridge"],
        "botanist_email": ["kenneth.buckridge@lnhm.co.uk"],
        "botanist_phone": ["+447639148635"]
    })

    mock_conn = MagicMock()

    load_data(mock_data, mock_conn)

    mock_country.assert_called_once_with(mock_data, mock_conn)
    mock_city.assert_called_once_with(mock_data, mock_conn)
    mock_botanist.assert_called_once_with(mock_data, mock_conn)
    mock_plant.assert_called_once_with(mock_data, mock_conn)
    mock_bp.assert_called_once_with(mock_data, mock_conn)
    mock_record.assert_called_once_with(mock_data, mock_conn)
