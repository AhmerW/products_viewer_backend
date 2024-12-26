from typing import List

from sqlmodel import SQLModel, Field, Column, JSON

from app.models.field_model import FieldBaseModel   
from app.models.product_model import ProductLabelModel


class DefaultModel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    fields: List[FieldBaseModel] = Field(default=[], sa_column=Column(JSON))
    headers: List[FieldBaseModel] = Field(default=[], sa_column=Column(JSON))
    labels: List[ProductLabelModel] = Field(default=[], sa_column=Column(JSON))

class DefaultFieldsResponse(SQLModel):
    fields: List[FieldBaseModel]

class DefaultHeadersResponse(SQLModel):
    headers: List[FieldBaseModel]

class DefaultLabelsResponse(SQLModel):
    labels: List[ProductLabelModel]

class DefaultFieldAndHeaderResponse(SQLModel):
    fields: List[FieldBaseModel]
    headers: List[FieldBaseModel]


class DefaultResponse(SQLModel):
    fields: List[FieldBaseModel]
    headers: List[FieldBaseModel]
    labels: List[ProductLabelModel]