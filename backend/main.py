from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from .database import engine
from .models import Sweet, User

# Import FastAPI, SQLModel, engine from database, and the models
# Create a lifespan context manager that creates the database tables on startup
# Initialize the FastAPI app with the lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)