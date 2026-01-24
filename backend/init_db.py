from sqlalchemy import text
from backend.database import engine
import bcrypt

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_db():
    print(f"Initializing database schema...")

    with engine.connect() as conn:
        # Users Table
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''))

        # Ingestion Logs Table - now linked by username for robustness
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS ingestion_logs (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            uploaded_by_username TEXT NOT NULL,
            upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            total_rows INTEGER DEFAULT 0,
            inserted_rows INTEGER DEFAULT 0,
            rejected_rows INTEGER DEFAULT 0,
            rejection_reason TEXT
        )
        '''))

        # Records Table
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS records (
            id SERIAL PRIMARY KEY,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, phone)
        )
        '''))
        
        # Access Logs Table - now linked by username for robustness
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''))

        # Indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_records_search ON records(name, city, constituency)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_records_phone ON records(phone)"))

        # Seed Admin User
        admin_password = get_password_hash("admin123")
        try:
            result = conn.execute(text("SELECT 1 FROM users WHERE username = 'admin'")).fetchone()
            if not result:
                conn.execute(text("INSERT INTO users (username, password_hash, role) VALUES (:u, :p, :r)"),
                            {"u": "admin", "p": admin_password, "r": "admin"})
                conn.commit()
                print("Seeded admin user (admin/admin123)")
            else:
                print("Admin user already exists")
        except Exception as e:
            print(f"Seeding error: {e}")

        conn.commit()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
