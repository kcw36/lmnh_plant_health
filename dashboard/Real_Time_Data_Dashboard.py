"""Main streamlit dashboard for the plant monitoring system."""

from os import environ as ENV
from datetime import datetime
from logging import getLogger, INFO, StreamHandler
from sys import stdout

import streamlit as st
from dotenv import load_dotenv


from data import DatabaseFunctions, PlantDataProcessor, StatisticsCalculator
from visualisations import (
    MetricsDisplay, AlertsDisplay, TimeSeriesCharts, FilterComponents,
    DataTableDisplay, DashboardLayout
)


class PlantMonitoringDashboard:
    """Main dashboard application class."""

    def __init__(self):
        """Initialise the dashboard application."""
        config = {
            "DB_HOST": ENV["DB_HOST"],
            "DB_PORT": ENV["DB_PORT"],
            "DB_NAME": ENV["DB_NAME"],
            "DB_USER": ENV["DB_USER"],
            "DB_PASSWORD": ENV["DB_PASSWORD"]
        }
        self.db_functions = DatabaseFunctions(config)
        self.data_processor = PlantDataProcessor(self.db_functions)
        self.stats_calculator = StatisticsCalculator()
        self.filtering = FilterComponents()
        self.alerts = AlertsDisplay()
        self.metrics = MetricsDisplay()
        self.data_table = DataTableDisplay()
        self.dashboard = DashboardLayout()
        self.timeseries_charts = TimeSeriesCharts()
        self.logger = getLogger(__name__)
        self.logger.setLevel(INFO)
        self.logger.addHandler(StreamHandler(stdout))

    def _setup_filters(self) -> tuple[int, str]:
        """Setup and create filter components in the sidebar."""
        st.sidebar.header("🔍 Filters")

        try:
            botanist_data = self.data_processor.get_botanist_list()
            species_data = self.data_processor.get_plant_species_list()

            selected_botanist = self.filtering.create_botanist_filter(
                botanist_data)
            selected_species = self.filtering.create_species_filter(
                species_data)

            return selected_botanist, selected_species

        except Exception as e:
            st.sidebar.error(f"Error loading filter options: {str(e)}")
            return None, None

    @st.cache_data(ttl=300)
    def _get_filtered_plant_list(_self, botanist_id: int,
                                 plant_species: str) -> list[str]:
        """Get list of plant names based on current filters."""
        try:
            filtered_data = _self.data_processor.get_filtered_data(
                botanist_id, plant_species)

            if filtered_data.empty:
                raise ValueError("No plants found for the selected filters.")

            return filtered_data['plant_name'].tolist() if not filtered_data.empty else []

        except Exception as e:
            _self.logger.error(f"Error getting filtered plant list: {str(e)}")
            st.error(f"{str(e)}")
            return []

    def _get_key_stats_section(self, filtered_plants: list[str]) -> None:
        """Create the key performance indicators section."""
        try:
            total_plants = self.data_processor.get_total_plants()
            active_botanists = self.data_processor.get_active_botanists()

            latest_readings = self.data_processor.get_latest_readings()

            if filtered_plants:
                latest_readings = latest_readings[
                    latest_readings['plant_name'].isin(filtered_plants)
                ]

            if not latest_readings.empty:
                avg_metrics = {
                    'avg_temperature': latest_readings['temperature'].median(),
                    'avg_soil_moisture': latest_readings['soil_moisture'].median()
                }
            else:
                avg_metrics = {'avg_temperature': 0.0,
                               'avg_soil_moisture': 0.0}

            self.metrics.show_key_metrics(
                total_plants if not filtered_plants else len(
                    filtered_plants),
                active_botanists,
                avg_metrics['avg_temperature'],
                avg_metrics['avg_soil_moisture']
            )

        except Exception as e:
            st.error(f"Error loading key metrics: {str(e)}")
            self.logger.error(f"Key metrics section error: {str(e)}")

    def _create_alerts_section(self) -> None:
        """Create the alerts and critical issues section."""
        try:
            critical_plants = self.data_processor.identify_critical_plants()
            self.alerts.show_critical_plants(critical_plants)

            low_reading_plants = self.data_processor.get_plants_with_least_readings()
            self.alerts.show_low_reading_plants(low_reading_plants)

        except Exception as e:
            st.error(f"Error loading alerts: {str(e)}")
            self.logger.error(f"Alerts section error: {str(e)}")

    def _create_trends_section(self, filtered_plants: list[str]) -> None:
        """Create the time series trends section."""
        st.header("📈 Trends Analysis")

        try:
            readings_24h = self.data_processor.get_24h_readings()

            if readings_24h.empty:
                st.info("No readings available for the last 24 hours.")
                return

            temp_hourly = self.stats_calculator.calculate_hourly_averages(
                readings_24h, 'temperature'
            )
            moisture_hourly = self.stats_calculator.calculate_hourly_averages(
                readings_24h, 'soil_moisture'
            )

            temp_plot = self.timeseries_charts.create_trend_chart(
                temp_hourly, 'temperature', filtered_plants
            )
            st.altair_chart(temp_plot, use_container_width=True)

            moisture_plot = self.timeseries_charts.create_trend_chart(
                moisture_hourly, 'moisture', filtered_plants
            )
            st.altair_chart(moisture_plot, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading trends: {str(e)}")
            self.logger.error(f"Trends section error: {str(e)}")

    def _create_data_table_section(self, filtered_plants: list[str]) -> None:
        """Create the detailed data table section."""
        with st.expander("📊 Latest Readings Details"):
            try:
                latest_readings = self.data_processor.get_latest_readings()
                self.data_table.show_latest_readings_table(
                    latest_readings, filtered_plants
                )
            except Exception as e:
                st.error(f"Error loading data table: {str(e)}")
                self.logger.error(f"Data table section error: {str(e)}")

    def _create_sidebar_info(self) -> None:
        """Create additional information in the sidebar."""
        st.sidebar.markdown("---")
        st.sidebar.header("ℹ️ Dashboard Info")

        st.sidebar.info(
            "This dashboard provides real-time monitoring of plant health "
            "including temperature, soil moisture, and critical alerts."
        )

        st.sidebar.markdown("### 🚨 Critical Thresholds")
        st.sidebar.markdown(
            "- **Extreme readings**: >3 standard deviations from median\n"
            "- **Stale data**: No readings for >2 hours"
        )

        st.sidebar.markdown("### 🔄 Auto-refresh")
        if st.sidebar.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown("*Dashboard last updated:*")
        st.sidebar.markdown(
            f"*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    def run(self) -> None:
        """Main method to run the dashboard application."""
        try:
            self.dashboard.setup_page_config()
            self.dashboard.create_header()

            selected_botanist, selected_species = self._setup_filters()

            filtered_plants = self._get_filtered_plant_list(
                selected_botanist, selected_species
            )

            if selected_botanist or selected_species:
                filter_info = []
                if selected_botanist:
                    botanist_data = self.data_processor.get_botanist_list()
                    botanist_name = botanist_data[
                        botanist_data['botanist_id'] == selected_botanist
                    ]['name'].values[0]
                    filter_info.append(f"Botanist: {botanist_name}")
                if selected_species:
                    filter_info.append(
                        f"Species: {', '.join(selected_species)}")

                st.info(f"🔍 **Active Filters:** {' | '.join(filter_info)}")

            self._get_key_stats_section(filtered_plants)

            st.markdown("---")

            col1, col2 = st.columns([1, 2])

            with col1:
                self._create_alerts_section()

            with col2:
                self._create_trends_section(filtered_plants)

            st.markdown("---")

            self._create_data_table_section(filtered_plants)

            self._create_sidebar_info()

        except Exception as e:
            st.error("An unexpected error occurred while loading the dashboard.")
            st.error(f"Error details: {str(e)}")
            self.logger.error(f"Dashboard error: {str(e)}")

            st.markdown("### Troubleshooting")
            st.markdown("1. Check your database connection settings")
            st.markdown("2. Verify that your database is accessible")
            st.markdown("3. Try refreshing the page")

            if st.button("🔄 Retry"):
                st.cache_data.clear()
                st.rerun()


if __name__ == "__main__":
    load_dotenv()
    dashboard = PlantMonitoringDashboard()
    dashboard.run()
