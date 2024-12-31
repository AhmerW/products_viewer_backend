from typing import Optional, List
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models.user_model import UserRoles
from app.models.default_model import *

router = APIRouter(prefix="/defaults", tags=["defaults"])

def get_default(session: SessionDep) -> DefaultModel:
    statement = select(DefaultModel).where(DefaultModel.id == 0)
    default = session.exec(statement).first()
    if not default:
        print("Default not found")
        default = DefaultModel(id=0, fields=[], headers=[], labels=[])

    return default

def save_default(session: SessionDep, default: DefaultModel) -> DefaultModel:
    session.add(default)
    session.commit()
    session.refresh(default)
    return default

# retrieve all defaults (id = 1)
@router.get("", response_model=DefaultFieldAndHeaderResponse)
@router.get("/", response_model=DefaultFieldAndHeaderResponse)
async def read_defaults(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 30,
):
    if not current_user.roles:  
        raise HTTPException(status_code=403, detail="Forbidden")

    default = get_default(session)
    return default


# get labels
@router.get("/labels/", response_model=DefaultLabelsResponse)
@router.get("/labels", response_model=DefaultLabelsResponse)
async def read_default_labels(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 30,
):
    if not current_user.roles:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    default = get_default(session)
    return default

# update default fields
@router.put("/fields/", response_model=DefaultFieldAndHeaderResponse)
@router.put("/fields", response_model=DefaultFieldAndHeaderResponse)
async def update_default_fields(
    session: SessionDep,
    current_user: CurrentUser,

    fields: DefaultFieldsResponse,
):
    if not current_user.roles:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    default = get_default(session)
    default.fields = fields.model_dump().get("fields")
 
    return save_default(session, default)


# update default headers
@router.put("/headers/", response_model=DefaultHeadersResponse)
@router.put("/headers", response_model=DefaultHeadersResponse)
async def update_default_headers(
    session: SessionDep,
    current_user: CurrentUser,
    headers: DefaultHeadersResponse,
):
    if not current_user.roles: 
        raise HTTPException(status_code=403, detail="Forbidden")
    
    default = get_default(session)
    default.headers = headers.model_dump().get("headers")
 
    return save_default(session, default)


# update default labels
@router.put("/labels/", response_model=DefaultLabelsResponse)
@router.put("/labels", response_model=DefaultLabelsResponse)
async def update_default_labels(
    session: SessionDep,
    current_user: CurrentUser,
    labels: DefaultLabelsResponse,
):
    if not current_user.roles: 
        raise HTTPException(status_code=403, detail="Forbidden")
    
    default = get_default(session)
    default.labels = labels.model_dump().get("labels")
 
    return save_default(session, default)
