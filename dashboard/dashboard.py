"""Hello World Module"""

from logging import getLogger


def hello_world():
    return "Hello World!"


def lambda_handler(event, context):
    """
    Main Lambda Handler Function.
    Parameters:
        event: Dict containing the lambda function event data
        context: LAMBDA RUNTIME CONTEXT
    Returns:
        Dict containing status message
    """
    logger = getLogger()
    logger.info("Initiating Info level logger.")
    try:
        logger.info(hello_world())
        return {
            "statusCode": 200,
            "message": "Hello."
        }
    except Exception as e:
        logger.error("Error processing hello world: %s", str(e))
        raise RuntimeError("Error with Python runtime.")
