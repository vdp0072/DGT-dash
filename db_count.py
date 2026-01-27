import os
import sys

# Add current directory to path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from sqlalchemy import text
from backend.database import engine

def print_db_stats():
    try:
        with engine.connect() as conn:
            # Row count
            row_count = conn.execute(text("SELECT COUNT(*) FROM records")).scalar()
            
            # Column detection (agnostic approach)
            # Fetch one row to see columns, or just use a fixed list if we know it
            result = conn.execute(text("SELECT * FROM records LIMIT 1"))
            columns = result.keys()
            
            print(f"Database Stats for 'records' table:")
            print(f"-----------------------------------")
            print(f"Total Rows:    {row_count}")
            print(f"Total Columns: {len(columns)}")
            print(f"Columns:       {', '.join(columns)}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print_db_stats()
