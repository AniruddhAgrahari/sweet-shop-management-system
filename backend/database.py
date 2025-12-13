from sqlalchemy import text
from sqlmodel import SQLModel, create_engine, Session

# Import SQLModel, create_engine, and Session
# Create a sqlite engine for "sqlite:///./sweetshop.db" with check_same_thread=False
# Define a function get_session that yields a Session(engine)
# Define a function create_db_and_tables that calls SQLModel.metadata.create_all(engine)

sqlite_file_name = "sweetshop.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

def _ensure_sweets_image_url_column() -> None:
    """Ensure the `sweet` table has an `image_url` column.

    SQLModel won't auto-migrate existing SQLite tables when models change, so
    we do a tiny, safe migration on startup.
    """

    with engine.connect() as connection:
        # SQLite table name for the Sweet model is typically "sweet".
        columns = connection.execute(text("PRAGMA table_info('sweet')")).fetchall()
        column_names = {row[1] for row in columns}  # row[1] is column name

        if "image_url" not in column_names:
            connection.execute(text("ALTER TABLE sweet ADD COLUMN image_url VARCHAR"))
            connection.commit()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _ensure_sweets_image_url_column()
