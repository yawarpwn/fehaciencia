# app/modules/auth/model.py
import uuid
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    username: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    full_name: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
