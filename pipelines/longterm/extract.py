"""Module for extracting from short term storage for use in historic storage."""

from logging import getLogger
from os import environ as ENV

from dotenv import load_dotenv
from pandas import DataFrame
from pyodbc import connect, Connection


def get_connection():
    """Return database connection."""
    logger = getLogger(__name__)
    logger.info("Getting RDS connection...")
    connection_string = f"""
                            DRIVER={{ODBC Driver 18 for SQL Server}};
                            SERVER={ENV["DB_HOST"]},{ENV["DB_PORT"]};
                            DATABASE={ENV["DB_NAME"]};
                            UID={ENV["DB_USER"]};
                            PWD={ENV["DB_PASSWORD"]};
                            TrustServerCertificate=yes;
                            Encrypt=yes;
                            Connection Timeout=30;
                         """
    return connect(connection_string)


def get_data_from_RDS(conn: Connection) -> DataFrame:
    """Return data as Dataframe from RDS connection."""
    logger = getLogger(__name__)
    logger.info("Getting data from RDS...")


if __name__ == "__main__":
    load_dotenv()
    sql_server_conn = get_connection()
