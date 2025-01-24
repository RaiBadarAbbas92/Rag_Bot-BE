from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional  # Keep the import for Optional
from pydantic import EmailStr

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: EmailStr
    hashed_password: str
    name: str
    phone_no: str
    country: str
    address: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
