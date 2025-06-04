"""Module for extracting from short term storage for use in historic storage."""

from logging import getLogger
from os import environ as ENV

from dotenv import load_dotenv
from pandas import DataFrame
from pyodbc import connect, Connection


def get_connection():
    """Return database connection."""
    logger = getLogger()
    logger.info("Getting RDS connection...")
    connection_string = f"""
                            DRIVER={{ODBC Driver 18 for SQL Server}};
                            SERVER={ENV["DB_HOST"]},{ENV["DB_PORT"]};
                            DATABASE={ENV["DB_NAME"]};
                            UID={ENV["DB_USER"]};
                            PWD={ENV["DB_PASSWORD"]};
                            TrustServerCertificate=yes;
                            Encrypt=yes;
                            Connection Timeout=30;
                         """
    return connect(connection_string)


def get_full_data(conn: Connection, schema: str) -> list:
    """Return row data from full sql query."""
    logger = getLogger()
    logger.info("Send SELECT query to RDS...")
    with conn.cursor() as curs:
        query = f"""SELECT p.plant_id, p.name,
                     r.temperature, r.last_watered, r.soil_moisture,
                     r.recording_taken, ci.name, co.name, b.name
                     FROM {schema}.plant AS P
                     JOIN {schema}.record AS r
                     ON (p.plant_id = r.plant_id)
                     JOIN {schema}.botanist_plant AS bp
                     ON (p.plant_id=bp.plant_id)
                     JOIN {schema}.botanist AS b
                     ON (bp.botanist_id=b.botanist_id)
                     JOIN {schema}.origin_city AS ci
                     ON (p.city_id = ci.city_id)
                     JOIN {schema}.origin_country AS co
                     ON (ci.country_id = co.country_id);"""
        curs.execute(query)
        rows = curs.fetchall()
        if not rows:
            logger.error("No data returned from RDS.")
    return rows


def get_dict_from_rows(rows: list) -> dict:
    """Return dictionary from row data."""
    logger = getLogger()
    logger.info("Converting rows to dictionary...")
    output_object = {
        "plant_id": [],
        "plant_name": [],
        "temperature": [],
        "last_watered": [],
        "soil_moisture": [],
        "recording_taken": [],
        "city": [],
        "country": [],
        "botanist": []
    }
    for row in rows:
        if len(row) == 9:
            output_object["plant_id"].append(row[0])
            output_object["plant_name"].append(row[1])
            output_object["temperature"].append(row[2])
            output_object["last_watered"].append(row[3])
            output_object["soil_moisture"].append(row[4])
            output_object["recording_taken"].append(row[5])
            output_object["city"].append(row[6])
            output_object["country"].append(row[7])
            output_object["botanist"].append(row[8])
            logger.info("Succesfully retrieved values from row")
        else:
            logger.error("Row data is malformed: %s", row)
    return output_object


def get_dataframe_from_dict(data: dict) -> DataFrame:
    """Return Dataframe from dictionary data."""
    logger = getLogger()
    logger.info("Converting dictionary to Dataframe...")
    return DataFrame.from_dict(data)


def truncate_record(conn: Connection, schema: str):
    """Remove data from records table."""
    logger = getLogger()
    logger.info("Removing data from Record table...")
    with conn.cursor() as curs:
        query = f"TRUNCATE TABLE {schema}.record;"
        curs.execute(query)
        curs.commit()


def get_schema() -> str:
    """Return schema name from environment."""
    logger = getLogger()
    logger.info("Checking schema is valid...")
    schema = ENV["DB_SCHEMA"]
    if not schema.isidentifier():
        raise ValueError(f"Invalid schema name: {schema}")
    return schema


def get_data_from_rds() -> DataFrame:
    """Return data as Dataframe from RDS connection."""
    logger = getLogger()
    logger.info("Getting data from RDS...")
    rds_conn = get_connection()
    target_schema = get_schema()
    data_rows = get_full_data(rds_conn, target_schema)
    if data_rows:
        data_dict = get_dict_from_rows(data_rows)
        data_df = get_dataframe_from_dict(data_dict)
        truncate_record(rds_conn, target_schema)
    else:
        data_df = DataFrame()
    rds_conn.close()
    return data_df


if __name__ == "__main__":
    load_dotenv()
    get_data_from_rds()
