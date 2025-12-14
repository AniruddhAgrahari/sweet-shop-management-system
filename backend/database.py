import os
from sqlalchemy import text
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
# For local development with SQLite: sqlite:///./sweetshop.db
# For production with PostgreSQL: postgresql://user:password@host:port/database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sweetshop.db")

# Configure connection arguments based on database type
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create engine with connection pooling for PostgreSQL
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,         # Number of connections to maintain
        max_overflow=10      # Max connections beyond pool_size
    )
else:
    engine = create_engine(DATABASE_URL, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

def _ensure_sweets_image_url_column() -> None:
    """Ensure the `sweet` table has an `image_url` column.

    SQLModel won't auto-migrate existing tables when models change, so
    we do a tiny, safe migration on startup.
    """

    with engine.connect() as connection:
        # Check database type and use appropriate query
        if DATABASE_URL.startswith("sqlite"):
            # SQLite: Use PRAGMA to check columns
            columns = connection.execute(text("PRAGMA table_info('sweet')")).fetchall()
            column_names = {row[1] for row in columns}  # row[1] is column name
        else:
            # PostgreSQL: Query information_schema
            result = connection.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'sweet'"
            )).fetchall()
            column_names = {row[0] for row in result}

        if "image_url" not in column_names:
            connection.execute(text("ALTER TABLE sweet ADD COLUMN image_url VARCHAR"))
            connection.commit()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _ensure_sweets_image_url_column()
