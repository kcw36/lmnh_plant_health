"""Long-term plant data analysis dashboard page."""

from os import environ as ENV
from datetime import datetime

import streamlit as st
import altair as alt
import pandas as pd

from historic_data import LongTermDataProcessor
from visualisations import DashboardLayout, TimeSeriesCharts


def configure_page() -> None:
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title="Historic Plant Data Analysis",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )


class LongTermAnalysisDashboard:
    """Dashboard for analysing long-term plant data."""

    def __init__(self):
        """Initialise the long-term analysis dashboard."""
        config = {
            "AWS_ACCESS_KEY_ID": ENV["AWS_ACCESS_KEY_ID"],
            "AWS_SECRET_ACCESS_KEY": ENV["AWS_SECRET_ACCESS_KEY"],
            "AWS_REGION_NAME": ENV["AWS_REGION_NAME"],
            "ATHENA_DB_NAME": ENV["ATHENA_DB_NAME"],
            "S3_OUTPUT": ENV["S3_OUTPUT"]
        }
        self.data_processor = LongTermDataProcessor(config)
        self.dashboard = DashboardLayout()
        self.timeseries_charts = TimeSeriesCharts()

    def _setup_filters(self) -> tuple[str, list[str]]:
        """Setup and create filter components in the sidebar."""
        st.sidebar.header("🔍 Filters")

        try:
            time_period = st.sidebar.selectbox(
                "⏰ Time Period:",
                options=["24h", "1m", "1y"],
                format_func=lambda x: {
                    "24h": "Last 24 Hours",
                    "1m": "Last Month",
                    "1y": "Last Year"
                }[x],
                help="Select the time period for analysis"
            )

            plants = self.data_processor.get_plant_list()

            if not plants:
                st.sidebar.error(
                    "No plants found in the database. Please check your AWS connection and database configuration.")
                return time_period, []

            selected_plants = st.sidebar.multiselect(
                "🌱 Select Plants:",
                options=plants,
                help="Select plants to analyse"
            )

            return time_period, selected_plants

        except Exception as e:
            st.sidebar.error(f"Error loading filter options: {str(e)}")
            return "24h", []

    def _create_temperature_chart(self, data: pd.DataFrame, selected_plants: list[str]) -> None:
        """Create temperature trend chart with min/max ranges."""
        st.subheader("🌡️ Temperature Trends")

        if data.empty:
            st.info("No temperature data available for the selected period.")
            return

        if selected_plants:
            data = data[data['plant_name'].isin(selected_plants)]

        base = alt.Chart(data).encode(
            x=alt.X('date:T', title='Date'),
            color=alt.Color('plant_name:N', title='Plant')
        )

        line = base.mark_line(point=True).encode(
            y=alt.Y('avg_temperature:Q', title='Temperature (°C)'),
            tooltip=[
                'plant_name',
                'date',
                alt.Tooltip('avg_temperature:Q',
                            title='Median Temperature', format='.1f'),
                alt.Tooltip('temperature_min:Q',
                            title='Min Temperature', format='.1f'),
                alt.Tooltip('temperature_max:Q',
                            title='Max Temperature', format='.1f')
            ]
        )

        area = base.mark_area(opacity=0.3).encode(
            y=alt.Y('temperature_min:Q', title='Temperature (°C)'),
            y2='temperature_max:Q',
            tooltip=[
                'plant_name',
                'date',
                alt.Tooltip('temperature_min:Q',
                            title='Min Temperature', format='.1f'),
                alt.Tooltip('temperature_max:Q',
                            title='Max Temperature', format='.1f')
            ]
        )

        chart = (area + line).properties(
            title='Temperature Trends with Min/Max Ranges',
            height=400
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

    def _create_moisture_chart(self, data: pd.DataFrame, selected_plants: list[str]) -> None:
        """Create moisture trend chart with min/max ranges."""
        st.subheader("💧 Moisture Trends")

        if data.empty:
            st.info("No moisture data available for the selected period.")
            return

        if selected_plants:
            data = data[data['plant_name'].isin(selected_plants)]

        base = alt.Chart(data).encode(
            x=alt.X('date:T', title='Date'),
            color=alt.Color('plant_name:N', title='Plant')
        )

        line = base.mark_line(point=True).encode(
            y=alt.Y('avg_moisture:Q', title='Moisture (%)'),
            tooltip=[
                'plant_name',
                'date',
                alt.Tooltip('avg_moisture:Q',
                            title='Median Moisture', format='.1f'),
                alt.Tooltip('soil_moisture_min:Q',
                            title='Min Moisture', format='.1f'),
                alt.Tooltip('soil_moisture_max:Q',
                            title='Max Moisture', format='.1f')
            ]
        )

        area = base.mark_area(opacity=0.3).encode(
            y=alt.Y('soil_moisture_min:Q', title='Moisture (%)'),
            y2='soil_moisture_max:Q',
            tooltip=[
                'plant_name',
                'date',
                alt.Tooltip('soil_moisture_min:Q',
                            title='Min Moisture', format='.1f'),
                alt.Tooltip('soil_moisture_max:Q',
                            title='Max Moisture', format='.1f')
            ]
        )

        chart = (area + line).properties(
            title='Moisture Trends with Min/Max Ranges',
            height=400
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

    def _create_sidebar_info(self) -> None:
        """Create additional information in the sidebar."""
        st.sidebar.markdown("---")
        st.sidebar.header("ℹ️ Dashboard Info")

        st.sidebar.info(
            "This dashboard provides long-term analysis of plant health "
            "including temperature and soil moisture trends over time."
        )

        st.sidebar.markdown("### 📊 Data Source")
        st.sidebar.markdown(
            "Data is sourced from AWS Athena, showing daily aggregated "
            "metrics including min, median, and max values."
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
            self.dashboard.create_header()

            time_period, selected_plants = self._setup_filters()

            if not selected_plants:
                st.warning("Please select at least one plant to analyse.")
                return

            data = self.data_processor.get_time_period_data(time_period)

            if data.empty:
                st.error("No data available for the selected time period.")
                return

            self._create_temperature_chart(data, selected_plants)
            st.markdown("---")
            self._create_moisture_chart(data, selected_plants)

            self._create_sidebar_info()

        except Exception as e:
            st.error("An unexpected error occurred while loading the dashboard.")
            st.error(f"Error details: {str(e)}")

            st.markdown("### Troubleshooting")
            st.markdown("1. Check your AWS credentials and permissions")
            st.markdown("2. Verify that the Athena database and table exist")
            st.markdown("3. Try refreshing the page")

            if st.button("🔄 Retry"):
                st.cache_data.clear()
                st.rerun()


if __name__ == "__main__":
    configure_page()
    dashboard = LongTermAnalysisDashboard()
    dashboard.run()
