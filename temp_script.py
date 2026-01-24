
import sqlite3
import pandas as pd
import random

def generate_temp_data():
    db_path = "d:/DGT_dash/dgt.db"
    output_path = "d:/DGT_dash/extracted_data_250.xlsx"
    
    # 1. Connect to DB and extract 250 rows
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM records LIMIT 250"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("No data found in database.")
        return

    # 2. Add/Overwrite columns as requested
    constituencies = ["Kothrud", "Baner", "Pimpri", "Kondwa"]
    
    def random_phone():
        return "9" + "".join([str(random.randint(0, 9)) for _ in range(9)])

    df['phone'] = [random_phone() for _ in range(len(df))]
    df['city'] = "Pune"
    df['constituency'] = [random.choice(constituencies) for _ in range(len(df))]
    
    # 3. Save as XLSX
    df.to_excel(output_path, index=False)
    print(f"Successfully saved 250 rows to {output_path}")

if __name__ == "__main__":
    generate_temp_data()
