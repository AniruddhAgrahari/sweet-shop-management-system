from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
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

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sweet Shop API"}

# Create POST /sweets/ endpoint:
#   Takes sweet: Sweet, session: Session = Depends(get_session)
#   Adds sweet to session, commits, refreshes, returns sweet

@app.post("/sweets/", response_model=Sweet, status_code=201)
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

# Create a GET endpoint "/sweets/{sweet_id}"
# Takes sweet_id: int and session: Session
# Uses session.get(Sweet, sweet_id) to find the sweet
# If not found, raise HTTPException status_code=404
# Returns the sweet
@app.get("/sweets/{sweet_id}")
def read_sweet(sweet_id: int, session: Session = Depends(get_session)):
    sweet = session.get(Sweet, sweet_id)
    if not sweet:
        raise HTTPException(status_code=404, detail="Sweet not found")
    return sweet

# Create a PUT endpoint "/sweets/{sweet_id}"
# Takes sweet_id: int, sweet_update: Sweet, session: Session
# Get the sweet by ID. If not found, raise HTTPException(404)
# Update the sweet attributes with sweet_update data
# Commit, refresh, and return the updated sweet

@app.put("/sweets/{sweet_id}", response_model=Sweet)
def update_sweet(sweet_id: int, sweet_update: Sweet, session: Session = Depends(get_session)):
    sweet = session.get(Sweet, sweet_id)
    if not sweet:
        raise HTTPException(status_code=404, detail="Sweet not found")
    
    sweet_data = sweet_update.model_dump(exclude_unset=True)
    for key, value in sweet_data.items():
        setattr(sweet, key, value)
        
    session.add(sweet)
    session.commit()
    session.refresh(sweet)
    return sweet

# Create a DELETE endpoint "/sweets/{sweet_id}"
# Get the sweet by ID. If not found, raise HTTPException(404)
# Delete the sweet from session and commit
# Return {"ok": True}

@app.delete("/sweets/{sweet_id}")
def delete_sweet(sweet_id: int, session: Session = Depends(get_session)):
    sweet = session.get(Sweet, sweet_id)
    if not sweet:
        raise HTTPException(status_code=404, detail="Sweet not found")
    session.delete(sweet)
    session.commit()
    return {"ok": True}