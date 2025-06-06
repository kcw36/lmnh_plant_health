"""Module for extracting data from RDS."""
from logging import getLogger
from os import environ as ENV

from datetime import datetime

from dotenv import load_dotenv
import pandas as pd
from pandas import DataFrame, Series

import numpy as np
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


def detect_outliers(series: Series) -> Series:
    """Detect outliers in a pandas Series"""
    z_scores = np.abs((series - series.median()) / series.std())
    return z_scores > 3


def get_latest_readings(conn: Connection) -> DataFrame:
    """Get 3 latest readings for each plant."""
    query = """
        WITH LatestReadings AS (
        SELECT 
            r.plant_id,
            r.temperature,
            r.soil_moisture,
            r.recording_taken,
            ROW_NUMBER() OVER (PARTITION BY r.plant_id ORDER BY r.recording_taken DESC) as record
        FROM record r
    )
    SELECT 
        lr.plant_id,
        p.name as plant_name,
        lr.temperature,
        lr.soil_moisture,
        lr.recording_taken,
        b.botanist_id,
        b.name,
        b.phone
    FROM LatestReadings lr
    JOIN plant p ON lr.plant_id = p.plant_id
    JOIN botanist_plant bp ON lr.plant_id = bp.plant_id
    JOIN botanist b ON bp.botanist_id = b.botanist_id
    WHERE lr.record = 1 OR lr.record = 2 OR lr.record = 3
    """

    return pd.read_sql(query, conn)


def create_issue_message(row):
    """Create issues message if issues present."""
    issues = []
    if row['is_temp_issue']:
        issues.append(
            f"Extreme temperature: {row['temperature']:.1f}°C")
    if row['is_moisture_issue']:
        issues.append(f"Extreme moisture: {row['soil_moisture']:.1f}%")
    if row['is_stale']:
        issues.append(
            f"Stale reading: {row['time_diff_hr']:.1f} hours old")
    return "; ".join(issues)


def identify_critical_plants(conn: Connection) -> DataFrame:
    """Identify plants with critical issues using efficient vectorised operations."""
    latest_readings = get_latest_readings(conn)
    if latest_readings.empty:
        return DataFrame()

    temp_outliers = detect_outliers(
        latest_readings['temperature'])

    moisture_outliers = detect_outliers(
        latest_readings['soil_moisture'])

    current_time = datetime.now()
    time_diffs = (
        current_time - pd.to_datetime(
            latest_readings['recording_taken'])).dt.total_seconds() / 3600
    stale_data = time_diffs > 2

    issues_df = pd.DataFrame({
        'plant_id': latest_readings['plant_id'],
        'plant_name': latest_readings['plant_name'],
        'recording_taken': latest_readings['recording_taken'],
        'temperature': latest_readings['temperature'],
        'soil_moisture': latest_readings['soil_moisture'],
        'is_temp_issue': temp_outliers,
        'is_moisture_issue': moisture_outliers,
        'is_stale': stale_data,
        'time_diff_hr': time_diffs,
        'botanist_id': latest_readings['botanist_id'],
        'botanist_name': latest_readings['name'],
        'botanist_phone_number': latest_readings['phone']
    })

    issue_rows = issues_df[
        issues_df['is_temp_issue'] |
        issues_df['is_moisture_issue'] |
        issues_df['is_stale']
    ]

    if issue_rows.empty:
        return pd.DataFrame()

    issue_messages = issue_rows.apply(create_issue_message, axis=1)

    return pd.DataFrame({
        'plant_id': issue_rows['plant_id'].values,
        'plant_name': issue_rows['plant_name'].values,
        'issues': issue_messages.values,
        'last_reading': issue_rows['recording_taken'].values,
        'botanist_id': issue_rows['botanist_id'].values,
        'botanist_name': issue_rows['botanist_name'].values,
        'botanist_phone_number': issue_rows['botanist_phone_number'].values
    })
