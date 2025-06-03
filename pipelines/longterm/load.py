"""Module for loading long term data to S3."""

from logging import getLogger

from pandas import DataFrame
from boto3 import client
from dotenv import load_dotenv


def get_s3_client() -> client:
    """Return client to s3 bucket."""
    logger = getLogger(__name__)
    logger.info("Return S3 client")


def load_to_s3(awsclient: client) -> bool:
    """Load objects to s3."""
    logger = getLogger(__name__)
    logger.info("Starting load to S3...")


def create_data_directory() -> bool:
    """Return true if data directory created successfully"""
    logger = getLogger(__name__)
    logger.info("Creating empty data directory for Parquet files...")


def delete_data_directory() -> bool:
    """Return true if deleted data directory"""
    logger = getLogger(__name__)
    logger.info("Deleting filled data directory...")


def create_parquet(data: DataFrame) -> bool:
    """Save data as parquet files."""
    logger = getLogger(__name__)
    logger.info("Storing local parquet files...")


if __name__ == "__main__":
    load_dotenv()
    sample_dataframe = DataFrame()
    delete_data_directory()
    create_data_directory()
    if create_parquet(sample_dataframe):
        s3 = get_s3_client()
        load_to_s3(s3)
