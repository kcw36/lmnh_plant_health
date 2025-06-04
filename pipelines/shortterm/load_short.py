"""Modules for loading data to SQL Server DB."""

from logging import getLogger
from os import environ as ENV

import pandas as pd
from pandas import DataFrame

from dotenv import load_dotenv
from pyodbc import connect, Connection


def get_connection() -> Connection:
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


def insert_origin_country(data: DataFrame):
    """Insert data into `origin_country` table."""
    pass


def insert_botanist(data: DataFrame):
    """Insert data into `botanist` table."""
    pass


def insert_botanist_plant(data: DataFrame):
    """Insert data into `botanist` table."""
    pass


def insert_origin_city(data: DataFrame):
    """Insert data into `origin_city` table."""
    pass


def insert_plant(data: DataFrame):
    """Insert data into `botanist` table."""
    pass


def insert_record(data: DataFrame):
    """Insert data into `botanist` table."""
    pass


if __name__ == "__main__":
    load_dotenv()

    data = [
        {
            'plant_id': 1,
            'name': 'Venus flytrap',
            'origin_city': 'Stammside',
            'origin_country': 'Albania',
            'temperature': 13.77,
            'last_watered': '2025-06-04 13:51:41+00:00',
            'soil_moisture': 92.33,
            'recording_taken': '2025-06-04 16:10:03.580000+00:00',
            'botanist_name': 'Kenneth Buckridge',
            'botanist_email': 'kenneth.buckridge@lnhm.co.uk',
            'botanist_phone': '+7639148635'
        },
        {
            'plant_id': 2,
            'name': 'Sundew',
            'origin_city': 'Willowtown',
            'origin_country': 'Canada',
            'temperature': 18.21,
            'last_watered': '2025-06-03 09:14:12+00:00',
            'soil_moisture': 88.9,
            'recording_taken': '2025-06-03 09:15:00.000000+00:00',
            'botanist_name': 'Dr. Alice Greene',
            'botanist_email': 'alice.greene@lnhm.co.uk',
            'botanist_phone': '+1445982713'
        },
        {
            'plant_id': 3,
            'name': 'Pitcher plant',
            'origin_city': 'Rainford',
            'origin_country': 'Malaysia',
            'temperature': 27.45,
            'last_watered': '2025-06-01 18:20:05+00:00',
            'soil_moisture': 73.5,
            'recording_taken': '2025-06-01 18:25:10.100000+00:00',
            'botanist_name': 'Carlos Rivera',
            'botanist_email': 'carlos.rivera@lnhm.co.uk',
            'botanist_phone': '+6038291010'
        }
    ]

    df = pd.DataFrame(data)

    print(df)
    # with get_connection() as conn:
    #     print("Connected")
