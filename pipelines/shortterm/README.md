# Short Term Pipeline

# Setup
- Setup virtual environment
    - Run `python3 -m venv .venv`
    - Run `source .venv/bin/activate`
- Install dependencies
    - Run `pip install -r requirements.txt`


# `.env file`

```sh
DB_HOST=<DB_IP_ADDRESS>
DB_PORT=<PORT>
DB_NAME=<NAME_OF_DB>
DB_PASSWORD=<PASS_FOR_DB>
DB_USER=<USER_FOR_ACCESSING_DB>
DB_SCHEMA=<SCHEMA_USED_FOR_DB>

AWS_REGION=<REGION_THAT_RESOURCES_DEPLOY_TO>
AWS_ACCESS_KEY_ID=<AWS_USER_KEY_IDENTIFIER>
AWS_SECRET_ACCESS_KEY=<AWS_USER_KEY_SECRET>
S3_BUCKET=<BUCKET_FROM_TERRAFORM>
```

# Python

## `extract` module

### Key Steps 
- Defines a custom `APIError` class to raise specific HTTP-related issues (404, 500, etc).
- Fetches data for each plant via the API.
- Loops through plant ids 1 to 50, skipping missing plants.
- Returns a pandas DataFrame containing all the individual plant data.
- Logs all skipped plants (with their IDS, error messages, and status codes) to 'skipped_plants.log' file.


## `transform` module

Responsible for transforming the raw plant data into a clean, structured format, so that it is ready for the loading phase.

### Key Steps
- Pulls the raw data using the `fetch_all_plants` function from `extract_short.py`.
    - Can optionally clean the data from an uncleaned CSV if using the `load_csv` function.
- Extracts nested fields from dictionary structures (botanist, origin_location).
- Drops columns not required in the loading phase (botanist, images, etc).
- Converts strings to str objects.
- Converts and rounds numeric fields .
- Ensures date/time columns are datetime objects.
- Formats phone numbers into valid E.164 format (e.g `+1234567890`), defaulting to UK (leading with `+44`).
- Returns a cleaned Pandas DataFrame, ready to be loaded into the RDS database..

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

## `load` module

### Key Steps
- Takes in transformed data as a pandas DataFrame.
- Has a function to insert data in every table within the database.
- Populates all tables within the database (Checks for duplicates).


## `pipeline` script

This script is required for running the short term ETL pipeline for the LMNH Plant Health project.

### Key Steps
- Calls the data transformation logic and retrieves a cleaned Pandas DataFrame.
- Loads a cleaned DataFrame into the RDS.
- Includes logging to track progress of the pipeline and for debugging purposes.

- The 'lambda_handler' function triggers the above steps in the cloud.
- Returns status codes for integration with cloud services.

### Usage
- To run from the command line: `python3 pipeline_short.py`.
- Or deployed using **AWS Lambda** for cloud-based automated execution.


# Dockerfile

Allows the short-term ETL pipeline to be packaged and deployed as a container, making it suitable for execution on AWS Lambda with custom dependencies such as OBDC drivers.

### Key Steps

- Installs all required python packages and OBDC drivers.
- Copies all the required ETL scripts.
- Sets the lambda handler function that AWS Lambda should run when triggered.

### Usage 

To build and test locally:
- Run `docker build -t [name-of-image] .`.
- Run `docker run [name-of-image]`.

To build and push the docker image to AWS:
- 1. Authenticate docker to AWS ECR registry.
- 2. Create a repository on ECR if not done already.
- 3. Tag local Docker image for the ECR.
- 4. Push image to ECR.