"""Test script for `pipeline_short.py`."""
import pytest
import pandas as pd
from unittest.mock import patch

import pipeline_short


def test_run_pipeline_raises_if_empty():

    with patch("pipeline_short.transform_data", return_value=pd.DataFrame()):
        with patch("pipeline_short.get_connection"), patch("pipeline_short.load_data"):
            # import pipeline_short
            with pytest.raises(ValueError, match="No cleaned DataFrame received."):
                pipeline_short.run_pipeline()


def test_lambda_handler_returns_success():

    with patch("pipeline_short.run_pipeline"):
        # import pipeline_short
        result = pipeline_short.lambda_handler({}, {})
        assert result["statusCode"] == 200


def test_run_pipeline_runs_with_valid_data():

    fake_data = pd.DataFrame({"plant_id": [1]})

    with patch("pipeline_short.transform_data", return_value=fake_data):
        with patch("pipeline_short.get_connection"):
            with patch("pipeline_short.load_data") as fake_load:
                # import pipeline_short
                pipeline_short.run_pipeline()
                fake_load.assert_called_once()
