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

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
