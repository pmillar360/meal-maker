from datetime import datetime, timedelta
from jose import jwt, JWTError, constants
import os

SECRET_KEY = os.getenv("SECRET_KEY") or "your-default-secret-key-here-123"
ALGORITHM = constants.ALGORITHMS.HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except JWTError:
        return None