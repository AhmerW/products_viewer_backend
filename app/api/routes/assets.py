from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

from sqlmodel import select
import os

from app.core.config import settings
from app.api.deps import CurrentUser, SessionDep
from app.models.user_model import UserRoles


router = APIRouter(prefix="/assets", tags=["assets", "asset"])

# upload image
@router.post("")
@router.post("/")
async def upload_image(session: SessionDep,  files: List[UploadFile] = File(...)):
    file = files[0]
 
    
    # save 
    with open(os.path.join("static", "images", f"{file.filename}"), "wb") as buffer:
        buffer.write(file.file.read())
    
    return {"filename": file.filename}

# get
@router.get("")
@router.get("/")
async def get_image(filename: str):
    if not os.path.exists(os.path.join("static", "images", filename)):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(os.path.join("static", "images", filename))