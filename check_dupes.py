import os
import sys

# Add current directory to path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from sqlalchemy import text
from backend.database import engine

def check_duplicates():
    try:
        with engine.connect() as conn:
            # Query to find name+phone duplicates treating NULL as a value
            # COALESCE is more standard than IFNULL
            query = """
            SELECT name, phone, COUNT(*) as count 
            FROM records 
            GROUP BY name, COALESCE(phone, '')
            HAVING COUNT(*) > 1
            """
            
            result = conn.execute(text(query))
            dupes = result.fetchall()
            
            total_dupe_sets = len(dupes)
            total_excess_rows = sum(d[2] - 1 for d in dupes)
            
            print(f"Duplicate Check Results:")
            print(f"------------------------")
            print(f"Total sets of duplicates found: {total_dupe_sets}")
            print(f"Total excess rows to remove:   {total_excess_rows}")
            
            if total_dupe_sets > 0:
                print("\nTop 10 duplicates:")
                for i, row in enumerate(dupes[:10]):
                    name = row[0]
                    phone = row[1]
                    count = row[2]
                    p_val = phone if phone else "NULL/None"
                    print(f"{i+1}. {name} | Phone: {p_val} | Occurrences: {count}")
                    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_duplicates()
