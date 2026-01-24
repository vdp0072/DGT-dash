import sqlite3

def update_role_constraint():
    db_path = "d:/DGT_dash/dgt.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Create new table with updated constraint
        cursor.execute('''
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'user', 'superuser')) NOT NULL DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 2. Copy data
        cursor.execute("INSERT INTO users_new SELECT * FROM users")
        
        # 3. Swap tables
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        
        # 4. Create the superuser
        from passlib.context import CryptContext
        pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')
        cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                       ('superuser', pwd.hash('super123'), 'superuser'))
        
        conn.commit()
        print("Successfully updated 'users' table and created user: superuser / super123")
        
    except Exception as e:
        conn.rollback()
        print(f"Failed to update table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_role_constraint()
