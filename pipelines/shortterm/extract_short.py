"""Script to retrieve the data from the plant API."""

import requests
import logging
import pandas as pd
import json
import csv


URL_BASE = "https://sigma-labs-bot.herokuapp.com/api/plants/"


class APIError(Exception):
    """Describes an error triggered by a failing API call."""

    def __init__(self, message: str, code: int = 500):
        """Creates a new APIError instance."""
        self.message = message
        self.code = code


def configure_logs(log_file: str) -> None:
    """Sets up logging for skipped plants."""
    logging.basicConfig(filename=log_file, level=logging.WARNING,
                        format="%(asctime)s - %(levelname)s - %(message)s")


def fetch_plant_info(plant_id: int) -> dict:
    """Returns the json data for the plant with the given id."""

    res = requests.get(
        f"{URL_BASE}{plant_id}")
    if res.status_code == 200:
        return res.json()

    elif res.status_code >= 500:
        raise APIError("Server error occurred.", 500)
    elif res.status_code == 404:
        raise APIError("Plant not found.", 404)
    elif res.status_code == 403:
        raise APIError("Access to resource is forbidden.", 403)
    elif res.status_code == 400:
        raise APIError(
            "Bad Request.", 400)

    else:
        print(f"Failed to fetch plant with id: {plant_id}")


def fetch_all_plants(start_plant: int = 1, end_plant: int = 51) -> list[dict]:
    """Fetches the data from all plants and appends to a list."""

    plants = []
    skipped_ids = []

    for p_id in range(start_plant, end_plant):
        try:
            # print(p_id)
            plant_data = fetch_plant_info(p_id)
            plants.append(plant_data)

        except APIError as e:
            logging.warning(
                f"Skipped plant {p_id} - {e.message}, HTTP {e.code}")
            # print(f"Skipped id: {p_id} - {e.message} HTTP {e.code}")
            skipped_ids.append(p_id)

    # print(f"skipped ids: ", skipped_ids)
    return plants


def save_to_csv(plant_data: list[dict], filename: str) -> None:
    """Converts list of plant dicts to pandas df and saves as CSV."""

    if not plant_data:
        print("No plant data available to save.")
        return

    plants_df = pd.DataFrame(plant_data)
    plants_df.to_csv(filename, index=False)
    print(f"Saved {len(plant_data)} plant records to {filename}.")


if __name__ == "__main__":
    configure_logs("skipped_plants.log")
    all_plant_data = fetch_all_plants()
    print(
        f"Successfully retrieved {len(all_plant_data)} plant records.\n"
        "Logged skipped entries to 'skipped_plants.log'."
    )

    save_to_csv(all_plant_data, "plant_data.csv")
