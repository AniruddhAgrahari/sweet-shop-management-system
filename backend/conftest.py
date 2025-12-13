import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from main import app
from database import get_session
from models import Sweet, User

# Import pytest, Session, SQLModel, create_engine, StaticPool
# Import app from main, get_session from database
# Import TestClient

# Create a fixture "session" that:
#   1. Creates an in-memory sqlite engine with StaticPool
#   2. Creates all tables (SQLModel.metadata.create_all)
#   3. Yields a session linked to this engine
#   4. Drops all tables after the test

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

# Create a fixture "client" that:
#   1. Uses app.dependency_overrides to replace get_session with a lambda yielding the fixture session
#   2. Yields TestClient(app)
#   3. Clears dependency_overrides

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
