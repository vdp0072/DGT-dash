import sqlite3
from sqlite3 import Connection
from contextlib import contextmanager

DB_PATH = "dgt.db"

@contextmanager
def get_db():
    """Context manager for thread-safe database connections."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_db_connection() -> Connection:
    """Legacy function - creates a new connection (caller must close)."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
