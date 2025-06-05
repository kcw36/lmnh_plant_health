"""Script to run the full short term pipeline."""

from transform_short import transform_data
from load_short import (
    get_connection,
    insert_origin_country,
    insert_botanist,
    insert_origin_city,
    insert_plant,
    insert_botanist_plant
)


def run_pipeline():
    """Runs the pipeline."""

    clean_df = transform_data()

    with get_connection as conn:
        insert_origin_country(clean_df, conn)
        insert_botanist(clean_df, conn)
        insert_origin_city(clean_df, conn)
        insert_plant(clean_df, conn)
        insert_botanist_plant(clean_df, conn)


if __name__ == "__main__":
    run_pipeline()
