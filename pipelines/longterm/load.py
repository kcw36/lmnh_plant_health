"""Module for loading long term data to S3."""

from logging import getLogger
from os import environ as ENV, path, walk, mkdir
from shutil import rmtree

from pandas import DataFrame
from boto3 import client
from dotenv import load_dotenv
from pyarrow import Table, parquet as pq


def create_data_directory() -> bool:
    """Return true if data directory created successfully."""
    logger = getLogger()
    logger.info("Creating empty data directory for Parquet files...")
    dir_path = "/tmp/data"
    if not path.exists(dir_path):
        mkdir(dir_path)
        mkdir(f"{dir_path}/plant")
        return True
    return False


def delete_data_directory() -> bool:
    """Return true if deleted data directory."""
    logger = getLogger()
    logger.info("Deleting filled data directory...")
    dir_path = "/tmp/data"
    rmtree(dir_path)
    if not path.exists(dir_path):
        return False
    return True


def create_parquet(data: DataFrame) -> bool:
    """Save data as parquet files."""
    logger = getLogger()
    logger.info("Storing local parquet files...")
    datatable = Table.from_pandas(data)
    if not datatable:
        logger.error("No data given.")
        return False
    pq.write_to_dataset(datatable, root_path="/tmp/data/plant",
                        partition_cols=["year", "month", "day"],
                        basename_template="summary-{i}")
    logger.info("Parquet created successfully.")
    return True


def get_s3_client() -> client:
    """Return client to S3 bucket."""
    logger = getLogger()
    logger.info("Return S3 client")
    return client("s3",
                  aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])


def load_to_s3(awsclient: client) -> bool:
    """Load objects to S3."""
    logger = getLogger()
    logger.info("Starting load to S3...")
    has_data = False
    for root, _, files in walk("/tmp/data"):
        if files:
            has_data = True
            for file in files:
                full_path = path.join(root, file)
                logger.info("Uploading file: %s", full_path)
                awsclient.upload_file(full_path,
                                      ENV["S3_BUCKET"], f"input/{root[10:]}/{file}")
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
                                  "botanist": [1, 2, 1],
                                  "year": [2000, 2001, 2002],
                                  "month": [1, 2, 3],
                                  "day": [1, 2, 3]})
    load_all(sample_dataframe)
