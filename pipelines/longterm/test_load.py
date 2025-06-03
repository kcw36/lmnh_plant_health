"""Tests for long term load module."""

from unittest.mock import Mock, patch, call
from pytest import mark

from load import (create_data_directory,
                  create_parquet,
                  delete_data_directory,
                  load_to_s3)


@mark.parametrize("exists", (True, False))
def test_create_data_directory(exists):
    """Test that method attempts to create directory."""
    with patch("load.path.exists") as mock_exists:
        with patch("load.mkdir") as mock_mkdir:
            mock_exists.return_value = exists
            actual = create_data_directory()
            if exists:
                mock_mkdir.assert_not_called()
            else:
                mock_mkdir.assert_has_calls([call("data"), call("data/plant")])
    assert actual != exists


@mark.parametrize("success", (False, True))
def delete_data_directory(success):
    """Test that method attempts to delete directory."""
    with patch("load.path.exists") as mock_exists:
        with patch("load.rmtree") as mock_rmtree:
            mock_exists.return_value = success
            actual = delete_data_directory()
            mock_rmtree.assert_called_once_with("data")
    assert actual != success


def test_create_parquet():
    """Test that create parquet attempts to make parquet files."""
    mock_dataframe = Mock()
    mock_table_instance = Mock()
    with patch("load.Table") as mock_table:
        with patch("load.pq.write_to_dataset") as mock_write:
            mock_table.from_pandas.return_value = mock_table_instance
            actual = create_parquet(mock_dataframe)
            mock_table.from_pandas.assert_called()
            mock_write.assert_called()
            assert actual


@mark.parametrize("directory", ((("test/planyt_1", "", "summary"), ("test/plant_2", "", "summary")),
                                (("test/planyt_1", "", "hs766sgvhba7d"), ("test/plant_2", "", "hs766sgvhba7d"))))
def test_load_s3(directory):
    """Test that load to S3 attempts to contact client with formatted arguments."""
    mock_client = Mock()
    mock_client.upload_file.return_value = None
    print(directory)
    with patch("load.walk") as mock_walk:
        with patch("load.ENV") as mock_environ:
            mock_walk.return_value = directory
            load_to_s3(mock_client)
            mock_client.upload_file.assert_called()
