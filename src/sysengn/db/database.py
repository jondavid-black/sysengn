import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path("sysengn.db")


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Establishes a connection to the SQLite database."""
    path = db_path if db_path is not None else DB_PATH
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise


def init_db(db_path: str | Path | None = None) -> None:
    """Initialize the database with required tables."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()

        # Create Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                password_hash TEXT,
                roles TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()
