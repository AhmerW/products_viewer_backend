import uuid
from sqlmodel import Session, select
from app.models.product_model import Product, ProductCreate

def create_item(*, session: Session, item_in: ProductCreate) -> Product:
    db_item = Product.model_validate(item_in)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item