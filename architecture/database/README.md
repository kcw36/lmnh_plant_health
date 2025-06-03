# Database

The Liverpool Natural History Museum Plant Monitoring System is stored in two parts. With short-term daily data being stored on an AWS RDS instance using Microsoft SQL Server, and long-term historical data being stored in an S3 bucket.

## Short-term


## Long-term

The long term data solution stores columnar Parquet files in an S3 bucket with the following structure:

```
LMNH-long-term-plant-storage
├── output
├── input
│   ├── image
│   │   ├── images.parquet
│   ├── scientific_name
│   │   ├── scientific_names.parquet
│   ├── origin
│   │   ├── origin_locations.parquet
│   ├── botanist
│   │   ├── botanists.parquet
│   ├── plant
│   │   ├── year=2025/
│   │   │    ├── month=06/
│   │   │    │    ├── day=01/
│   │   │    │    │    ├── plant_id=1/
│   │   │    │    │    │    └── summary.parquet
│   │   │    │    │    ├── plant_id=2/
│   │   │    │    │    │    └── summary.parquet
│   │   │    │    │    └── plant_id=…/
│   │   │    │    ├── day=02/
│   │   │    │    │    ├── plant_id=1/
│   │   │    │    │    │    └── summary.parquet
│   │   │    │    │    └── …
│   │   │    │    └── …
│   │   │    └── …
│   └── …
```

This structure enables efficient querying of the historic data for each individual plant's history. 