from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import Sweet

# Import FastAPI, SQLModel, engine from database, and the models
# Create a lifespan context manager that creates the database tables on startup
# Initialize the FastAPI app with the lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sweet Shop API"}

# Create a POST endpoint "/sweets/" that takes a sweet: Sweet and a session: Session = Depends(get_session)
# Add the sweet to the session, commit, refresh, and return the sweet
@app.post("/sweets/", response_model=Sweet)
def create_sweet(sweet: Sweet, session: Session = Depends(get_session)):
    session.add(sweet)
    session.commit()
    session.refresh(sweet)
    return sweet