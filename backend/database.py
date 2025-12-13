from sqlmodel import SQLModel, create_engine, Session

sqlite_file_name = "sweetshop.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def get_session():
    with Session(engine) as session:
        yield session
