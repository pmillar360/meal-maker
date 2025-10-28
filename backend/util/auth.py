import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, constants
import os

SECRET_KEY = os.getenv("SECRET_KEY") or "your-default-secret-key-here-123"
ALGORITHM = constants.ALGORITHMS.HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Maybe something shorter like 10/15 minutes?
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except JWTError:
        return None

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def get_refresh_token_age() -> int:
    return REFRESH_TOKEN_EXPIRE_DAYS