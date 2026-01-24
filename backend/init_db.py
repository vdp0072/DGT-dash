import sqlite3
import os
import os
import bcrypt

DB_PATH = "dgt.db"

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_db():
    print(f"Initializing database at {os.path.abspath(DB_PATH)}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin', 'user', 'superuser')) NOT NULL DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Ingestion Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ingestion_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        uploaded_by_user_id INTEGER NOT NULL,
        upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT CHECK(status IN ('success', 'partial', 'failed')),
        total_rows INTEGER DEFAULT 0,
        inserted_rows INTEGER DEFAULT 0,
        rejected_rows INTEGER DEFAULT 0,
        rejection_reason TEXT,
        FOREIGN KEY(uploaded_by_user_id) REFERENCES users(id)
    )
    ''')

    # Records Table - Updated Schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        fathers_name TEXT,
        age INTEGER,
        gender TEXT,
        constituency TEXT,
        city TEXT,
        company TEXT,
        phone TEXT NOT NULL DEFAULT '',
        misc TEXT,
        source_file_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(source_file_id) REFERENCES ingestion_logs(id),
        UNIQUE(name, phone)
    )
    ''')
    
    # Access Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        details TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_search ON records(name, city, constituency)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_phone ON records(phone)")

    # Seed Admin User
    admin_password = get_password_hash("admin123")
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                       ("admin", admin_password, "admin"))
        print("Seeded admin user (admin/admin123)")
    except sqlite3.IntegrityError:
        print("Admin user already exists")

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
