from sqlalchemy import text
from backend.database import engine, is_sqlite
import bcrypt

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_db():
    print(f"Initializing database schema...")

    with engine.connect() as conn:
        pk_type = "INTEGER PRIMARY KEY" if is_sqlite() else "SERIAL PRIMARY KEY"
        
        # Users Table
        conn.execute(text(f'''
        CREATE TABLE IF NOT EXISTS users (
            id {pk_type},
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''))

        # Ingestion Logs Table - now linked by username for robustness
        conn.execute(text(f'''
        CREATE TABLE IF NOT EXISTS ingestion_logs (
            id {pk_type},
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
        conn.execute(text(f'''
        CREATE TABLE IF NOT EXISTS records (
            id {pk_type},
            name TEXT NOT NULL,
            fathers_name TEXT,
            age INTEGER,
            gender TEXT,
            area TEXT,
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
        conn.execute(text(f'''
        CREATE TABLE IF NOT EXISTS access_logs (
            id {pk_type},
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''))

        # Indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_records_search ON records(name, city, area)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_records_phone ON records(phone)"))

        # Seed System Users
        default_users = [
            {"u": "admin", "p": "admin123", "r": "admin"},
            {"u": "demo", "p": "demo123", "r": "user"},
            {"u": "superuser", "p": "super123", "r": "superuser"}
        ]
        
        for user_data in default_users:
            try:
                result = conn.execute(
                    text("SELECT 1 FROM users WHERE username = :u"), 
                    {"u": user_data["u"]}
                ).fetchone()
                
                if not result:
                    password_hash = get_password_hash(user_data["p"])
                    conn.execute(
                        text("INSERT INTO users (username, password_hash, role) VALUES (:u, :p, :r)"),
                        {"u": user_data["u"], "p": password_hash, "r": user_data["r"]}
                    )
                    print(f"Seeded user: {user_data['u']} ({user_data['r']})")
                else:
                    print(f"User already exists: {user_data['u']}")
            except Exception as e:
                print(f"Error seeding user {user_data['u']}: {e}")

        conn.commit()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
