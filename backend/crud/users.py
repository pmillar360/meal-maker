from datetime import datetime, timezone
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import delete, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from util.auth import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    hash_password,
    oauth2_scheme,
    verify_password,
    verify_token,
)

REFRESH_TOKEN_MAX_AGE = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def get_user(username: str, db: Session):
    return db.query(models.User).filter(
        func.lower(models.User.username) == func.lower(username)
    ).first()


def get_current_active_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme),
) -> models.User:
    payload = verify_token(token)
    user = db.query(models.User).filter_by(auth_id=payload["sub"]).first() if payload else None
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user


def _refresh_token_hash(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def _issue_tokens(
    db: Session, user: models.User, status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    token = token_urlsafe(32)
    response = JSONResponse(
        {"access_token": create_access_token(user.auth_id), "token_type": "bearer"},
        status_code=status_code,
    )
    response.headers["Cache-Control"] = "no-store"
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=REFRESH_TOKEN_MAX_AGE,
    )
    db.add(models.RefreshSession(
        token_hash=_refresh_token_hash(token),
        user_auth_id=user.auth_id,
        expires_at=int(datetime.now(timezone.utc).timestamp()) + REFRESH_TOKEN_MAX_AGE,
    ))
    db.commit()
    return response


def register_user(user_data: schemas.UserCreate, db: Session):
    if get_user(user_data.username, db):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = models.User(username=user_data.username, hashed_password=hash_password(user_data.password))
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        if get_user(user_data.username, db):
            raise HTTPException(status_code=400, detail="Username already taken")
        raise

    return _issue_tokens(db, user, status.HTTP_201_CREATED)


def login(form_data: schemas.LoginRequest, db: Session):
    user = get_user(form_data.username, db)
    if not user or not user.is_active or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    db.execute(delete(models.RefreshSession).where(
        models.RefreshSession.expires_at <= int(datetime.now(timezone.utc).timestamp())
    ))
    return _issue_tokens(db, user)


def refresh_token(token: str, db: Session):
    # Consume the old token atomically so concurrent requests cannot both rotate it.
    auth_id = db.execute(
        delete(models.RefreshSession)
        .where(
            models.RefreshSession.token_hash == _refresh_token_hash(token),
            models.RefreshSession.expires_at > int(datetime.now(timezone.utc).timestamp()),
        )
        .returning(models.RefreshSession.user_auth_id)
    ).scalar_one_or_none()
    user = db.query(models.User).filter_by(auth_id=auth_id).first() if auth_id else None
    if not user or not user.is_active:
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    return _issue_tokens(db, user)


def revoke_refresh_token(token: str, db: Session):
    db.execute(delete(models.RefreshSession).where(
        models.RefreshSession.token_hash == _refresh_token_hash(token)
    ))
    db.commit()
