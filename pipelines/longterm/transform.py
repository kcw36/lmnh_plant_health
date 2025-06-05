"""Module for transforming data ready for S3."""

from logging import getLogger
from pandas import DataFrame
from pandas.api.typing import DataFrameGroupBy


def get_grouped_data(df: DataFrame) -> DataFrameGroupBy:
    """Return data grouped by key column."""
    logger = getLogger()
    logger.info("Creating group from Dataframe...")
    return df.groupby(by=['plant_id', 'plant_name', 'botanist', 'year', 'month', 'day'])


def get_summary_stats(grouping: DataFrameGroupBy) -> DataFrame:
    """Return Dataframe with summary statistics from group."""
    logger = getLogger()
    logger.info("Getting summary statistics from group object...")
    summary = grouping.agg({'temperature': ['min', 'median', 'max'],
                            'soil_moisture': ['min', 'median', 'max'],
                            'plant_id': 'count'})
    summary.columns = ['_'.join(col).strip('_')
                       for col in summary.columns.values]
    summary = summary.rename(columns={"plant_id_count": "count"})
    summary = summary.reset_index(
        level=['plant_name', 'botanist', 'year', 'month', 'day'])
    return summary


def get_time_parts(data: DataFrame) -> DataFrame:
    """Return dataframe with split time columsn from recording at datetime."""
    logger = getLogger()
    logger.info("Getting time parts from recording column...")
    data['year'] = data['recording_taken'].dt.year
    data['month'] = data['recording_taken'].dt.month
    data['day'] = data['recording_taken'].dt.day
    return data


def get_summary_from_df(raw: DataFrame) -> DataFrame:
    """Return summary Dataframe from regular Dataframe."""
    logger = getLogger()
    logger.info("Getting summary stats from raw dataframe...")
    time_df = get_time_parts(raw)
    grouped_df = get_grouped_data(time_df)
    return get_summary_stats(grouped_df)


if __name__ == "__main__":
    sample_data = {
        "plant_id": [1, 2, 1, 3, 2, 1, 4],
        "plant_name": ["Fern", "Bonsai", "Fern", "Cactus", "Bonsai", "Fern", "Palm"],
        "temperature": [22.5, 18.0, 23.0, 30.0, 19.0, 21.5, 25.0],
        "last_watered": [
            "2025-06-01", "2025-05-28", "2025-06-02",
            "2025-06-03", "2025-05-29", "2025-06-01", "2025-06-04"
        ],
        "soil_moisture": [35, 20, 33, 15, 22, 37, 30],
        "recording_taken": [
            "2025-06-02 10:00", "2025-05-29 09:30", "2025-06-03 11:15",
            "2025-06-04 08:45", "2025-05-30 10:10", "2025-06-02 10:30", "2025-06-05 09:00"
        ],
        "city": ["Seattle", "Portland", "Seattle", "Phoenix", "Portland", "Seattle", "Miami"],
        "country": ["USA", "USA", "USA", "USA", "USA", "USA", "USA"],
        "botanist": ["Alice", "Bob", "Alice", "Charlie", "Bob", "Alice", "Diana"]
    }
    sample_df = DataFrame.from_dict(sample_data)
    print(get_summary_from_df(sample_df))
