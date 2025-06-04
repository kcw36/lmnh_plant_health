"""Script to clean the raw plant data."""
import pandas as pd
import json

from extract_short import fetch_all_plants


def load_csv(filename: str) -> pd.DataFrame:
    """Loads raw plant data csv into a pandas dataframe"""

    return pd.read_csv(filename)


def extract_nested_columns(raw_plants: pd.DataFrame) -> pd.DataFrame:
    """Extracts the necessary data from the columns containing dictionaries."""

    raw_plants_df = raw_plants.copy()

    botanist = raw_plants_df['botanist'].apply(pd.Series)
    raw_plants_df['botanist_name'] = botanist['name']
    raw_plants_df['botanist_email'] = botanist['email']
    raw_plants_df['botanist_phone'] = botanist['phone']

    origin = raw_plants_df['origin_location'].apply(pd.Series)
    raw_plants_df['origin_city'] = origin['city']
    raw_plants_df['origin_country'] = origin['country']

    image = raw_plants_df['images'].apply(pd.Series)
    raw_plants_df['image_url'] = image['original_url']

    return raw_plants_df


def drop_irrelevant_columns(plants_df: pd.DataFrame) -> pd.DataFrame:
    """Removes unnecessary columns that aren't needed for loading."""
    columns_to_drop = ['origin_location', 'botanist', 'images']

    return plants_df.drop(columns=columns_to_drop)


def clean_df(plants_df: pd.DataFrame) -> pd.DataFrame:
    """Transforms and cleans dataframe to match target schema."""

    # convert strings
    plants_df['scientific_name'] = plants_df['scientific_name'].astype(
        str).fillna('')
    plants_df['image_url'] = plants_df['image_url'].astype(str).fillna('')
    plants_df['origin_city'] = plants_df['origin_city'].astype(str)
    plants_df['origin_country'] = plants_df['origin_country'].astype(str)
    plants_df['botanist_email'] = plants_df['botanist_email'].astype(str)
    plants_df['botanist_phone'] = plants_df['botanist_phone'].astype(str)

    # convert numeric
    plants_df['temperature'] = pd.to_numeric(
        plants_df['temperature'], errors='coerce')
    plants_df['soil_moisture'] = pd.to_numeric(
        plants_df['soil_moisture'], errors='coerce')

    # convert timestamps
    plants_df['last_watered'] = pd.to_datetime(
        plants_df['last_watered'], errors='coerce')
    plants_df['recording_taken'] = pd.to_datetime(
        plants_df['recording_taken'], errors='coerce')

    ordered_cols = ['plant_id', 'name', 'origin_city', 'origin_country',
                    'temperature', 'last_watered', 'soil_moisture',
                    'recording_taken', 'botanist_name', 'botanist_email',
                    'botanist_phone', 'image_url', 'scientific_name']
    clean_df = plants_df[ordered_cols]

    return clean_df


def save_to_csv(clean_plants: pd.DataFrame, output_path: str) -> None:
    """Saves cleaned df to csv file."""

    clean_plants.to_csv(output_path, index=False)


def transform_data() -> pd.DataFrame:
    """Runs the transformation phase of the pipeline."""

    raw_plants_df = fetch_all_plants()
    raw_plants_df = extract_nested_columns(raw_plants_df)
    raw_plants_df = drop_irrelevant_columns(raw_plants_df)
    clean_plants_df = clean_df(raw_plants_df)

    save_to_csv(clean_plants_df)


if __name__ == "__main__":

    transform_data()
