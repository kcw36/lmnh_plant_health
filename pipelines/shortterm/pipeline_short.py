"""Script to run the full short term pipeline."""
from sys import stdout
from logging import getLogger, StreamHandler, INFO

from dotenv import load_dotenv
import pandas as pd

from transform_short import transform_data
from load_short import get_connection, load_data


def set_logger():
    """Set logger."""
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(StreamHandler(stdout))


def run_pipeline():
    """Runs the pipeline."""

    logger = getLogger()
    logger.info("Starting short term ETL pipeline...")

    clean_df = transform_data()

    if clean_df.empty:
        raise ValueError("No cleaned DataFrame received.")
    logger.info("Successfully retrieved and cleaned data from API!")

    with get_connection() as conn:
        load_data(clean_df, conn)
    logger.info("Successfully loaded data into RDS!")


def lambda_handler(event, context):
    """AWS handler for short-term ETL."""

    set_logger()
    logger = getLogger()
    logger.info("Initiating short-term ETL with Lambda...")

    try:
        run_pipeline()
        return {
            "statusCode": 200,
            "message": "Short-term ETL pipeline completed."
        }
    except Exception as e:
        logger.error("Short-term ETL pipeline failed: %s", str(e))
        raise RuntimeError("Error with Python runtime.")


if __name__ == "__main__":
    set_logger()
    load_dotenv()
    run_pipeline()
