"""Script to clean the raw plant data."""
import pandas as pd
import json


def load_csv(filename: str) -> pd.DataFrame:
    """Loads raw plant data csv into a pandas dataframe"""

    return pd.read_csv(filename)


def drop_irrelevant_columns(plants_df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Removes unnecessary columns that aren't needed for loading."""

    return plants_df.drop(columns=columns)


def clean_df(plants_df: pd.DataFrame) -> pd.DataFrame:
    """Transforms and cleans dataframe to match target schema."""

    columns_to_remove = ["origin_location"]
    drop_irrelevant_columns(plants_df, columns_to_remove)

    ordered_cols = ["plant_id", "name", "temperature", "last_watered",
                    "soil_moisture", "recording_taken", "botanist_name",
                    "image_url", "scientific_name"]
    plants_df = plants_df[ordered_cols]


def save_to_csv(plants_df: pd.DataFrame, output_path: str) -> None:
    """Saves cleaned df to csv file."""

    plants_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    raw_plant_df = load_csv("plant_data.csv")

    clean_plant_df = clean_df(raw_plant_df)

    save_to_csv(clean_plant_df, "clean_plant_data.csv")
