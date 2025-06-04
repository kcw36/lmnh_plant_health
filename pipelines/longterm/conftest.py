# pylint: skip-file
"""Module for test fixtures in historic pipeline."""

from pytest import fixture
from pandas import DataFrame


@fixture
def test_good_rows():
    return [
        [1, "Mike", 10, "then", 5, "this year", "LA", "USA", "Steve"],
        [2, "Stan", 80, "after", 10, "that year", "BRUM", "UK", "Michael"],
        [3, "Geoff", 60, "now", 2, "then year",
            "MANNY", "united Kingdom", "Theodore"]
    ]


@fixture
def test_bad_rows():
    return [
        [1, "Mike", "then", 5, "this year", "LA", "USA", "Steve"],
        [2, "Stan", 80, "after", "that year", "BRUM", "UK", "Michael"],
        [3, "Geoff", 60, "now", 2, "then year", "MANNY", "Theodore"]
    ]


@fixture
def test_empty_dictionary():
    return {
        "plant_id": [],
        "plant_name": [],
        "temperature": [],
        "last_watered": [],
        "soil_moisture": [],
        "recording_taken": [],
        "city": [],
        "country": [],
        "botanist": []
    }


@fixture
def test_dictionary():
    return {
        "plant_id": [1, 2, 3],
        "plant_name": ["Mike", "Stan", "Geoff"],
        "temperature": [10, 80, 60],
        "last_watered": ["then", "after", "now"],
        "soil_moisture": [5, 10, 2],
        "recording_taken": ["this year", "that year", "then year"],
        "city": ["LA", "BRUM", "MANNY"],
        "country": ["USA", "UK", "united Kingdom"],
        "botanist": ["Steve", "Michael", "Theodore"]
    }


@fixture
def test_sample_dataframe():
    return DataFrame({
        "plant_id": [1, 2, 3],
        "plant_name": ["Mike", "Stan", "Geoff"],
        "temperature": [10, 80, 60],
        "last_watered": ["then", "after", "now"],
        "soil_moisture": [5, 10, 2],
        "recording_taken": ["this year", "that year", "then year"],
        "city": ["LA", "BRUM", "MANNY"],
        "country": ["USA", "UK", "united Kingdom"],
        "botanist": ["Steve", "Michael", "Theodore"]
    })
