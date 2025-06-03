"""Module for loading long term data to S3."""

from logging import getLogger
from os import environ as ENV, path, walk, mkdir
from shutil import rmtree

from pandas import DataFrame
from boto3 import client
from dotenv import load_dotenv
from pyarrow import Table, parquet as pq


def create_data_directory() -> bool:
    """Return true if data directory created successfully"""
    logger = getLogger(__name__)
    logger.info("Creating empty data directory for Parquet files...")
    if not path.exists("data"):
        mkdir("data")
        mkdir("data/plant")
        return True
    return False


def delete_data_directory() -> bool:
    """Return true if deleted data directory"""
    logger = getLogger(__name__)
    logger.info("Deleting filled data directory...")
    rmtree("data")
    if not path.exists("data"):
        return False
    return True


def create_parquet(data: DataFrame) -> bool:
    """Save data as parquet files."""
    logger = getLogger(__name__)
    logger.info("Storing local parquet files...")
    datatable = Table.from_pandas(data)
    if not datatable:
        logger.error("No data given.")
        return False
    pq.write_to_dataset(datatable, root_path="data/plant",
                        partition_cols=["year", "month", "day", "plant_id"],
                        basename_template="summary")
    logger.info("Parquet created successfully.")
    return True


def get_s3_client() -> client:
    """Return client to s3 bucket."""
    logger = getLogger(__name__)
    logger.info("Return S3 client")
    return client("s3",
                  aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])


def load_to_s3(awsclient: client) -> bool:
    """Load objects to s3."""
    logger = getLogger(__name__)
    logger.info("Starting load to S3...")
    has_data = False
    for root, _, files in walk("data"):
        if files:
            has_data = True
            for file in files:
                full_path = path.join(root, file)
                logger.info("Uploading file: %s", full_path)
                awsclient.upload_file(full_path,
                                      ENV["S3_BUCKET"], f"input/{root[5:]}/{file}")
    return has_data


def load_all(df: DataFrame):
    """Load all data given to S3."""
    create_data_directory()
    if create_parquet(df):
        s3 = get_s3_client()
        load_to_s3(s3)
    delete_data_directory()


if __name__ == "__main__":
    load_dotenv()
    sample_dataframe = DataFrame({"plant_id": [1, 2, 3],
                                  "name": ["colin", "kevin", "sam"],
                                  "botanist": [1, 2, 1]})
    load_all(sample_dataframe)
