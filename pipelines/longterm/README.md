# Longterm Pipeline

- This module is repsonsible for an extract, transform, load pipeline from a RDS instance to a S3 bucket.
- This module stores the data as partioned parquet files using star schema.

# Installation

## Python
### Mac
- Use Homebrew
    - `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- Install python with brew
    - `brew install python`
### Windows
- Use Chocolatey
    - `Set-ExecutionPolicy AllSigned`
    - `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`
- Install python with choco
    - `choco install python`
### Linux
- `apt install python3`
## Python Modules
- Create a venv
    - `python -m venv .venv`
- Activate venv
    - On Mac/Linux
        - `source .venv/bin/activate`
    - On Windows
        - `.\.venv\Scripts\activate.bat`
- Install dependencies
    - `pip install -r requirements.txt`
## SQL Server Driver
- ODBC Driver Manager
    - `brew install unixodbc`
- ODBC Driver for SQL from Mac
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18 mssql-tools18
```

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
```

# Modules

<b> All files should be ran from the module directory `/pipelines/longterm/` </b>

## `pipeline`

## `extract`
- Provides utilities for extracting data from a cloud hosted RDS for SQL Server Instance.

## `transform`

## `load`
- Provides utilties for loading data into a cloud hosted AWS S3 bucket.

# Testing Python

- All the python utilty modules have associated test files in th format `test_<module_name>.py`
- `conftest.py` provides test fixtures for those tests
- To run the test suite
    - `pytest *.py`
    - OR
    - `pytes *.py -vvx` for more verbosity
