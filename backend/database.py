import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Support DATABASE_URL from env or fallback to local sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dgt.db")

# Fix for Render/Postgres: change postgres:// to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Mask URL for safe logging
masked_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
engine_name = engine.dialect.name

if engine_name == "sqlite":
    print(f"⚠️  ACTIVE DATABASE: SQLite (EPHEMERAL — DATA WILL NOT PERSIST)")
    print(f"🔗 Database connection: {masked_url}")
else:
    print(f"✅ ACTIVE DATABASE: PostgreSQL (PERSISTENT)")
    print(f"🔗 Database connection: {masked_url}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# engine_name is now the primary way to check database dialect.
