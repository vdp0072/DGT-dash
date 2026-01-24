import sqlite3

def run_cleanup():
    db_path = "d:/DGT_dash/dgt.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get count before
    cursor.execute("SELECT COUNT(*) FROM records")
    before = cursor.fetchone()[0]
    
    # Update all NULL phones to '' to enable uniqueness check
    cursor.execute("UPDATE records SET phone = '' WHERE phone IS NULL")
    conn.commit()
    
    # Delete duplicates treating NULL phone as empty string
    cursor.execute("""
    DELETE FROM records 
    WHERE id NOT IN (
        SELECT MAX(id) 
        FROM records 
        GROUP BY name, phone
    )
    """)
    
    conn.commit()
    
    # Get count after
    cursor.execute("SELECT COUNT(*) FROM records")
    after = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Cleanup Successful:")
    print(f"Rows before: {before}")
    print(f"Rows after:  {after}")
    print(f"Removed:     {before - after}")

if __name__ == "__main__":
    run_cleanup()
