from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session, select
from database import get_session
from models import User
from security import SECRET_KEY, ALGORITHM

# Import necessary FastAPI and JWT dependencies
# Define an OAuth2PasswordBearer instance for the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Define a function get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session))
# It must decode the token, get the username, and fetch the user object from the database.
# If anything fails (token invalid, user not found), raise HTTPException 401.
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

# Define a function get_current_admin(current_user: User = Depends(get_current_user))
# If current_user.role is not "admin", raise HTTPException 403 (Forbidden).
# Return current_user.
def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
