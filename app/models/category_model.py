from typing import List
from enum import Enum

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
  

class CategoryBase(SQLModel):
    name: str = Field(index=True)
    description: str = Field(index=True)


class Category(CategoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    products: List["Product"] = Relationship(back_populates="category_obj")


# public facing models (e.g id etc are a must)

class CategoryCreate(CategoryBase):
    pass

class CategoryPublic(CategoryBase):
    id: int

class CategoriesPublic(SQLModel):
    categories: List[CategoryPublic]
    count: int