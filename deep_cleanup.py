import os
import sys

# Add current directory to path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from sqlalchemy import text
from backend.database import engine

def run_cleanup():
    try:
        with engine.connect() as conn:
            # Get count before
            before = conn.execute(text("SELECT COUNT(*) FROM records")).scalar()
            
            # Update all NULL phones to '' to enable uniqueness check
            conn.execute(text("UPDATE records SET phone = '' WHERE phone IS NULL"))
            conn.commit()
            
            # Delete duplicates treating NULL phone as empty string
            # We use a subquery to find IDs to keep (the max ID for each name/phone pair)
            # and delete everything else.
            cleanup_sql = """
            DELETE FROM records 
            WHERE id NOT IN (
                SELECT MAX(id) 
                FROM records 
                GROUP BY name, phone
            )
            """
            conn.execute(text(cleanup_sql))
            conn.commit()
            
            # Get count after
            after = conn.execute(text("SELECT COUNT(*) FROM records")).scalar()
            
            print(f"Cleanup Successful:")
            print(f"Rows before: {before}")
            print(f"Rows after:  {after}")
            print(f"Removed:     {before - after}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_cleanup()
