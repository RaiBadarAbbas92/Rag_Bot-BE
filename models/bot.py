from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import uuid4
class Chatbot(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    description: str
    tone: str
    personality: str
    index_file_path: str
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
