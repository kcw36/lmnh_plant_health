"""Report script that notifies botanist if there is something wrong with a plant."""

from dotenv import load_dotenv
from data import (get_connection,
                  get_latest_readings,
                  identify_critical_plants,
                  )

if __name__ == "__main__":
    load_dotenv()
    with get_connection() as conn:
        critical_plants = identify_critical_plants(conn)
        print(critical_plants)
