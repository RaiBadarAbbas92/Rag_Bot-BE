from sqlmodel import SQLModel
from pydantic import EmailStr
from pydantic import ConfigDict  # Import for Pydantic v2 configuration

class UserCreate(SQLModel):
    username: str
    email: EmailStr
    password: str
    name: str
    phone_no: str
    country: str
    address: str

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class UserResponse(SQLModel):
    id: int
    username: str
    email: EmailStr
    name: str
    country : str
    phone_no:str
    address : str


    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 compatibility for orm_mode

class Token(SQLModel):
    access_token: str
    token_type: str