"""Module for extracting from short term storage for use in historic storage."""

from sys import stdout
from logging import getLogger, INFO, StreamHandler
from os import environ as ENV

from dotenv import load_dotenv
from pandas import DataFrame
from pyodbc import connect, Connection


def get_connection():
    """Return database connection."""
    logger = getLogger(__name__)
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


def set_schema(conn: Connection):
    """Set schema for connection."""
    logger = getLogger(__name__)
    logger.info("Setting DB schema..")
    with conn.cursor() as curs:
        schema = ENV["DB_SCHEMA"]
        if not schema.isidentifier():
            raise ValueError(f"Invalid schema name: {schema}")
        curs.execute(f"USE {schema};")
        curs.commit()


def get_full_data(conn: Connection) -> list:
    """Return row data from full sql query."""
    logger = getLogger(__name__)
    logger.info("Send SELECT query to RDS...")
    with conn.cursor() as curs:
        query = """SELECT (p.plant_id, p.name,
                     r.temperature, r.last_watered, r.soil_moisture,
                     r.recording_taken, ci.name, co.name, b.name)
                     FROM plant AS P
                     JOIN record AS r
                     ON (p.plant_id = r.plant_id)
                     JOIN botanist_plant AS bp
                     ON (p.plant_id=bp.plant_id)
                     JOIN botanist AS b
                     ON (bp.botanist_id=b.botanist_id)
                     JOIN origin_city AS ci
                     ON (p.city_id = ci.city_id)
                     JOIN origin_county AS co
                     ON (ci.country_id = co.country_id);"""
        curs.execute(query)
        curs.fetchall()
        rows = curs.fetchall()
    return rows


def get_dict_from_rows(rows: list) -> dict:
    """Return dictionary from row data."""
    logger = getLogger(__name__)
    logger.info("Converting rows to dictionary...")
    output_object = {
        "plant_id": None,
        "plant_name": None,
        "temperature": None,
        "last_watered": None,
        "soil_moisture": None,
        "recording_taken": None,
        "city": None,
        "country": None,
        "botanist": None
    }
    for row in rows:
        if row.length == 9:
            output_object["plant_id"] += row[0]
            output_object["plant_name"] += row[1]
            output_object["temperature"] += row[2]
            output_object["last_watered"] += row[3]
            output_object["soil_moisture"] += row[4]
            output_object["recording_taken"] += row[5]
            output_object["city"] += row[6]
            output_object["country"] += row[7]
            output_object["botanist"] += row[8]
            logger.info("Succesfully retrieved values from row")
        else:
            logger.error("Row data is malformed: %s", row)
    return output_object


def get_dataframe_from_dict(object: dict) -> DataFrame:
    """Return Dataframe from dictionary data."""
    logger = getLogger(__name__)
    logger.info("Converting dictionary to Dataframe...")
    return DataFrame(object)


def truncate_record(conn: Connection):
    """Remove data from records table."""
    logger = getLogger(__name__)
    logger.info("Removing data from Record table...")
    with conn.cursor() as curs:
        query = F"TRUNCATE TABLE record;"
        curs.execute(query)
        curs.commit()


def get_data_from_RDS() -> DataFrame:
    """Return data as Dataframe from RDS connection."""
    logger = getLogger(__name__)
    logger.info("Getting data from RDS...")
    rds_conn = get_connection()
    set_schema(rds_conn)
    data_rows = get_full_data(rds_conn)
    data_dict = get_dict_from_rows(data_rows)
    data_df = get_dataframe_from_dict(data_dict)
    truncate_record(rds_conn)
    rds_conn.close()
    return data_df


if __name__ == "__main__":
    load_dotenv()
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    logger.addHandler(StreamHandler(stdout))
    get_data_from_RDS()
