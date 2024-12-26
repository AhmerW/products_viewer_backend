from pydantic import BaseModel

class FieldBaseModel(BaseModel):
    key: str
    value: str
    note: str
    index: int
    is_divider: bool = False


class FieldModel(FieldBaseModel):
    is_divider: bool = False

class FieldDividerModel(FieldBaseModel):
    is_divider: bool = True


