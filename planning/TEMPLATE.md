# Pipeline

- This module is repsonsible for an extract, transform, load pipeline from A MySQL to S3.
- This module stores the data as partioned parquet files using star schema

# Installation

- This module requires Docker, aws cli and python installed
    - Install Pages:
        - Docker: [INSTALL](https://www.docker.com/products/docker-desktop/)
        - Python: [INSTALL](https://www.python.org/downloads/)
- All files should be ran from the module directory `~/pipeline`

# `.env file`

```txt
DB_HOST=<DB_IP_ADDRESS>
DB_PORT=<PORT>
DB_NAME=<NAME_OF_DB>
DB_PASSWORD=<PASS_FOR_DB>
DB_USER=<USER_FOR_ACCESSING_DB>

AWS_REGION=<REGION_THAT_RESOURCES_DEPLOY_TO>
AWS_ACCESS_KEY_ID=<AWS_USER_KEY_IDENTIFIER>
AWS_SECRET_ACCESS_KEY=<AWS_USER_KEY_SECRET>

S3_BUCKET=<NAME_OF_BUCKET_TO_SEND_QUERY_RESULTS_TO>
GLUE_CATALOG_NAME=<NAME_OF_CATALOG_TO_QUERY>
```

# Python Modules

- Create a venv
    - `python -m venv .venv`
- Install dependencies
    - `pip install -r requirements.txt`

## `pipeline`

- Runs the pipeline using the other modules
- `python pipeline.py`

## `extract`

- Provides utilties for extracting the data from a MySQL database.

## `transform`

- Provides utilties for transforming data in preparation for loading.

## `load`

- Provides utilties for loading data into local parquet files and/or into a cloud hosted AWS S3 bucket.

# Testing Python

- All the python utilty modules have associated test files in th format `test_<module_name>.py`
- `conftest.py` provides test fixtures for those tests
- To run the test suite
    - `pytest *.py`
    - OR
    - `pytes *.py -vvx` for more verbosity

# Docker

## `Dockerfile`

- Configuration for building a docker image of the pipeline for use in containers
