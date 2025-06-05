"""Calculates the statistics and data used in the dashboard and visualisations."""
from os import environ as ENV
from datetime import datetime, timedelta
from logging import getLogger, INFO, StreamHandler
from sys import stdout

from dotenv import load_dotenv
from pyodbc import connect, Connection
import pandas as pd
import numpy as np
import streamlit as st


class DatabaseManager:
    """Manages database connections and queries for the plant monitoring system."""

    def __init__(self, config: dict):
        """Initialise database manager with configuration."""
        self.config = config
        self.logger = getLogger(__name__)

    def set_logger():
        """Set logger."""
        logger = getLogger(__name__)
        logger.setLevel(INFO)
        logger.addHandler(StreamHandler(stdout))

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
        with self.get_connection() as conn:
            return pd.read_sql(query, conn, params=params)


class PlantDataProcessor:
    """Processes plant monitoring data and performs statistical calculations."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize data processor with database manager."""
        self.db_manager = db_manager

    @st.cache_data()
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

    @st.cache_data(ttl=60)
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
        JOIN plant p USING(plant_id)
        JOIN origin_city c USING(city_id)
        JOIN origin_country co USING(country_id)
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

    def identify_critical_plants(self) -> pd.DataFrame:
        """Identify plants with critical issues (extreme readings or stale data)."""
        latest_readings = self.get_latest_readings()
        current_time = datetime.now()
        critical_plants = []

        temp_median = latest_readings['temperature'].median()
        temp_std = latest_readings['temperature'].std()
        moisture_median = latest_readings['soil_moisture'].median()
        moisture_std = latest_readings['soil_moisture'].std()

        for _, plant in latest_readings.iterrows():
            issues = []

            temp_z_score = abs(plant['temperature'] - temp_median) / temp_std
            if temp_z_score > 3:
                issues.append(
                    f"Extreme temperature: {plant['temperature']:.1f}°C")

            moisture_z_score = abs(
                plant['soil_moisture'] - moisture_median) / moisture_std
            if moisture_z_score > 3:
                issues.append(
                    f"Extreme moisture: {plant['soil_moisture']:.1f}%")

            time_diff = current_time - plant['recording_taken']
            if time_diff > timedelta(hours=2):
                hours_old = time_diff.total_seconds() / 3600
                issues.append(f"Stale reading: {hours_old:.1f} hours old")

            if issues:
                critical_plants.append({
                    'plant_id': plant['plant_id'],
                    'plant_name': plant['plant_name'],
                    'issues': '; '.join(issues),
                    'last_reading': plant['recording_taken']
                })

        return pd.DataFrame(critical_plants)

    @st.cache_data(ttl=300)
    def get_plants_with_least_readings(_self, limit: int = 5) -> pd.DataFrame:
        """Get plants with the least number of readings."""
        query = """
        SELECT TOP (?) 
            p.plant_id,
            p.name as plant_name,
            COUNT(r.record_id) as reading_count
        FROM plant p
        LEFT JOIN record r ON p.plant_id = r.plant_id
        GROUP BY p.plant_id, p.name
        ORDER BY reading_count ASC
        """
        return _self.db_manager.execute_query(query, (limit,))

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

    def get_filtered_data(self, botanist_id: int = None,
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
            base_query += " JOIN botanist_plant bp USING(plant_id)"
            conditions.append("bp.botanist_id = ?")
            params.append(botanist_id)

        if plant_species:
            conditions.append("p.name = ?")
            params.append(plant_species)

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY p.name"

        return self.db_manager.execute_query(base_query, tuple(params) if params else None)


class StatisticsCalculator:
    """Handles statistical calculations and data aggregations."""

    @staticmethod
    def calculate_hourly_averages(data: pd.DataFrame,
                                  metric_column: str,
                                  time_column: str = 'recording_taken',
                                  group_column: str = 'plant_name') -> pd.DataFrame:
        """Calculate hourly averages for a specific metric grouped by plant species."""
        if data.empty:
            return pd.DataFrame()

        data = data.copy()

        data[time_column] = pd.to_datetime(data[time_column])
        data['hour'] = data[time_column].dt.floor('H')

        hourly_avg = data.groupby([group_column, 'hour'])[
            metric_column].mean().reset_index()
        return hourly_avg

    @staticmethod
    def detect_outliers(series: pd.Series, method: str = 'iqr') -> pd.Series:
        """Detect outliers in a pandas Series."""
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (series < lower_bound) | (series > upper_bound)

        elif method == 'zscore':
            z_scores = np.abs((series - series.mean()) / series.std())
            return z_scores > 3

        else:
            raise ValueError("Method must be 'iqr' or 'zscore'")
