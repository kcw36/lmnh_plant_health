"""Handles long-term plant data processing using AWS Athena."""

from datetime import datetime, timedelta
from logging import getLogger, INFO, StreamHandler
from sys import stdout

import awswrangler as wr
from boto3 import Session
import pandas as pd
import streamlit as st


class LongTermDataProcessor:
    """Processes long-term plant monitoring data from S3 using Athena."""

    def __init__(self, config: dict[str]):
        """Initialise the long-term data processor."""
        self.config = config
        self.logger = getLogger(__name__)
        self.logger.setLevel(INFO)
        self.logger.addHandler(StreamHandler(stdout))
        self.session = self.get_boto3_session()

    @st.cache_resource
    def get_boto3_session(_self) -> Session:
        """Returns a live Boto3 session."""
        print("Connecting to AWS...")
        aws_session = Session(
            aws_access_key_id=_self.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=_self.config["AWS_SECRET_ACCESS_KEY"],
            region_name=_self.config["AWS_REGION_NAME"]
        )
        return aws_session

    @st.cache_data(ttl=300)
    def get_time_period_data(_self, time_period: str) -> pd.DataFrame:
        """Get aggregated plant data for the specified time period."""
        try:
            end_date = datetime.now()
            if time_period == "24h":
                start_date = end_date - timedelta(days=1)
            elif time_period == "1m":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=365)

            query = f"""
            SELECT 
                plant_name,
                botanist,
                CAST(year AS INTEGER) as year,
                CAST(month AS INTEGER) as month,
                CAST(day AS INTEGER) as day,
                temperature_median as avg_temperature,
                soil_moisture_median as avg_moisture,
                count as total_readings,
                temperature_min,
                temperature_max,
                soil_moisture_min,
                soil_moisture_max,
                plant_id
            FROM input
            WHERE DATE(CONCAT(year, '-', month, '-', day)) BETWEEN DATE('{start_date.strftime('%Y-%m-%d')}') 
                AND DATE('{end_date.strftime('%Y-%m-%d')}')
            ORDER BY year, month, day
            """

            data = wr.athena.read_sql_query(
                sql=query,
                database=_self.config['ATHENA_DB_NAME'],
                s3_output=_self.config['S3_OUTPUT'],
                boto3_session=_self.session
            )

            data['date'] = pd.to_datetime(
                data[['year', 'month', 'day']].assign(
                    hour=0, minute=0, second=0
                )
            )

            return data

        except Exception as e:
            _self.logger.error(f"Error fetching long-term data: {str(e)}")
            return pd.DataFrame()

    @st.cache_data(ttl=300)
    def get_plant_list(_self) -> list[str]:
        """Get list of all plants in the long-term dataset."""
        try:
            query = """
            SELECT DISTINCT plant_name
            FROM input
            ORDER BY plant_name
            """

            data = wr.athena.read_sql_query(
                sql=query,
                database=_self.config['ATHENA_DB_NAME'],
                s3_output=_self.config['S3_OUTPUT'],
                boto3_session=_self.session
            )

            if data.empty:
                _self.logger.warning("No plants found in the database")
                return []

            plant_list = data['plant_name'].tolist()
            _self.logger.info(
                f"Found {len(plant_list)} plants in the database")
            return plant_list

        except Exception as e:
            _self.logger.error(f"Error fetching plant list: {str(e)}")
            st.error(f"Error fetching plant list: {str(e)}")
            return []
