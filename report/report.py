"""Report script that notifies botanist if there is something wrong with a plant."""

from dotenv import load_dotenv
from data import get_connection

if __name__ == "__main__":
    load_dotenv()
    with get_connection() as conn:
        print("Connected successfully")
