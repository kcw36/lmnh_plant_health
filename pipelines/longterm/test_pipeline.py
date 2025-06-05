# pylint: skip-file
"""Module for testing pipeline script."""

from logging import getLogger, StreamHandler, INFO
from sys import stdout
from unittest.mock import patch, MagicMock

from pytest import mark, raises

from pipeline import run


def test_run_valid(caplog):
    """Test run across expected valid case."""
    mock_data = MagicMock()
    mock_data.empty = False

    mock_summary = MagicMock()
    mock_summary.empty = False

    logger = getLogger()
    logger.setLevel(INFO)

    handler = StreamHandler(stdout)
    handler.setLevel(INFO)
    logger.addHandler(handler)

    with patch('pipeline.get_data_from_rds', return_value=mock_data), \
            patch('pipeline.get_summary_from_df', return_value=mock_summary), \
            patch('pipeline.load_all') as mock_load:
        run()

        mock_load.assert_called_once_with(mock_summary)
        out = caplog.text
        assert "Attempting pipeline run..." in out
        assert "Successfully recieved data from RDS!" in out
        assert "Successfully summarised data from RDS!" in out
        assert "Successfully loaded data into S3!" in out


def test_run_rds_empty():
    """Test run when RDS has no data."""
    mock_data = MagicMock()
    mock_data.empty = True

    with patch('pipeline.get_data_from_rds', return_value=mock_data), \
            patch('pipeline.get_summary_from_df'), \
            patch('pipeline.load_all'):

        with raises(ValueError, match="Recieved no data from RDS."):
            run()


def test_run_no_summary_data():
    """Test run when summary data cannot be pulled from Dataframe."""
    mock_data = MagicMock()
    mock_data.empty = False

    mock_summary = MagicMock()
    mock_summary.empty = True

    with patch('pipeline.get_data_from_rds', return_value=mock_data), \
            patch('pipeline.get_summary_from_df', return_value=mock_summary), \
            patch('pipeline.load_all'):

        with raises(ValueError, match="Found no summary data from returned raw data!"):
            run()
