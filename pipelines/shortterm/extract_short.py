"""Script to retrieve the data from the plant API."""

import requests
import logging
import pandas as pd
import json
import csv


class APIError(Exception):
    """Describes an error triggered by a failing API call."""

    def __init__(self, message: str, code: int = 500):
        """Creates a new APIError instance."""
        self.message = message
        self.code = code


def configure_logs(log_file: str) -> None:
    """Sets up logging for skipped plants."""
    logging.basicConfig(
        filename=log_file,
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def validate_status(status_code: int, plant_id: int) -> None:
    """Returns True if valid status (200), otherwise returns False."""
    if status_code == 200:
        return
    elif status_code >= 500:
        raise APIError(f"Server error occurred. {status_code}", 500)
    elif status_code == 404:
        raise APIError("Plant not found.", 404)
    elif status_code == 403:
        raise APIError("Access to resource is forbidden.", 403)
    elif status_code == 400:
        raise APIError("Bad Request.", 400)
    else:
        raise APIError(
            f"Unexpected error for plant with id: {plant_id}", status_code)


def fetch_plant_info(plant_id: int) -> dict:
    """Returns plant data from the API for a given id."""
    base_url = "https://sigma-labs-bot.herokuapp.com/api/plants/"

    res = requests.get(f"{base_url}{plant_id}")
    validate_status(res.status_code, plant_id)
    return res.json()


def fetch_all_plants(start_plant: int = 1, end_plant: int = 50) -> list[dict]:
    """Fetches the data from all plants, appends to a list and returns a DataFrame."""
    plants = []
    skipped_ids = []

    for p_id in range(start_plant, end_plant+1):
        try:
            plant_data = fetch_plant_info(p_id)
            plants.append(plant_data)
        except APIError as e:
            logging.warning(
                f"Skipped plant {p_id} - {e.message}, HTTP {e.code}")
            skipped_ids.append(p_id)

    if not plants:
        logging.warning("No plant data was fetched.")
    return pd.DataFrame(plants)


def save_to_csv(plant_data: pd.DataFrame, filename: str) -> None:
    """Converts list of plant dicts to pandas DataFrame and saves as CSV."""
    plant_data.to_csv(filename, index=False)
    print(f"Saved {len(plant_data)} plant records to {filename}.")


if __name__ == "__main__":
    configure_logs("skipped_plants.log")
    plants_df = fetch_all_plants()
    print(
        f"Successfully retrieved {len(plants_df)} plant records.\n"
        "Logged skipped entries to 'skipped_plants.log'."
    )
    save_to_csv(plants_df, "plant_data_2.csv")
