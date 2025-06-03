"""Tests for long term load module."""

from unittest.mock import Mock, patch
from pytest import mark

from load import (create_data_directory,
                  create_parquet,
                  delete_data_directory,
                  load_to_s3)


@mark.parametrize("success", (True, False))
def test_create_data_directory(success):
    """Test that method attempts to create directory."""
    with patch("path.exists") as mock_exists:
        with patch("load.mkdir") as mock_mkdir:
            mock_exists.return_value = success
            actual = create_data_directory()
            mock_mkdir.assert_called_once_with("data")
    assert actual == success


@mark.parametrize("success", (False, True))
def delete_data_directory(success):
    """Test that method attempts to delete directory."""
    with patch("path.exists") as mock_exists:
        with patch("load.rmtree") as mock_rmtree:
            mock_exists.return_value = success
            actual = delete_data_directory()
            mock_rmtree.assert_called_once_with("data")
    assert actual != success


def test_create_parquet():
    """Test that create parquet attempts to make parquet files."""
    mock_dataframe = Mock()
    mock_dataframe.to_parquet.return_value = None
    actual = create_parquet(mock_dataframe)
    mock_dataframe.to_parquet.assert_called()
    assert actual


@mark.parametrize("directory", ([["summary", "summary"], "", ["test/plant_1", "test/plant_2"]],
                                [["093725y1792", "0823528162ef"], "", ["test/plant_1", "test/plant_2"]]))
def test_load_s3(directory):
    """Test that load to S3 attempts to contact client with formatted arguments."""
    mock_client = Mock()
    mock_client.upload_file.return_value = None
    with patch("load.walk") as mock_walk:
        mock_walk.return_value = directory
        load_to_s3(mock_client)
        mock_client.upload_file.assert_called()
