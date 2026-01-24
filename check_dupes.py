import sqlite3

def check_duplicates():
    db_path = "d:/DGT_dash/dgt.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query to find name+phone duplicates treating NULL as a value
    # IFNULL(phone, '') allows us to group rows where both are NULL
    query = """
    SELECT name, phone, COUNT(*) as count 
    FROM records 
    GROUP BY name, IFNULL(phone, '')
    HAVING count > 1
    """
    
    cursor.execute(query)
    dupes = cursor.fetchall()
    
    total_dupe_sets = len(dupes)
    total_excess_rows = sum(d[2] - 1 for d in dupes)
    
    print(f"Duplicate Check Results:")
    print(f"------------------------")
    print(f"Total sets of duplicates found: {total_dupe_sets}")
    print(f"Total excess rows to remove:   {total_excess_rows}")
    
    if total_dupe_sets > 0:
        print("\nTop 10 duplicates:")
        for i, (name, phone, count) in enumerate(dupes[:10]):
            p_val = phone if phone else "NULL/None"
            print(f"{i+1}. {name} | Phone: {p_val} | Occurrences: {count}")
            
    conn.close()

if __name__ == "__main__":
    check_duplicates()
