from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel


# ---- Auth ----

class UserCreate(SQLModel):
    email: str
    password: str


class UserRead(SQLModel):
    id: int
    email: str
    # Notice: no hashed_password here. This is the whole point of having
    # separate schemas — we control exactly what leaves the API.


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# ---- Recipes ----

class RecipeCreate(SQLModel):
    title: str
    ingredients: str
    instructions: str


class RecipeUpdate(SQLModel):
    title: Optional[str] = None
    ingredients: Optional[str] = None
    instructions: Optional[str] = None


class RecipeRead(SQLModel):
    id: int
    title: str
    ingredients: str
    instructions: str
    created_at: datetime
    owner_id: int
