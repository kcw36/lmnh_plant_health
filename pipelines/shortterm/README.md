
# Short Term Pipeline

## Setup
- Setup virtual environment
    - Run `python3 -m venv .venv`
    - Run `source .venv/bin/activate`
- Install dependencies
    - Run `pip install -r requirements.txt`


## `extract_short.py` module

### Key Steps 
- Defines a custom `APIError` class to raise specific HTTP-related issues (404, 500, etc)
- Fetches data for each plant via the API
- Loops through plant ids 1 to 50, skipping missing plants
- Returns a pandas DataFrame containing all the individual plant data
- Logs all skipped plants (with their IDS, error messages, and status codes) to 'skipped_plants.log' file


## `transform_short.py` module

Responsible for transforming the raw plant data into a clean, structured format, 
so that it is ready for the loading phase

### Key Steps
- Pulls the raw data using the `fetch_all_plants` function from `extract_short.py`
    - Can optionally clean the data from an uncleaned CSV if using the `load_csv` function.
- Extracts nested fields from dictionary structures (botanist, origin_location)
- Drops columns not required in the loading phase (botanist, images, etc)
- Converts strings to str objects
- Converts and rounds numeric fields 
- Ensures date/time columns are datetime objects
- Formats phone numbers into valid E.164 format (e.g `+1234567890`), defaulting to UK (leading with `+44`)
- Returns a cleaned Pandas DataFrame, ready to be loaded into the RDS database.

### Output
The transformed DataFrame contains the following columns:

- 'plant_id' (int)
- 'name' (str object)
- 'origin_city' (str object)
- 'origin_country' (str object)
- 'temperature' (float)
- 'last_watered' (datetime)
- 'soil_moisture' (float)
- 'recording_taken' (datetime)
- 'botanist_name' (str object)
- 'botanist_email' (str object)
- 'botanist_phone' (str object)
