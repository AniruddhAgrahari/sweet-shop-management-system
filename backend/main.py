from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import Sweet

# Import FastAPI, Depends, SQLModel, Session, select, asynccontextmanager
# Import create_db_and_tables, get_session from database
# Import Sweet from models

# Define lifespan(app: FastAPI): create_db_and_tables() on startup
# Initialize app = FastAPI(lifespan=lifespan)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Create POST /sweets/ endpoint:
#   Takes sweet: Sweet, session: Session = Depends(get_session)
#   Adds sweet to session, commits, refreshes, returns sweet

@app.post("/sweets/", response_model=Sweet)
def create_sweet(sweet: Sweet, session: Session = Depends(get_session)):
    session.add(sweet)
    session.commit()
    session.refresh(sweet)
    return sweet

# Create GET /sweets/ endpoint:
#   Takes session: Session = Depends(get_session)
#   Returns list of sweets using session.exec(select(Sweet)).all()

@app.get("/sweets/", response_model=list[Sweet])
def read_sweets(session: Session = Depends(get_session)):
    return session.exec(select(Sweet)).all()