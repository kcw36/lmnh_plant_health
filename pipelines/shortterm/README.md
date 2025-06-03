
# Short Term Pipeline

## Setup
- setup virtual environment
- pip install -r requirements.txt


## Extract_short.py script

- Defines a custom 'APIError' class to raise specific HTTP-related issues (404, 500, etc)
- Fetches data for each plant via the API
- Loops through plant ids 1 to 50, skipping missing plants
- Returns a list of dictinaries each containing individual plant info
- Logs all skipped plants (the IDS and error messages) to 'skipped_plants.log' file