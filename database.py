
import sqlite3
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent

# Database and schema file paths
DATABASE_PATH = BASE_DIR / "hemolink.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


# Connect to SQLite database
def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Enable foreign key constraints
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# Initialize database and create tables
def init_db():
    connection = get_db_connection()

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
            schema = file.read()

        connection.executescript(schema)
        connection.commit()

        print("HemoLink Pro database initialized successfully!")

    except sqlite3.Error as error:
        print("Database initialization failed:", error)
        raise

    finally:
        connection.close()


# Test database connection
def test_connection():
    connection = get_db_connection()

    try:
        result = connection.execute(
            "SELECT sqlite_version()"
        ).fetchone()

        print("SQLite version:", result[0])
        print("Database connection successful!")

    finally:
        connection.close()


if __name__ == "__main__":
    init_db()
    test_connection()
