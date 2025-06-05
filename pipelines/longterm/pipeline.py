"""Script for running the historic data pipeline."""

from sys import stdout
from logging import getLogger, StreamHandler, INFO

from dotenv import load_dotenv

from extract import get_data_from_rds
from transform import get_summary_from_df
from load import load_all


def set_logger():
    """Set logger."""
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(StreamHandler(stdout))


def run():
    """Run pipeline script."""
    logger = getLogger()
    logger.info("Attempting pipeline run...")

    data = get_data_from_rds()
    if data.empty:
        raise ValueError("Recieved no data from RDS.")
    logger.info("Successfully recieved data from RDS!")

    summary = get_summary_from_df(data)
    if summary.empty:
        raise ValueError("Found no summary data from returned raw data!")
    logger.info("Successfully summarised data from RDS!")

    load_all(summary)
    logger.info("Successfully loaded data into S3!")


def lambda_handler(event, context):
    """
    Main Lambda Handler Function.
    Parameters:
        event: Dict containing the lambda function event data
        context: LAMBDA RUNTIME CONTEXT
    Returns:
        Dict containing status message
    """
    set_logger()
    logger = getLogger()
    logger.info("Initiating Info level logger.")
    try:
        run()
        return {
            "statusCode": 200,
            "message": "Data uploaded successfully."
        }
    except Exception as e:
        logger.error("Error processing pipeline: %s", str(e))
        raise


if __name__ == "__main__":
    set_logger()
    load_dotenv()
    run()
