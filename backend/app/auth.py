from datetime import datetime, timedelta

import bcrypt
from fastapi import Depends, HTTPException, Header
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


class CurrentUser(BaseModel):
    id: int
    username: str
    email: str
    role: str


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> CurrentUser:
    if not authorization:
        raise HTTPException(401, "Missing authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")
    token = authorization[7:]
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(401, "Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Invalid token payload")
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(401, "Invalid token payload")
    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise HTTPException(401, "User not found")
    return CurrentUser(id=user.id, username=user.username, email=user.email, role=user.role)
