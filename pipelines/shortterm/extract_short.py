"""Script to retrieve the data from the plant API."""

import requests
import json


URL_BASE = "https://sigma-labs-bot.herokuapp.com/api/plants/"


class APIError(Exception):
    """Describes an error triggered by a failing API call."""

    def __init__(self, message: str, code: int = 500):
        """Creates a new APIError instance."""
        self.message = message
        self.code = code


def fetch_plant_info(plant_id: int) -> dict:
    """Returns the json data for the plant with the given id."""

    res = requests.get(
        f"{URL_BASE}{plant_id}")
    if res.status_code == 200:
        return res.json()

    elif res.status_code >= 500:
        raise APIError("Server error occurred.", 500)
    elif res.status_code == 404:
        raise APIError("Page not found.", 404)
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
    # plant_ids = (1, 51)

    for p_id in range(start_plant, end_plant):
        try:
            # print(p_id)
            plant_data = fetch_plant_info(p_id)
            plants.append(plant_data)
        except APIError as e:
            skipped_ids.append(p_id)
    print(f"skipped ids: ", skipped_ids)

    return plants


if __name__ == "__main__":
    all_plant_data = fetch_all_plants()
    print(
        f"Successfully retrieved all plant data, length={len(all_plant_data)}")
