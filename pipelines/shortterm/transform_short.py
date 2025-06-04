"""Script to clean the raw plant data."""
import pandas as pd
from extract_short import fetch_all_plants


def load_csv(filename: str) -> pd.DataFrame:
    """Loads raw plant data csv into a pandas dataframe."""

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

    return raw_plants_df


def drop_irrelevant_columns(plants_df: pd.DataFrame) -> pd.DataFrame:
    """Removes unnecessary columns that aren't needed for loading."""
    columns_to_drop = ['origin_location',
                       'botanist', 'images', 'scientific_name']

    return plants_df.drop(columns=columns_to_drop)


def validate_string_cols(plants_df: pd.DataFrame) -> pd.DataFrame:
    """Ensures relevant columns are clean strings."""

    plants_df['origin_city'] = plants_df['origin_city'].astype(str)
    plants_df['origin_country'] = plants_df['origin_country'].astype(str)
    plants_df['botanist_email'] = plants_df['botanist_email'].astype(str)
    plants_df['botanist_phone'] = plants_df['botanist_phone'].astype(str)

    return plants_df


def validate_numeric_cols(plants_df: pd.DataFrame) -> pd.DataFrame:
    """Ensures numeric columns are valid numbers."""

    plants_df['temperature'] = pd.to_numeric(
        plants_df['temperature'], errors='coerce').round(2)
    plants_df['soil_moisture'] = pd.to_numeric(
        plants_df['soil_moisture'], errors='coerce').round(2)

    return plants_df


def validate_datetime_cols(plants_df: pd.DataFrame) -> pd.DataFrame:
    """Converts columns to proper datetime format."""

    plants_df['last_watered'] = pd.to_datetime(
        plants_df['last_watered'], errors='coerce')
    plants_df['recording_taken'] = pd.to_datetime(
        plants_df['recording_taken'], errors='coerce')

    return plants_df


def clean_phone_nos(plants_df: pd.DataFrame) -> pd.DataFrame:
    """Cleans phone numbers to be compatible with AWS SNS E.164 format."""

    cleaned_phone_nos = []
    for phone_no in plants_df['botanist_phone']:
        if pd.isna(phone_no):
            cleaned_phone_nos.append('')
            continue
        phone_no = str(phone_no)
        if 'x' in phone_no:  # remove extension (e.g 1234 x373)
            phone_no = phone_no.split('x')[0]

        # filters out symbols (like '-', '.', '+')
        number_str = ''.join(char for char in phone_no if char.isdigit())

        if len(number_str) == 11 and number_str.startswith('0'):  # UK number
            cleaned_no = '+44'+number_str[1:]
        elif len(number_str) == 11 and number_str.startswith('1'):  # US number
            cleaned_no = '+'+number_str
        elif len(number_str) == 10:  # default to UK
            cleaned_no = '+44'+number_str
        else:  # couldn't classify as UK or US, must be other intl.
            cleaned_no = '+'+number_str
        cleaned_phone_nos.append(cleaned_no)
    plants_df['botanist_phone'] = cleaned_phone_nos
    return plants_df


def clean_df(plants_df: pd.DataFrame) -> pd.DataFrame:
    """Transforms and cleans dataframe to match target schema."""

    plants_df = validate_string_cols(plants_df)
    plants_df = validate_numeric_cols(plants_df)
    plants_df = validate_datetime_cols(plants_df)
    plants_df = clean_phone_nos(plants_df)

    plants_df = plants_df.fillna('')
    ordered_cols = ['plant_id', 'name', 'origin_city', 'origin_country',
                    'temperature', 'last_watered', 'soil_moisture',
                    'recording_taken', 'botanist_name', 'botanist_email',
                    'botanist_phone']
    clean_df = plants_df[ordered_cols]
    return clean_df


def save_to_csv(clean_plants: pd.DataFrame, output_path: str) -> None:
    """Saves cleaned pandas DataFrame to CSV file."""

    clean_plants.to_csv(output_path, index=False)


def transform_data() -> pd.DataFrame:
    """Runs the transformation phase of the pipeline."""

    raw_plants_df = fetch_all_plants()
    raw_plants_df = extract_nested_columns(raw_plants_df)
    raw_plants_df = drop_irrelevant_columns(raw_plants_df)
    clean_plants_df = clean_df(raw_plants_df)

    save_to_csv(clean_plants_df, "clean_plants.csv")
    return clean_plants_df


if __name__ == "__main__":

    transform_data()
