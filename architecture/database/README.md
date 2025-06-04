# Database

The Liverpool Natural History Museum Plant Monitoring System is stored in two parts. With short-term daily data being stored on an AWS RDS instance using Microsoft SQL Server, and long-term historical data being stored in an S3 bucket.

## Short-term

The short term data solution uses a 3NF design [ERD](short_term_erd.png), to reduce redundancy and improve efficiency when querying. The schema for this can be viewed in the[here](schema.sql). 


Use `bash connect.sh` to connect to the database. If this is your first time running this script you should run `bash set_up_database.sh`.  

## Long-term

The long term data solution stores columnar Parquet files in an S3 bucket with the following structure:

```
LMNH-long-term-plant-storage
├── output
├── input
│   ├── plant
│   │   ├── year=2025/
│   │   │    ├── month=06/
│   │   │    │    ├── day=01/
│   │   │    │    │    │    └── summary.parquet
│   │   │    │    ├── day=02/
│   │   │    │    │    │    └── summary.parquet
│   │   │    │    │    └── …
│   │   │    │    └── …
│   │   │    └── …
│   └── …
```

This structure enables efficient querying of the historic data for each individual plant's history. 