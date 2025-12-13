from typing import Optional
from sqlmodel import SQLModel, Field

# Import SQLModel, Field, and Optional
# Define class Sweet(SQLModel, table=True):
#   id: Optional[int] primary key
#   name: str, category: str, price: float, quantity: int
# Define class User(SQLModel, table=True):
#   id: Optional[int] primary key
#   username: str unique, password_hash: str, role: str default "customer"

class Sweet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    price: float
    quantity: int

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    password_hash: str
    role: str = Field(default="customer")

class UserRegister(SQLModel):
    username: str
    password: str
    role: str = "customer"
