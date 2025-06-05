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


@fixture
def test_ungrouped_dataframe():
    return DataFrame({
        "plant_id": [1, 2, 1, 3, 2, 1, 4],
        "plant_name": ["Fern", "Bonsai", "Fern", "Cactus", "Bonsai", "Fern", "Palm"],
        "temperature": [22.5, 18.0, 23.0, 30.0, 19.0, 21.5, 25.0],
        "last_watered": [
            "2025-06-01", "2025-05-28", "2025-06-02",
            "2025-06-03", "2025-05-29", "2025-06-01", "2025-06-04"
        ],
        "soil_moisture": [35.0, 20.0, 33.0, 15.0, 22.0, 37.0, 30.0],
        "recording_taken": [
            "2025-06-02 10:00", "2025-05-29 09:30", "2025-06-03 11:15",
            "2025-06-04 08:45", "2025-05-30 10:10", "2025-06-02 10:30", "2025-06-05 09:00"
        ],
        "city": ["Seattle", "Portland", "Seattle", "Phoenix", "Portland", "Seattle", "Miami"],
        "country": ["USA", "USA", "USA", "USA", "USA", "USA", "USA"],
        "botanist": ["Alice", "Bob", "Alice", "Charlie", "Bob", "Alice", "Diana"]
    })


@fixture
def test_grouper():
    sample = DataFrame({
        "plant_id": [1, 2, 1, 3, 2, 1, 4],
        "plant_name": ["Fern", "Bonsai", "Fern", "Cactus", "Bonsai", "Fern", "Palm"],
        "temperature": [22.5, 18.0, 23.0, 30.0, 19.0, 21.5, 25.0],
        "last_watered": [
            "2025-06-01", "2025-05-28", "2025-06-02",
            "2025-06-03", "2025-05-29", "2025-06-01", "2025-06-04"
        ],
        "soil_moisture": [35.0, 20.0, 33.0, 15.0, 22.0, 37.0, 30.0],
        "recording_taken": [
            "2025-06-02 10:00", "2025-05-29 09:30", "2025-06-03 11:15",
            "2025-06-04 08:45", "2025-05-30 10:10", "2025-06-02 10:30", "2025-06-05 09:00"
        ],
        "city": ["Seattle", "Portland", "Seattle", "Phoenix", "Portland", "Seattle", "Miami"],
        "country": ["USA", "USA", "USA", "USA", "USA", "USA", "USA"],
        "botanist": ["Alice", "Bob", "Alice", "Charlie", "Bob", "Alice", "Diana"]
    })
    return sample.groupby(['plant_id', 'plant_name', 'botanist'])


@fixture
def test_summary_dataframe():
    return DataFrame({
        "plant_id": [1, 2, 3, 4],
        "plant_name": ["Fern", "Bonsai", "Cactus", "Palm"],
        "botanist": ["Alice", "Bob", "Charlie", "Diana"],
        "temperature_min": [21.5, 18.0, 30.0, 25.0],
        "temperature_median": [22.5, 18.5, 30.0, 25.0],
        "temperature_max": [23.0, 19.0, 30.0, 25.0],
        "soil_moisture_min": [33.0, 20.0, 15.0, 30.0],
        "soil_moisture_median": [35.0, 21.0, 15.0, 30.0],
        "soil_moisture_max": [37.0, 22.0, 15.0, 30.0],
        "count": [3, 2, 1, 1]
    }).set_index(keys="plant_id")
