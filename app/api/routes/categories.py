
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from sqlmodel import select


from app.api.deps import CurrentUser, SessionDep
from app.models.user_model import UserRoles
from app.models.category_model import Category, CategoryPublic, CategoriesPublic, CategoryCreate

router = APIRouter(prefix="/categories", tags=["category", "categories"])

@router.get("/", response_model=CategoriesPublic)
async def read_categories(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 30,
   
):
    # if not empty must either be viewer, editor, or admin..
    if not current_user.roles: 
        raise HTTPException(status_code=403, detail="Forbidden")
    

    statement = select(Category)
    # apply filters


    statement = statement.offset(skip).limit(limit)
    categories = session.exec(statement).all()

    return CategoriesPublic(categories= categories, count=len(categories))




@router.post("/", response_model=CategoryPublic)
async def create_category(session: SessionDep, current_user: CurrentUser, category_in: CategoryCreate):
    if (not UserRoles.admin in current_user.roles) and (not UserRoles.editor in current_user.roles):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    cat_data = jsonable_encoder(category_in)
    cat = Category(**cat_data)

    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat



@router.delete("/{id}", response_model=CategoryPublic)
async def delete_category(session: SessionDep, current_user: CurrentUser, id: int):
    if not UserRoles.editor in current_user.roles or not UserRoles.admin in current_user.roles:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    cat = session.get(Category, id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    
    session.delete(cat)
    session.commit()
    return cat