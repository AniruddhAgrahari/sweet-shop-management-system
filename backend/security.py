from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

# Define a SECRET_KEY = "supersecretkey" (in real life, this comes from env vars)
# Define ALGORITHM = "HS256"

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

# Import PassLib CryptContext
# Create a pwd_context using "bcrypt", deprecated="auto"

# NOTE: The installed `bcrypt` backend in this environment raises `ValueError` during
# PassLib's bcrypt backend self-check (it hashes a >72-byte test secret).
# Using `pbkdf2_sha256` avoids that backend issue while still providing secure hashing.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Define a function get_password_hash(password) that returns the hashed password
# Define a function verify_password(plain_password, hashed_password) that returns True if they match

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


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
