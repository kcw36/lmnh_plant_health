"""Visualisation components for the plant monitoring dashboard."""

from datetime import datetime

import pandas as pd
import streamlit as st
import altair as alt


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
    def show_critical_plants(critical_plants_data: pd.DataFrame) -> None:
        """Display plants with critical issues in an expandable section."""
        if critical_plants_data.empty:
            st.success("✅ No critical plant issues detected!")
            return

        with st.expander(f"🚨 Critical Plants ({len(critical_plants_data)} issues)", expanded=True):
            def display_row(row):
                st.error(f"**{row['plant_name']}** (ID: {row['plant_id']})")
                st.write(f"Issues: {row['issues']}")
                st.write(
                    f"Last reading: {pd.to_datetime(
                        row['last_reading']).strftime('%Y-%m-%d %H:%M:%S')}")
                st.divider()
            critical_plants_data.apply(display_row, axis=1)

    @staticmethod
    def show_low_reading_plants(low_reading_plants_data: pd.DataFrame) -> None:
        """Display plants with the least number of readings."""
        st.subheader("📊 Plants with Least Readings")

        if low_reading_plants_data.empty:
            st.info("No data available for plant reading counts.")
            return

        chart = alt.Chart(low_reading_plants_data).mark_bar().encode(
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
    def create_trend_chart(hourly_data: pd.DataFrame, metric: str,
                           filtered_plants: list = None) -> alt.Chart:
        """Create a line chart for temperature or moisture trends."""
        if hourly_data.empty:
            return alt.Chart(pd.DataFrame({'text': [f'No {metric} data available']})).mark_text(
                align='center', baseline='middle', fontSize=16
            ).encode(text='text')

        if not filtered_plants:
            st.warning('Please select filters to view data')
            return alt.Chart(pd.DataFrame()).mark_point().encode(
                x=alt.X('hour:T', title='Time'),
                y=alt.Y('temperature:Q', title='Temperature (°C)' if metric ==
                        'temperature' else 'Soil Moisture (%)')
            ).properties(
                title='Average Temperature Trends (Last 24 Hours)' if metric == 'temperature'
                else 'Average Soil Moisture Trends (Last 24 Hours)',
                height=400
            )

        data = hourly_data.copy()
        if filtered_plants:
            data = data[data['plant_name'].isin(filtered_plants)]

        data['hour_formatted'] = data['hour'].dt.strftime('%H:%M')

        if metric == 'temperature':
            y_field = 'temperature:Q'
            y_title = 'Temperature (°C)'
            data['value_formatted'] = data['temperature'].round(
                1).astype(str) + '°C'
            title = 'Average Temperature Trends (Last 24 Hours)'
        else:
            y_field = 'soil_moisture:Q'
            y_title = 'Soil Moisture (%)'
            data['value_formatted'] = data['soil_moisture'].round(
                1).astype(str) + '%'
            title = 'Average Soil Moisture Trends (Last 24 Hours)'

        return alt.Chart(data).mark_line(point=True).encode(
            x=alt.X('hour:T', title='Time'),
            y=alt.Y(y_field, title=y_title),
            color=alt.Color('plant_name:N', legend=None),
            tooltip=['plant_name', 'hour_formatted', 'value_formatted']
        ).properties(title=title, height=400).interactive()


class FilterComponents:
    """Handles filtering components for the dashboard."""

    @staticmethod
    def create_botanist_filter(botanist_data: pd.DataFrame) -> int:
        """Create a select box for botanist filtering."""
        botanist_options = ["All Botanists"] + botanist_data['name'].tolist()
        selected_botanist = st.sidebar.selectbox(
            "👨‍🔬 Filter by Botanist:",
            options=botanist_options,
            help="Filter data by botanist assignments"
        )

        if selected_botanist != "All Botanists":
            return int(botanist_data[
                botanist_data['name'] == selected_botanist]['botanist_id'].iloc[0])
        return None

    @staticmethod
    def create_species_filter(species_data: pd.DataFrame) -> list[str]:
        """Create a multiselect box for plant species filtering."""
        species_options = species_data['name'].tolist()
        selected_species = st.sidebar.multiselect(
            "🌱 Filter by Plant Species:",
            options=species_options,
            help="Filter data by plant species (select multiple)"
        )

        if selected_species:
            return selected_species
        return None


class DataTableDisplay:
    """Handles table data display components."""

    @staticmethod
    def show_latest_readings_table(latest_readings_data: pd.DataFrame,
                                   filtered_plants: list[str] = None) -> None:
        """Display latest readings in a table."""

        if latest_readings_data.empty:
            st.info("No recent readings available.")
            return None

        if filtered_plants:
            display_data = latest_readings_data[
                latest_readings_data['plant_name'].isin(filtered_plants)
            ]
        else:
            display_data = latest_readings_data

        if display_data.empty:
            st.info("No data matches the current filters.")
            return None

        display_data = display_data.copy()
        display_data['recording_taken'] = pd.to_datetime(
            display_data['recording_taken']).dt.strftime('%Y-%m-%d %H:%M')

        st.dataframe(
            display_data,
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
        return None


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
