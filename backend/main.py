from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import Sweet, User, UserRegister, AdminInit, AdminPasswordReset
from security import get_password_hash, verify_password, create_access_token
from security import SECRET_KEY
from auth_dependencies import get_current_admin

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

# Add CORS middleware to allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://sweet-shop-management-system-mocha.vercel.app",  # Vercel production frontend
        "https://*.vercel.app",  # Allow all Vercel deployments
    ],  # Allow local and production frontends
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


def _default_image_url_for_category(category: str | None) -> str | None:
    if not category:
        return None

    normalized = category.strip().lower().replace(" ", "_")
    mapping: dict[str, str] = {
        # Defaults point to assets in `frontend/public/sweets/`
        "indian": "/sweets/gulab_jamun.jpg",
        "chocolate": "/sweets/dark_chocolate_bark.jpg",
        "candy": "/sweets/gummy_bears.jpg",
        "cake": "/sweets/red_velvet_cupcake.webp",
        "cookie": "/sweets/chocochip_cookies.jpg",
        "cookies": "/sweets/chocochip_cookies.jpg",
        "ice_cream": "/sweets/ice_cream.svg",
        "ice-cream": "/sweets/ice_cream.svg",
        "icecream": "/sweets/ice_cream.svg",
    }
    return mapping.get(normalized)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sweet Shop API"}

# Create POST /sweets/ endpoint:
#   Takes sweet: Sweet, session: Session = Depends(get_session)
#   Adds sweet to session, commits, refreshes, returns sweet

@app.post("/sweets/", response_model=Sweet, status_code=201)
def create_sweet(
    sweet: Sweet, 
    session: Session = Depends(get_session),
    admin: Any = Depends(get_current_admin)
):
    if not sweet.image_url:
        sweet.image_url = _default_image_url_for_category(sweet.category)
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

@app.get("/sweets/search")
def search_sweets(
    name: str = None,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    session: Session = Depends(get_session)
):
    # Start with a base select statement
    statement = select(Sweet)

    # Apply filters based on query parameters
    if name:
        # Use ilike for case-insensitive partial match
        statement = statement.where(Sweet.name.ilike(f"%{name}%"))
    
    if category:
        categories = [c.strip() for c in category.split(",") if c.strip()]
        if len(categories) == 1:
            statement = statement.where(Sweet.category.ilike(f"%{categories[0]}%"))
        elif categories:
            statement = statement.where(or_(*[Sweet.category.ilike(f"%{c}%") for c in categories]))

    if min_price is not None:
        statement = statement.where(Sweet.price >= min_price)

    if max_price is not None:
        statement = statement.where(Sweet.price <= max_price)
        
    # Execute the query and fetch all results
    sweets = session.exec(statement).all()
    
    return sweets

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
def update_sweet(
    sweet_id: int, 
    sweet_update: Sweet, 
    session: Session = Depends(get_session),
    admin: Any = Depends(get_current_admin)
):
    sweet = session.get(Sweet, sweet_id)
    if not sweet:
        raise HTTPException(status_code=404, detail="Sweet not found")
    
    sweet_data = sweet_update.model_dump(exclude_unset=True)
    for key, value in sweet_data.items():
        setattr(sweet, key, value)

    if not sweet.image_url:
        sweet.image_url = _default_image_url_for_category(sweet.category)
        
    session.add(sweet)
    session.commit()
    session.refresh(sweet)
    return sweet

# Create a DELETE endpoint "/sweets/{sweet_id}"
# Get the sweet by ID. If not found, raise HTTPException(404)
# Delete the sweet from session and commit
# Return {"ok": True}

@app.delete("/sweets/{sweet_id}")
def delete_sweet(
    sweet_id: int, 
    session: Session = Depends(get_session),
    admin: Any = Depends(get_current_admin)
):
    sweet = session.get(Sweet, sweet_id)
    if not sweet:
        raise HTTPException(status_code=404, detail="Sweet not found")
    session.delete(sweet)
    session.commit()
    return {"ok": True}

@app.post("/sweets/{sweet_id}/purchase")
def purchase_sweet(
    sweet_id: int,
    quantity: int = 1,
    session: Session = Depends(get_session),
):
    sweet = session.get(Sweet, sweet_id)
    if not sweet:
        raise HTTPException(status_code=404, detail="Sweet not found")

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    if sweet.quantity <= 0:
        raise HTTPException(status_code=400, detail="Out of stock")

    if quantity > sweet.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    sweet.quantity -= quantity
    session.add(sweet)
    session.commit()
    session.refresh(sweet)
    return {
        "message": "Purchase successful",
        "purchased_qty": quantity,
        "remaining_stock": sweet.quantity,
    }

# Create a POST endpoint "/auth/register"
# Takes user: User and session: Session
# Check if a user with the same username already exists. If so, raise HTTPException 400.
# Hash the user's password using get_password_hash
# Add the user to the session, commit, refresh, and return the user

@app.post("/auth/register", response_model=User)
def register_user(user_data: UserRegister, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # bcrypt only uses the first 72 bytes; truncate to avoid ValueError for longer inputs
    hashed_password = get_password_hash(user_data.password[:72])
    # Public registration is always customer; admins are created separately.
    user = User(username=user_data.username, email=user_data.email, password_hash=hashed_password, role="customer")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post("/auth/init-admin", response_model=User)
def init_admin(payload: AdminInit, session: Session = Depends(get_session)):
    """Create the very first admin account.

    Safety: this only works if there is currently no admin in the database.
    After an admin exists, further admin creation should be done by an admin-only route.
    """

    existing_admin = session.exec(select(User).where(User.role == "admin")).first()
    if existing_admin:
        raise HTTPException(status_code=403, detail="An admin already exists")

    existing_user = session.exec(select(User).where(User.username == payload.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(payload.password[:72])
    user = User(username=payload.username, password_hash=hashed_password, role="admin")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post("/auth/dev-reset-admin-password", response_model=User)
def dev_reset_admin_password(
    payload: AdminPasswordReset,
    session: Session = Depends(get_session),
    x_setup_key: str | None = Header(default=None, alias="X-Setup-Key"),
):
    """DEV-ONLY: reset an admin password.

    This is intended for local development when you don't know the admin password.
    It is protected by a setup key header that must match SECRET_KEY.
    """

    if not x_setup_key or x_setup_key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid setup key")

    user = session.exec(select(User).where(User.username == payload.username)).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=404, detail="Admin user not found")

    user.password_hash = get_password_hash(payload.new_password[:72])
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post("/auth/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Include role so frontend can detect admin vs customer.
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/sweets/{sweet_id}/restock")
def restock_sweet(
    sweet_id: int, 
    quantity: int,
    session: Session = Depends(get_session),
    # THIS LINE PROTECTS THE ENDPOINT:
    admin: Any = Depends(get_current_admin)
):
    sweet = session.get(Sweet, sweet_id)
    if not sweet:
        raise HTTPException(status_code=404, detail="Sweet not found")
    
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    sweet.quantity += quantity
    session.add(sweet)
    session.commit()
    session.refresh(sweet)
    
    return {"message": f"Restocked {quantity} units.", "new_stock": sweet.quantity}