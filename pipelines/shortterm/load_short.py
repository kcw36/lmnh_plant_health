"""Modules for loading data to SQL Server DB."""

from logging import getLogger
from os import environ as ENV

import pandas as pd
from pandas import DataFrame

from dotenv import load_dotenv
from pyodbc import connect, Connection


def get_connection() -> Connection:
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


def insert_origin_country(data: DataFrame, conn: Connection):
    """Insert data into `origin_country` table."""
    logger = getLogger(__name__)
    logger.info("Inserting into origin_country...")

    existing_countries_query = "SELECT name FROM origin_country;"
    insert_query = """INSERT INTO origin_country (name) VALUES (?);"""

    unique_countries = data["origin_country"].unique()
    countries_in_db = pd.read_sql(existing_countries_query, conn)[
        "name"].to_list()
    countries_to_insert = [
        country for country in unique_countries if country not in countries_in_db
    ]

    if not countries_to_insert:
        logger.info("No new countries to insert.")
        return

    with conn.cursor() as curs:
        curs.executemany(insert_query, [(country,)
                         for country in countries_to_insert])
        conn.commit()
        logger.info(f"Inserted {len(countries_to_insert)} new countries.")


def insert_botanist(data: DataFrame, conn: Connection):
    """Insert data into `botanist` table."""
    logger = getLogger(__name__)
    logger.info("Inserting into botanist...")

    existing_botanist_query = "SELECT name, email, phone FROM botanist;"
    insert_query = "INSERT INTO botanist (name, email, phone) VALUES (?, ?, ?);"

    unique_botanists = data[["botanist_name",
                             "botanist_email", "botanist_phone"]].drop_duplicates()
    unique_botanists = set(unique_botanists.itertuples(index=False, name=None))

    botanist_in_db = pd.read_sql(existing_botanist_query, conn)
    botanist_in_db = set(botanist_in_db.itertuples(index=False, name=None))

    botanist_to_insert = list(unique_botanists - botanist_in_db)

    if not botanist_to_insert:
        logger.info("No new botanists to insert.")
        return

    with conn.cursor() as curs:
        curs.executemany(insert_query, botanist_to_insert)
        conn.commit()
        logger.info(f"Inserted {len(botanist_to_insert)} new botanists.")


def insert_origin_city(data: DataFrame, conn: Connection):
    """Insert data into `origin_city` table."""
    logger = getLogger(__name__)
    logger.info("Inserting into origin_city...")

    country_query = "SELECT country_id, name FROM origin_country"
    existing_city_query = "SELECT name, country_id FROM origin_city"
    insert_query = "INSERT INTO origin_city (name, country_id) VALUES (?, ?)"

    unique_cities = data[["origin_city", "origin_country"]
                         ].drop_duplicates()

    countries_in_db = pd.read_sql(country_query, conn)
    countries_in_db = dict(
        zip(countries_in_db["name"], countries_in_db["country_id"]))

    unique_cities["country_id"] = unique_cities["origin_country"].map(
        countries_in_db)
    unique_cities = unique_cities.dropna(subset=["country_id"])
    unique_cities = set(unique_cities[["origin_city", "country_id"]].itertuples(
        index=False, name=None))

    cities_in_db = pd.read_sql(existing_city_query, conn)
    cities_in_db = set(cities_in_db.itertuples(index=False, name=None))

    cities_to_insert = list(unique_cities - cities_in_db)

    if not cities_to_insert:
        logger.info("No new cities to insert.")
        return

    with conn.cursor() as curs:
        curs.executemany(insert_query, cities_to_insert)
        conn.commit()
        logger.info(f"Inserted {len(cities_to_insert)} new cities.")


def insert_plant(data: DataFrame, conn: Connection):
    """Insert data into `plant` table."""
    logger = getLogger(__name__)
    logger.info("Inserting into plant...")

    city_country_query = """
            SELECT origin_city.city_id,
              origin_city.name AS city_name,
              origin_country.country_id,
              origin_country.name AS country_name 
            FROM origin_city  
            JOIN origin_country ON origin_city.country_id = origin_country.country_id
    """

    existing_plant_query = "SELECT plant_id FROM plant"
    insert_query = "INSERT INTO plant (plant_id, name, city_id) VALUES (?, ?, ?)"

    unique_plants = data[["plant_id", "name", "origin_city",
                          "origin_country"]].drop_duplicates()

    city_country = pd.read_sql(city_country_query, conn)
    city_country = {
        (row.city_name, row.country_name): row.city_id
        for row in city_country.itertuples(index=False)
    }

    unique_plants["city_id"] = unique_plants.apply(
        lambda row: city_country.get((row.origin_city, row.origin_country)), axis=1

    )
    plants_in_db = pd.read_sql(existing_plant_query, conn)[
        "plant_id"].to_list()

    plants_to_insert = unique_plants[~unique_plants["plant_id"].isin(
        plants_in_db)]
    plants_to_insert = list(plants_to_insert[["plant_id", "name", "city_id"]].itertuples(
        index=False, name=None))

    if not plants_to_insert:
        logger.info("No new plants to insert.")
        return

    with conn.cursor() as curs:
        curs.executemany(insert_query, plants_to_insert)
        conn.commit()
        logger.info(f"Inserted {len(plants_to_insert)} new plants.")


def insert_botanist_plant(data: DataFrame, conn: Connection):
    """Insert data into `botanist_plant` table."""
    logger = getLogger(__name__)
    logger.info("Inserting into botanist_plant...")

    botanist_id_email_query = "SELECT botanist_id, email FROM botanist"
    plant_id_query = "SELECT plant_id FROM plant"
    botanist_plant_query = "SELECT plant_id, botanist_id FROM botanist_plant"

    botanist_id_email = pd.read_sql(botanist_id_email_query, conn)
    botanist_id_email = dict(
        zip(botanist_id_email["email"], botanist_id_email["botanist_id"]))

    plant_id = pd.read_sql(plant_id_query, conn)["plant_id"].to_list()

    botanist_plants = data[["plant_id", "botanist_email"]].drop_duplicates()
    botanist_plants["botanist_id"] = botanist_plants["botanist_email"].map(
        botanist_id_email)

    botanist_plant_in_db = pd.read_sql(botanist_plant_query, conn)

    print(botanist_plant_in_db)


def insert_record(data: DataFrame):
    """Insert data into `record` table."""
    logger = getLogger(__name__)
    logger.info("Inserting into record...")
    pass


if __name__ == "__main__":
    load_dotenv()

    data = [
        {
            'plant_id': 1,
            'name': 'Venus flytrap',
            'origin_city': 'Stammside',
            'origin_country': 'Albania',
            'temperature': 13.77,
            'last_watered': '2025-06-04 13:51:41+00:00',
            'soil_moisture': 92.33,
            'recording_taken': '2025-06-04 16:10:03.580000+00:00',
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
            'last_watered': '2025-06-03 09:14:12+00:00',
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
            'last_watered': '2025-06-01 18:20:05+00:00',
            'soil_moisture': 73.5,
            'recording_taken': '2025-06-01 18:25:10.100000+00:00',
            'botanist_name': 'Carlos Rivera',
            'botanist_email': 'carlos.rivera@lnhm.co.uk',
            'botanist_phone': '+6038291010'
        }
    ]

    data = pd.DataFrame(data)

    print(data)
    with get_connection() as conn:
        # insert_origin_country(data, conn)
        # insert_botanist(data, conn)
        # insert_origin_city(data, conn)
        #  insert_plant(data, conn)
        insert_botanist_plant(data, conn)
