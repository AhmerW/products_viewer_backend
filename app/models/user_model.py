from enum import Enum
from typing import List

from sqlmodel import SQLModel, Field , Column, JSON   

class UserRoles(str, Enum):
    admin = "admin"
    viewer = "viewer"
    editor = "editor"


class UserBase(SQLModel):
    username: str = Field(index=True)
    is_active: bool = True
    roles: List[UserRoles] = Field(default=[], sa_column=Column(JSON))

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

class UserPublic(UserBase):
    id: int 

class UserCreate(UserBase):
    password: str = Field()