from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.models import User
from app import schemas
from util.auth import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_age,
    hash_password,
    verify_password,
    verify_token,
    oauth2_scheme,
)

def get_user(username: str, db: Session = Depends(get_db)):
    found_user = (
        db.query(models.User)
        .filter(func.lower(models.User.username) == func.lower(username))
        .first()
    )
    return found_user

def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    found_user = db.query(models.User).filter(models.User.id == user_id).first()
    return found_user

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        if not token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        payload = verify_token(token)

        if not payload:
            # User passed an expired access token
            raise credentials_exception

        username = payload.get("sub")

        if not username:
            raise credentials_exception

        return get_user(username, db)
    except HTTPException as e:
        raise e

def get_current_active_user(
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = (
        db.query(models.User).filter(models.User.username == user_data.username).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    hashed_pwd = hash_password(user_data.password)
    new_user = models.User(username=user_data.username, hashed_password=hashed_pwd)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"sub": new_user.username})
    refresh_token = create_refresh_token({"sub": new_user.username})

    response = JSONResponse(
        {"access_token": access_token, "token_type": "bearer"},
        status_code=status.HTTP_201_CREATED,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=get_refresh_token_age() * 24 * 60 * 60,
    )

    return response

def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    new_access_token = create_access_token({"sub": username})
    new_refresh_token = create_refresh_token({"sub": username})

    response = JSONResponse({"access_token": new_access_token, "token_type": "bearer"})

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=get_refresh_token_age() * 24 * 60 * 60,
    )

    return response

def login(form_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Log in a user and return access and refresh tokens"""
    user = (
        db.query(models.User).filter(models.User.username == form_data.username).first()
    )

    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    token_data = {"sub": user.username}

    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=get_refresh_token_age() * 24 * 60 * 60,
    )

    return response

def get_current_user_by_token(token: str):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    return {"username": payload["sub"]}