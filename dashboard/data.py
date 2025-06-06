# pylint: disable=no-self-argument
"""Calculates the statistics and data used in the dashboard and visualisations."""
from os import environ as ENV
from datetime import datetime
from logging import getLogger, INFO, StreamHandler
from sys import stdout
from warnings import filterwarnings

from pyodbc import connect, Connection
import pandas as pd
import numpy as np
import streamlit as st


class DatabaseFunctions:
    """Manages database connections and queries for the plant monitoring system."""

    def __init__(self, config: dict):
        """Initialise database manager with configuration."""
        self.config = config
        self.logger = getLogger(__name__)
        self.logger.setLevel(INFO)
        self.logger.addHandler(StreamHandler(stdout))

    def get_connection(self) -> Connection:
        """Return a database connection."""
        self.logger.info("Getting RDS connection...")
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

    def execute_query(self, query: str, params: tuple[str] = None) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame."""
        filterwarnings(
            'ignore', message='pandas only supports SQLAlchemy connectable')
        with self.get_connection() as conn:
            return pd.read_sql(query, conn, params=params)


class PlantDataProcessor:
    """Processes plant monitoring data and performs statistical calculations."""

    def __init__(self, db_manager: DatabaseFunctions):
        """Initialise data processor with database manager."""
        self.db_manager = db_manager

    @st.cache_data
    def get_total_plants(_self) -> int:
        """Get total number of plants in the system."""

        query = "SELECT COUNT(*) as total_plants FROM plant"
        result = _self.db_manager.execute_query(query)
        return int(result.iloc[0]['total_plants'])

    @st.cache_data()
    def get_active_botanists(_self) -> int:
        """Get number of active botanists."""

        query = """
        SELECT COUNT(DISTINCT botanist_id) as active_botanists 
        FROM botanist_plant
        """
        result = _self.db_manager.execute_query(query)
        return int(result.iloc[0]['active_botanists'])

    @st.cache_data(ttl=300)
    def get_latest_readings(_self) -> pd.DataFrame:
        """Get the latest readings for each plant."""

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
            c.name as city_name,
            co.name as country_name
        FROM LatestReadings lr
        JOIN plant p ON lr.plant_id = p.plant_id
        JOIN origin_city c ON p.city_id = c.city_id
        JOIN origin_country co ON c.country_id = co.country_id
        WHERE lr.record = 1
        """
        return _self.db_manager.execute_query(query)

    def get_average_metrics(self) -> dict[float]:
        """Calculate average temperature and soil moisture from latest readings."""
        latest_readings = self.get_latest_readings()

        return {
            'avg_temperature': float(latest_readings['temperature'].median()),
            'avg_soil_moisture': float(latest_readings['soil_moisture'].median())
        }

    @st.cache_data(ttl=60)
    def identify_critical_plants(_self) -> pd.DataFrame:
        """Identify plants with critical issues using efficient vectorised operations."""
        latest_readings = _self.get_latest_readings()
        if latest_readings.empty:
            return pd.DataFrame()

        temp_outliers = StatisticsCalculator.detect_outliers(
            latest_readings['temperature'])
        moisture_outliers = StatisticsCalculator.detect_outliers(
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
            'time_diff_hr': time_diffs
        })

        issue_rows = issues_df[
            issues_df['is_temp_issue'] |
            issues_df['is_moisture_issue'] |
            issues_df['is_stale']
        ]

        if issue_rows.empty:
            return pd.DataFrame()

        def create_issue_message(row):
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

        issue_messages = issue_rows.apply(create_issue_message, axis=1)

        return pd.DataFrame({
            'plant_id': issue_rows['plant_id'].values,
            'plant_name': issue_rows['plant_name'].values,
            'issues': issue_messages.values,
            'last_reading': issue_rows['recording_taken'].values
        })

    @st.cache_data(ttl=300)
    def get_plants_with_least_readings(_self) -> pd.DataFrame:
        """Get plants with the least number of readings."""
        query = """
        SELECT TOP 5
            p.plant_id,
            p.name as plant_name,
            COUNT(r.record_id) as reading_count
        FROM plant p
        LEFT JOIN record r ON p.plant_id = r.plant_id
        GROUP BY p.plant_id, p.name
        ORDER BY reading_count
        """
        return _self.db_manager.execute_query(query)

    @st.cache_data(ttl=60)
    def get_24h_readings(_self) -> pd.DataFrame:
        """Get all readings from the last 24 hours with plant information."""

        query = """
        SELECT 
            r.temperature,
            r.soil_moisture,
            r.recording_taken,
            p.name as plant_name,
            r.plant_id
        FROM record r
        JOIN plant p ON r.plant_id = p.plant_id
        WHERE r.recording_taken >= DATEADD(hour, -24, GETDATE())
        ORDER BY r.recording_taken
        """
        return _self.db_manager.execute_query(query)

    @st.cache_data(ttl=300)
    def get_botanist_list(_self) -> pd.DataFrame:
        """ Get list of all botanists."""
        query = "SELECT botanist_id, name FROM botanist ORDER BY name"
        return _self.db_manager.execute_query(query)

    @st.cache_data(ttl=300)
    def get_plant_species_list(_self) -> pd.DataFrame:
        """Get list of all plant species (unique plant names)."""

        query = "SELECT DISTINCT name FROM plant ORDER BY name"
        return _self.db_manager.execute_query(query)

    @st.cache_data(ttl=300)
    def get_filtered_data(_self, botanist_id: int = None,
                          plant_species: str = None) -> pd.DataFrame:
        """Get filtered plant data based on botanist and/or plant species."""

        base_query = """
        SELECT DISTINCT
            p.plant_id,
            p.name as plant_name
        FROM plant p
        """

        conditions = []
        params = []

        if botanist_id:
            base_query += " JOIN botanist_plant bp ON p.plant_id = bp.plant_id"
            conditions.append("bp.botanist_id = ?")
            params.append(botanist_id)

        if plant_species:
            conditions.append("p.name = ?")
            params.append(plant_species)

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY p.name"

        return _self.db_manager.execute_query(base_query, tuple(params) if params else None)


class StatisticsCalculator:
    """Handles statistical calculations and data aggregations."""

    @staticmethod
    @st.cache_data(ttl=60)
    def calculate_hourly_averages(data: pd.DataFrame,
                                  metric_column: str,
                                  time_column: str = 'recording_taken',
                                  group_column: str = 'plant_name') -> pd.DataFrame:
        """Calculate hourly averages for a specific metric grouped by plant species."""
        if data.empty:
            return pd.DataFrame()

        data = data.copy()

        data[time_column] = pd.to_datetime(data[time_column])
        data['hour'] = data[time_column].dt.floor('h')

        return data.groupby([group_column, 'hour'])[metric_column].mean().reset_index()

    @staticmethod
    def detect_outliers(series: pd.Series) -> pd.Series:
        """Detect outliers in a pandas Series."""
        z_scores = np.abs((series - series.median()) / series.std())
        return z_scores > 3
