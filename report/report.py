"""Report script that notifies botanist if there is something wrong with a plant."""
from os import environ as ENV
from sys import stdout
from logging import getLogger, INFO, StreamHandler

from dotenv import load_dotenv

import boto3
from pandas import DataFrame
from data import get_connection, identify_critical_plants

logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler(stdout))


def turn_to_report(data: DataFrame) -> str:
    """Turn report DataFrame to a string."""
    if data.empty:
        logger.info("No critical issues detected.")
        return ""

    report = ["Plant Issue Report"]

    for _, row in data.iterrows():
        report.append(
            f"{row['plant_name']} (ID: {row['plant_id']})\n"
            f"Issue: {row['issues']}\n"
            f"Last Reading: {row['last_reading']}\n"
            f"Botanist: {row['botanist_name']} (ID: {row['botanist_id']})\n"
            f"Phone: {row['botanist_phone_number']}\n"
        )

    logger.info("Created report to be sent to the topic.")
    return "\n".join(report)


def report_to_topic(sns_client, report: str):
    """Send the report to SNS Topic."""
    if not report:
        logger.info("No report to send. Skipping SNS publish.")
        return

    try:
        response = sns_client.publish(
            TopicArn=ENV["TOPIC_ARN"],
            Message=report,
            Subject="Plant Issue Report"
        )
        logger.info("Message sent. ID: %s", response['MessageId'])
    except Exception as e:
        logger.error("Failed to send message: %s", e)


def run():
    """Run the Report script."""
    sns_client = boto3.client(
        "sns", aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"],
        aws_session_token=ENV["AWS_SESSION_TOKEN"],
        region_name=ENV["TOPIC_REGION"])
    logger.info("Connected to SNS Topic.")

    with get_connection() as conn:
        critical_plants = identify_critical_plants(conn)

    report = turn_to_report(critical_plants)
    report_to_topic(sns_client, report)
    return report


def lambda_handler(event=None, context=None):
    """AWS Lambda handler that sends out plant report using SNS."""
    try:
        report = run()
        return {
            "statusCode": 200,
            "message": report
        }
    except Exception as e:
        logger.error("Error processing pipeline: %s", str(e))
        raise RuntimeError("Error with Python runtime.")


if __name__ == "__main__":
    load_dotenv()
    plants_report = run()
    print(plants_report)
