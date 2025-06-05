"""Modules for loading data to SQL Server DB."""

from logging import getLogger
from os import environ as ENV

import pandas as pd
from pandas import DataFrame

from dotenv import load_dotenv
from pyodbc import connect, Connection


def get_connection() -> Connection:
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


def insert_origin_country(data: DataFrame, conn: Connection):
    """Insert data into `origin_country` table."""
    logger = getLogger()
    logger.info("Inserting into origin_country...")

    existing_countries_query = "SELECT name FROM gamma.origin_country;"
    countries_in_db = pd.read_sql(existing_countries_query, conn)[
        "name"].to_list()
    logger.info("Querying the `origin_country` table for country names.")

    unique_countries = data["origin_country"].unique()

    countries_to_insert = [
        country for country in unique_countries if country not in countries_in_db
    ]

    if countries_to_insert:
        insert_query = """INSERT INTO gamma.origin_country (name) VALUES (?);"""
        with conn.cursor() as curs:
            curs.executemany(insert_query, [(country,)
                                            for country in countries_to_insert])
            conn.commit()
            logger.info("Inserted %d new countries.", len(countries_to_insert))
    else:
        logger.info("No new countries to insert.")


def insert_botanist(data: DataFrame, conn: Connection):
    """Insert data into `botanist` table."""
    logger = getLogger()
    logger.info("Inserting into botanist...")

    existing_botanist_query = "SELECT name, email, phone FROM gamma.botanist;"
    botanist_in_db = pd.read_sql(existing_botanist_query, conn)
    logger.info("Querying the `botanist` table for botanist names and emails.")
    botanist_in_db = set(botanist_in_db.itertuples(index=False, name=None))

    unique_botanists = data[["botanist_name",
                             "botanist_email", "botanist_phone"]].drop_duplicates()
    unique_botanists = set(unique_botanists.itertuples(index=False, name=None))

    botanist_to_insert = list(unique_botanists - botanist_in_db)

    if botanist_to_insert:
        insert_query = "INSERT INTO gamma.botanist (name, email, phone) VALUES (?, ?, ?);"
        with conn.cursor() as curs:
            curs.executemany(insert_query, botanist_to_insert)
            conn.commit()
            logger.info("Inserted %d new botanists.", len(botanist_to_insert))
    else:
        logger.info("No new botanists to insert.")


def insert_origin_city(data: DataFrame, conn: Connection):
    """Insert data into `origin_city` table."""
    logger = getLogger()
    logger.info("Inserting into origin_city...")

    country_query = "SELECT country_id, name FROM gamma.origin_country"
    countries_in_db = pd.read_sql(country_query, conn)
    logger.info(
        "Querying the `origin_country` table for country name and its country_id.")
    countries_in_db = dict(
        zip(countries_in_db["name"], countries_in_db["country_id"]))

    existing_city_query = "SELECT name, country_id FROM gamma.origin_city"
    cities_in_db = pd.read_sql(existing_city_query, conn)
    logger.info(
        "Querying the `origin_city` table for city name and country_id associated with it.")
    cities_in_db = set(cities_in_db.itertuples(index=False, name=None))

    unique_cities = data[["origin_city", "origin_country"]
                         ].drop_duplicates()
    unique_cities["country_id"] = unique_cities["origin_country"].map(
        countries_in_db)
    unique_cities = unique_cities.dropna(subset=["country_id"])
    unique_cities = set(unique_cities[["origin_city", "country_id"]].itertuples(
        index=False, name=None))

    cities_to_insert = list(unique_cities - cities_in_db)

    if cities_to_insert:
        insert_query = "INSERT INTO gamma.origin_city (name, country_id) VALUES (?, ?)"
        with conn.cursor() as curs:
            curs.executemany(insert_query, cities_to_insert)
            conn.commit()
            logger.info("Inserted %d new cities.", len(cities_to_insert))
    else:
        logger.info("No new cities to insert.")


def insert_plant(data: DataFrame, conn: Connection):
    """Insert data into `plant` table."""
    logger = getLogger()
    logger.info("Inserting into plant...")

    city_country_query = """
            SELECT origin_city.city_id,
              origin_city.name AS city_name,
              origin_country.country_id,
              origin_country.name AS country_name 
            FROM gamma.origin_city  
            JOIN gamma.origin_country ON origin_city.country_id = origin_country.country_id
    """
    city_country = pd.read_sql(city_country_query, conn)
    city_country = {
        (row.city_name, row.country_name): row.city_id
        for row in city_country.itertuples(index=False)
    }

    existing_plant_query = "SELECT plant_id FROM gamma.plant"
    plants_in_db = pd.read_sql(existing_plant_query, conn)[
        "plant_id"].to_list()

    unique_plants = data[["plant_id", "name", "origin_city",
                          "origin_country"]].drop_duplicates()
    unique_plants["city_id"] = unique_plants.apply(
        lambda row: city_country.get((row.origin_city, row.origin_country)), axis=1

    )
    plants_to_insert = unique_plants[~unique_plants["plant_id"].isin(
        plants_in_db)]
    plants_to_insert = list(plants_to_insert[["plant_id", "name", "city_id"]].itertuples(
        index=False, name=None))

    if plants_to_insert:
        insert_query = "INSERT INTO gamma.plant (plant_id, name, city_id) VALUES (?, ?, ?)"
        with conn.cursor() as curs:
            curs.executemany(insert_query, plants_to_insert)
            conn.commit()
            logger.info("Inserted %d new plants.", len(plants_to_insert))
    else:
        logger.info("No new plants to insert.")


def insert_botanist_plant(data: DataFrame, conn: Connection):
    """Insert data into `botanist_plant` table."""
    logger = getLogger()
    logger.info("Inserting into botanist_plant...")

    botanist_id_email_query = "SELECT botanist_id, email FROM gamma.botanist"
    botanist_id_email = pd.read_sql(botanist_id_email_query, conn)
    botanist_id_email = dict(
        zip(botanist_id_email["email"], botanist_id_email["botanist_id"]))

    botanist_plant_query = "SELECT plant_id, botanist_id FROM gamma.botanist_plant"
    botanist_plant_in_db = pd.read_sql(botanist_plant_query, conn)
    botanist_plant_in_db = set(tuple(x)
                               for x in botanist_plant_in_db.to_numpy())

    botanist_plants = data[["plant_id", "botanist_email"]].drop_duplicates()
    botanist_plants["botanist_id"] = botanist_plants["botanist_email"].map(
        botanist_id_email)

    botanist_plant_to_insert = [
        (int(row.plant_id), int(row.botanist_id))
        for row in botanist_plants.itertuples(index=False)
        if (int(row.plant_id), int(row.botanist_id)) not in botanist_plant_in_db
    ]

    if botanist_plant_to_insert:
        insert_query = "INSERT INTO gamma.botanist_plant (plant_id, botanist_id) VALUES (?, ?)"
        with conn.cursor() as curs:
            curs.executemany(insert_query, botanist_plant_to_insert)
            conn.commit()
            logger.info("Inserted %d new botanist_plant records.",
                        len(botanist_plant_to_insert))
    else:
        logger.info("No new botanist_plant records to insert.")


def insert_record(data: DataFrame, conn: Connection):
    """Insert data into `record` table."""
    logger = getLogger()
    logger.info("Inserting into record...")

    records = data[[
        "temperature",
        "last_watered",
        "soil_moisture",
        "recording_taken",
        "plant_id"
    ]].drop_duplicates()

    records["last_watered"] = pd.to_datetime(records["last_watered"], utc=True)
    records["recording_taken"] = pd.to_datetime(
        records["recording_taken"], utc=True)

    records_to_insert = [
        (
            float(row.temperature),
            row.last_watered,
            float(row.soil_moisture),
            row.recording_taken,
            int(row.plant_id)
        )
        for row in records.itertuples(index=False)
    ]

    if records_to_insert:
        insert_query = """
            INSERT INTO gamma.record (temperature, last_watered, soil_moisture, recording_taken, plant_id)
            VALUES (?, ?, ?, ?, ?)
        """
        with conn.cursor() as curs:
            curs.executemany(insert_query, records_to_insert)
            conn.commit()
            logger.info("Inserted %d new records.", len(records_to_insert))
    else:
        logger.info("No new records to insert.")


def load_data(data: DataFrame, conn: Connection):
    """Load all plant data to the database in correct order."""
    logger = getLogger()
    logger.info("Starting data load pipeline...")

    insert_origin_country(data, conn)
    insert_origin_city(data, conn)
    insert_botanist(data, conn)
    insert_plant(data, conn)
    insert_botanist_plant(data, conn)
    insert_record(data, conn)

    logger.info("Data load pipeline completed successfully.")


if __name__ == "__main__":
    load_dotenv()

    plants_data = [
        {
            'plant_id': 1,
            'name': 'Venus flytrap',
            'origin_city': 'Stammside',
            'origin_country': 'Albania',
            'temperature': 13.77,
            'last_watered': '2025-06-04 13:51:41.000000+00:00',
            'soil_moisture': 92.33,
            'recording_taken': '2025-06-04 16:10:03.000000+00:00',
            'botanist_name': 'Kenneth Buckridge',
            'botanist_email': 'kenneth.buckridge@lnhm.co.uk',
            'botanist_phone': '+7639148635'
        },
        {
            'plant_id': 2,
            'name': 'Sundew',
            'origin_city': 'Willowtown',
            'origin_country': 'Canada',
            'temperature': 18.21,
            'last_watered': '2025-06-03 09:14:12.000000+00:00',
            'soil_moisture': 88.9,
            'recording_taken': '2025-06-03 09:15:00.000000+00:00',
            'botanist_name': 'Dr. Alice Greene',
            'botanist_email': 'alice.greene@lnhm.co.uk',
            'botanist_phone': '+1445982713'
        },
        {
            'plant_id': 3,
            'name': 'Pitcher plant',
            'origin_city': 'Rainford',
            'origin_country': 'Malaysia',
            'temperature': 27.45,
            'last_watered': '2025-06-01 18:20:05.000000+00:00',
            'soil_moisture': 73.5,
            'recording_taken': '2025-06-01 18:25:10.000000+00:00',
            'botanist_name': 'Carlos Rivera',
            'botanist_email': 'carlos.rivera@lnhm.co.uk',
            'botanist_phone': '+6038291010'
        },
        {
            'plant_id': 4,
            'name': 'Bladderwort',
            'origin_city': 'Stammside',
            'origin_country': 'Albania',
            'temperature': 14.5,
            'last_watered': '2025-06-02 12:00:00.000000+00:00',
            'soil_moisture': 80.1,
            'recording_taken': '2025-06-02 12:15:00.000000+00:00',
            'botanist_name': 'Kenneth Buckridge',
            'botanist_email': 'kenneth.buckridge@lnhm.co.uk',
            'botanist_phone': '+7639148635'
        },
        {
            'plant_id': 5,
            'name': 'Butterwort',
            'origin_city': 'Willowtown',
            'origin_country': 'Canada',
            'temperature': 16.9,
            'last_watered': '2025-06-03 14:22:30.000000+00:00',
            'soil_moisture': 85.0,
            'recording_taken': '2025-06-03 14:30:00.000000+00:00',
            'botanist_name': 'Dr. Alice Greene',
            'botanist_email': 'alice.greene@lnhm.co.uk',
            'botanist_phone': '+1445982713'
        },
        {
            'plant_id': 6,
            'name': 'Waterwheel plant',
            'origin_city': 'Ipoh',
            'origin_country': 'Malaysia',
            'temperature': 26.3,
            'last_watered': '2025-06-01 08:10:45.000000+00:00',
            'soil_moisture': 78.2,
            'recording_taken': '2025-06-01 08:15:00.000000+00:00',
            'botanist_name': 'Carlos Rivera',
            'botanist_email': 'carlos.rivera@lnhm.co.uk',
            'botanist_phone': '+6038291010'
        },
        {
            'plant_id': 7,
            'name': 'Cobra lily',
            'origin_city': 'Fern Hollow',
            'origin_country': 'USA',
            'temperature': 19.0,
            'last_watered': '2025-06-04 07:45:00.000000+00:00',
            'soil_moisture': 90.0,
            'recording_taken': '2025-06-04 08:00:00.000000+00:00',
            'botanist_name': 'Maria Thompson',
            'botanist_email': 'maria.thompson@lnhm.co.uk',
            'botanist_phone': '+1234567890'
        },
        {
            'plant_id': 8,
            'name': 'Australian pitcher plant',
            'origin_city': 'Perth',
            'origin_country': 'Australia',
            'temperature': 22.5,
            'last_watered': '2025-06-02 10:30:00.000000+00:00',
            'soil_moisture': 83.5,
            'recording_taken': '2025-06-02 10:45:00.000000+00:00',
            'botanist_name': 'Dr. Alice Greene',
            'botanist_email': 'alice.greene@lnhm.co.uk',
            'botanist_phone': '+1445982713'
        }
    ]

    plants_data = pd.DataFrame(plants_data)
    with get_connection() as db_connection:
        load_data(plants_data, db_connection)
