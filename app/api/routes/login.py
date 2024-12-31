from datetime import timedelta
from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.models import Token, RefreshToken, Tokens
from app.models.user_model import UserCreate, UserRoles, User, UserPublic

from app.services.user_service import create_user, authenticate, get_user_by_username

router = APIRouter(tags=["login"])


# takes username and password and returns refresh token
@router.post("/login/")
@router.post("/login", include_in_schema=False)
def login_refresh_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    OAuth2 compatible token login, get a refresh token for future requests
    """
    user = authenticate(
        session=session, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        )
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
        )
    dump = user.model_dump()
    if not isinstance(access_token, str):
        access_token = access_token.decode("utf-8")
    if not isinstance(refresh_token, str):
        refresh_token = refresh_token.decode("utf-8")

    response = JSONResponse(
       {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "roles": user.roles,
        },
    )
  
  
    response.set_cookie(key="refresh-token", value=refresh_token)
    return response


# takes refresh token and returns access token
@router.post("/login/refresh/")
@router.post("/login/refresh" , include_in_schema=False)
def login_access_token(
    request: Request,
    session: SessionDep, 
    refresh_token: str
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """


    # verify refresh token
    user_id = security.verify_refresh_token(refresh_token)
    if not user_id:
        return HTTPException(status_code=400, detail="Invalid token")
    
    user = session.exec(select(User).where(User.id == int(user_id))).first()
    # if not user
    if not user:
        return HTTPException(status_code=400, detail="Invalid token")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    dump = user.model_dump()
    access_token = security.create_access_token(
                user_id, expires_delta=access_token_expires
            )
    if not isinstance(access_token, str):
        access_token = access_token.decode("utf-8")
    return JSONResponse(
        {
            "access_token": access_token,
            "token_type": "bearer",
                    "user_id": user.id,
        "username": user.username,
        "roles": user.roles,

            }
    )
    return Token(
        access_token=security.create_access_token(
            user_id, expires_delta=access_token_expires
        )
    )





# create user if you are admin
@router.post("/users/", response_model=UserPublic, include_in_schema=False)
@router.post("/users", response_model=UserPublic, include_in_schema=False)
def create_user_route(
    session: SessionDep,
    current_user: CurrentUser,
    user_in: UserCreate,
    
):
    """
    Create a new user
    """
    if not UserRoles.admin in current_user.roles:
        raise HTTPException(status_code=400, detail="You are not an admin")
    
    user = create_user(session=session, user_create=user_in)
    return user

@router.get("/users/me/", response_model=UserPublic, include_in_schema=False)
@router.get("/users/me", response_model=UserPublic, include_in_schema=False)
def read_users_me(
    current_user: CurrentUser,
):
    """
    Get current user
    """
    return current_user

@router.get("/users/", response_model=List[UserPublic] , include_in_schema=False)
@router.get("/users", response_model=List[UserPublic] , include_in_schema=False)
def read_users(
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Get all users
    """
    if not UserRoles.admin in current_user.roles:
        raise HTTPException(status_code=400, detail="You are not an admin")
    users = session.exec(select(User)).all()
    return users

@router.delete("/users/{username}/", response_model=UserPublic)
@router.delete("/users/{username}", response_model=UserPublic)
def delete_user(
    session: SessionDep,
    current_user: CurrentUser,
    username: str,
):
    """
    Delete a user
    """
    if not UserRoles.admin in current_user.roles:
        raise HTTPException(status_code=400, detail="You are not an admin")
    user = get_user_by_username(session=session, username=username)
    session.delete(user)
    session.commit()
    return user