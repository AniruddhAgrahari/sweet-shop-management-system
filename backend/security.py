import os
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get SECRET_KEY from environment variable (required for production)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey-change-in-production")
ALGORITHM = "HS256"

# Import PassLib CryptContext
# Create a pwd_context using "bcrypt", deprecated="auto"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define a function get_password_hash(password) that returns the hashed password
# Define a function verify_password(plain_password, hashed_password) that returns True if they match

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    # Copy the data to a new dict
    to_encode = data.copy()

    # If expires_delta is set, expire = datetime.utcnow() + expires_delta
    # Else, expire = datetime.utcnow() + timedelta(minutes=15)
    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    # Add "exp": expire to the dict
    to_encode.update({"exp": expire})

    # Return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
