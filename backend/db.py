import os

import psycopg2
from dotenv import load_dotenv


def get_connection():
    """Create and return a new database connection."""
    load_dotenv()

    return psycopg2.connect(
        user=os.getenv("GETAMPEDVIVE_USER"),
        password=os.getenv("GETAMPEDVIVE_PASSWORD"),
        host=os.getenv("GETAMPEDVIVE_HOST"),
        port=os.getenv("GETAMPEDVIVE_PORT"),
        dbname=os.getenv("GETAMPEDVIVE_DBNAME"),
    )
