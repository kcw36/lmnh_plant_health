
# Short Term Pipeline

## Setup
- Setup virtual environment
    - Run `python3 -m venv .venv`
    - Run `source .venv/bin/activate`
- Install dependencies
    - Run `pip install -r requirements.txt`


## Extract_short.py script

- Defines a custom `APIError` class to raise specific HTTP-related issues (404, 500, etc)
- Fetches data for each plant via the API
- Loops through plant ids 1 to 50, skipping missing plants
- Returns a pandas DataFrame containing all the individual plant data
- Logs all skipped plants (with their IDS, error messages, and status codes) to 'skipped_plants.log' file

## load_short.py script

- Takes in transformed data as a pandas DataFrame
- Has a function to insert data in every table within the database
- Populates all tables within the database (Checks for duplicates)
