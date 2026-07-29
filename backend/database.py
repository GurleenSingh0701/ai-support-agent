import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import redis

# Load configurations from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@db:5432/autodesk_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Fix Render / Railway postgres:// URI format for SQLAlchemy 2.0 & psycopg3
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+psycopg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Setup SQLAlchemy
try:
    engine = create_engine(DATABASE_URL)
    # Test dialect initialization
    engine.dialect.dbapi
except Exception as e:
    print(f"Warning: PostgreSQL driver/database unavailable ({e}). Falling back to SQLite in-memory DB.")
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Setup Redis connection
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    # Ping to check if the connection is alive
    redis_client.ping()
    print("Successfully connected to Redis.")
except Exception as e:
    print(f"Warning: Failed to connect to Redis: {e}")
    redis_client = None

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
