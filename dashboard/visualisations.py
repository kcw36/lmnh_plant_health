"""Visualisation components for the plant monitoring dashboard."""

import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime


class MetricsDisplay:
    """Handles display of key performance metrics."""

    @staticmethod
    def show_key_metrics(total_plants: int, active_botanists: int,
                         avg_temperature: float, avg_moisture: float) -> None:
        """Display key performance indicators in a formatted layout."""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="🌱 Total Plants",
                value=f"{total_plants:,}",
                help="Total number of plants in the monitoring system"
            )

        with col2:
            st.metric(
                label="👨‍🔬 Active Botanists",
                value=f"{active_botanists:,}",
                help="Number of botanists with assigned plants"
            )

        with col3:
            st.metric(
                label="🌡️ Avg Temperature",
                value=f"{avg_temperature:.1f}°C",
                help="Average temperature across latest plant readings"
            )

        with col4:
            st.metric(
                label="💧 Avg Soil Moisture",
                value=f"{avg_moisture:.1f}%",
                help="Average soil moisture across latest plant readings"
            )


class AlertsDisplay:
    """Handles display of alerts and critical information."""

    @staticmethod
    def show_critical_plants(critical_plants_df: pd.DataFrame) -> None:
        """Display plants with critical issues in an expandable section."""
        if critical_plants_df.empty:
            st.success("✅ No critical plant issues detected!")
            return

        with st.expander(f"🚨 Critical Plants ({len(critical_plants_df)} issues)", expanded=True):
            def display_row(row):
                st.error(f"**{row['plant_name']}** (ID: {row['plant_id']})")
                st.write(f"Issues: {row['issues']}")
                st.write(f"Last reading: {row['last_reading']}")
                st.divider()
            critical_plants_df.apply(display_row, axis=1)

    @staticmethod
    def show_low_reading_plants(low_reading_plants_df: pd.DataFrame) -> None:
        """Display plants with the least number of readings."""
        st.subheader("📊 Plants with Least Readings")

        if low_reading_plants_df.empty:
            st.info("No data available for plant reading counts.")
            return

        chart = alt.Chart(low_reading_plants_df).mark_bar().encode(
            x=alt.X('reading_count:Q', title='Number of Readings'),
            y=alt.Y('plant_name:N', title='Plant Species', sort='x'),
            color=alt.Color('reading_count:Q', scale=alt.Scale(
                scheme='reds'), legend=None),
            tooltip=['plant_name', 'reading_count']
        ).properties(
            title='Top 5 Plants with Least Readings',
            height=400
        )

        st.altair_chart(chart, use_container_width=True)


class TimeSeriesCharts:
    """Handles time series visualisation for plant monitoring data."""

    @staticmethod
    def create_temperature_trend(hourly_data: pd.DataFrame,
                                 filtered_plants: list[str] = None) -> alt.Chart:
        """Create a line chart showing temperature trends over the last 24 hours."""

        if hourly_data.empty:
            return alt.Chart(pd.DataFrame({'text': ['No temperature data available']})).mark_text(
                align='center', baseline='middle', fontSize=16
            ).encode(text='text')

        if filtered_plants:
            hourly_data = hourly_data[hourly_data['plant_name'].isin(
                filtered_plants)]

        hourly_data['hour_formatted'] = hourly_data['hour'].dt.strftime(
            '%H:%M')
        hourly_data['temperature_formatted'] = hourly_data['temperature'].round(
            1).astype(str) + '°C'

        return alt.Chart(hourly_data).mark_line(point=True).encode(
            x=alt.X('hour:T', title='Time'),
            y=alt.Y('temperature:Q', title='Temperature (°C)'),
            color=alt.Color('plant_name:N', legend=None),
            tooltip=['plant_name', 'hour_formatted', 'temperature_formatted']
        ).properties(
            title='Average Temperature Trends (Last 24 Hours)',
            height=400
        ).interactive()

    @staticmethod
    def create_moisture_trend(hourly_data: pd.DataFrame,
                              filtered_plants: list[str] = None) -> alt.Chart:
        """Create a line chart showing soil moisture trends over the last 24 hours."""
        if hourly_data.empty:
            return alt.Chart(pd.DataFrame({'text': ['No moisture data available']})).mark_text(
                align='center', baseline='middle', fontSize=16
            ).encode(text='text')

        if filtered_plants:
            hourly_data = hourly_data[hourly_data['plant_name'].isin(
                filtered_plants)]

        hourly_data['hour_formatted'] = hourly_data['hour'].dt.strftime(
            '%H:%M')
        hourly_data['moisture_formatted'] = hourly_data['soil_moisture'].round(
            1).astype(str) + '%'

        return alt.Chart(hourly_data).mark_line(point=True).encode(
            x=alt.X('hour:T', title='Time'),
            y=alt.Y('soil_moisture:Q', title='Soil Moisture (%)'),
            color=alt.Color('plant_name:N', legend=None),
            tooltip=['plant_name', 'hour_formatted', 'moisture_formatted']
        ).properties(
            title='Average Soil Moisture Trends (Last 24 Hours)',
            height=400
        ).interactive()


class FilterComponents:
    """Handles filtering components for the dashboard."""

    @staticmethod
    def create_botanist_filter(botanist_df: pd.DataFrame) -> int:
        """Create a select box for botanist filtering."""
        botanist_options = ["All Botanists"] + botanist_df['name'].tolist()
        selected_botanist = st.sidebar.selectbox(
            "👨‍🔬 Filter by Botanist:",
            options=botanist_options,
            help="Filter data by botanist assignments"
        )

        if selected_botanist != "All Botanists":
            return int(botanist_df[botanist_df['name'] == selected_botanist]['botanist_id'].iloc[0])

    @staticmethod
    def create_species_filter(species_df: pd.DataFrame) -> str:
        """Create a select box for plant species filtering."""

        species_options = ["All Species"] + species_df['name'].tolist()
        selected_species = st.sidebar.selectbox(
            "🌱 Filter by Plant Species:",
            options=species_options,
            help="Filter data by plant species"
        )

        if selected_species != "All Species":
            return selected_species


class DataTableDisplay:
    """Handles table data display components."""

    @staticmethod
    def show_latest_readings_table(latest_readings_df: pd.DataFrame,
                                   filtered_plants: list[str] = None) -> None:
        """Display latest readings in a formatted table."""

        if latest_readings_df.empty:
            st.info("No recent readings available.")
            return None

        if filtered_plants:
            display_df = latest_readings_df[
                latest_readings_df['plant_name'].isin(filtered_plants)
            ]
        else:
            display_df = latest_readings_df

        if display_df.empty:
            st.info("No data matches the current filters.")
            return None

        display_df = display_df.copy()
        display_df['recording_taken'] = pd.to_datetime(
            display_df['recording_taken']).dt.strftime('%Y-%m-%d %H:%M')

        st.dataframe(
            display_df,
            column_config={
                "plant_id": "Plant ID",
                "plant_name": "Species",
                "temperature": st.column_config.NumberColumn(
                    "Temperature (°C)",
                    format="%.1f"
                ),
                "soil_moisture": st.column_config.NumberColumn(
                    "Soil Moisture (%)",
                    format="%.1f"
                ),
                "recording_taken": "Last Reading",
                "city_name": "City",
                "country_name": "Country"
            },
            hide_index=True,
            use_container_width=True
        )


class DashboardLayout:
    """Manages overall dashboard layout and styling."""

    @staticmethod
    def setup_page_config() -> None:
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Plant Monitoring Dashboard",
            page_icon="🌱",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    @staticmethod
    def create_header() -> None:
        """Create the dashboard header."""
        st.title("🌱 Plant Monitoring Dashboard")
        st.markdown("---")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                "**Real-time monitoring of plant health and environmental conditions**")
        with col2:
            st.markdown(
                f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
