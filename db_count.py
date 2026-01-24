import sqlite3

def print_db_stats():
    db_path = "d:/DGT_dash/dgt.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get column info
        cursor.execute("PRAGMA table_info(records)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM records")
        row_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"Database Stats for 'records' table:")
        print(f"-----------------------------------")
        print(f"Total Rows:    {row_count}")
        print(f"Total Columns: {len(columns)}")
        print(f"Columns:       {', '.join(columns)}")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print_db_stats()
