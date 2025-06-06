# pylint: skip-file
import pytest
import pandas as pd
from unittest.mock import patch

from pipeline_short import run_pipeline, lambda_handler


@patch("pipeline_short.transform_data", return_value=pd.DataFrame())
def test_run_pipeline_raises_on_empty_df(mock_transform):
    with pytest.raises(ValueError, match="No cleaned DataFrame received."):
        run_pipeline()


@patch("pipeline_short.transform_data")
@patch("pipeline_short.get_connection")
@patch("pipeline_short.load_data")
def test_run_pipeline_success(mock_load, mock_conn, mock_transform):
    mock_transform.return_value = pd.DataFrame({"plant_id": [1, 2, 3]})
    mock_conn.return_value.__enter__.return_value = "fake_conn"
    run_pipeline()
    mock_load.assert_called_once()


@patch("pipeline_short.run_pipeline", return_value=None)
def test_lambda_handler_success(mock_pipeline):
    response = lambda_handler({}, {})
    assert response["statusCode"] == 200
    assert response["message"] == "Short-term ETL pipeline completed."


@patch("pipeline_short.run_pipeline", side_effect=Exception("failed"))
def test_lambda_handler_fails(mock_pipeline):
    with pytest.raises(RuntimeError, match="Error with Python runtime."):
        lambda_handler({}, {})
