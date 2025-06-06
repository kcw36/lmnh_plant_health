"""Module for extracting data from RDS."""


from logging import getLogger
from os import environ as ENV

from dotenv import load_dotenv
from pandas import DataFrame
from pyodbc import connect, Connection


def get_connection():
    """Return database connection."""
    logger = getLogger()
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


def extract_relevant_data(conn: Connection):
    pass
