from typing import List, Optional
from enum import Enum

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from app.models.field_model import FieldBaseModel
from app.models.category_model import Category

class ProductFilterMode(str, Enum):
    label = "label"
    category = "category"
    field = "field"
    header = "header"
    field_and_header = "field_and_header"

class ProductOrderBy(str, Enum):
    asc = "asc" # recent
    desc = "desc" # oldest
    
class ProductFilter(BaseModel):
    filter_mode: ProductFilterMode
    filter_data: str
    filter_value: Optional[str] = None
    filter_value_any: bool = False
    filter_value_empty: bool = False

class ProductFilters(BaseModel):
    filters: List[ProductFilter]


class ProductLabelModel(BaseModel):
    title: str
    color: str

class ProductBase(SQLModel):                                                                                                    
    title: str = Field(index=True)
    fields: List[FieldBaseModel] = Field(default=[], sa_column=Column(JSON))
    headers: List[FieldBaseModel] = Field(default=[], sa_column=Column(JSON))
    labels: List[ProductLabelModel] = Field(default=[], sa_column=Column(JSON))
    category: int | None = Field(default=None, foreign_key="category.id")
    
 



class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)    
    category_obj: Optional[Category] = Relationship(back_populates="products")


class ProductCreate(ProductBase):
    pass

class ProductPublic(ProductBase):
    id: int 
    category_name: Optional[str] = None
    category_description: Optional[str] = None

class ProductsPublic(SQLModel):
    products: List[ProductPublic]
    count: int  


# docker run -d --name postgres-container -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -p 5432:5432 postgres:latest
