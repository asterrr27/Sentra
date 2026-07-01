from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_length(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class MeResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> dict:
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
    return {"id": user.id, "username": user.username, "email": user.email, "role": user.role}


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == req.username) | (User.email == req.email)).first():
        raise HTTPException(400, "Username or email already taken")
    user = User(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "username": user.username, "email": user.email, "role": user.role},
    )


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "username": user.username, "email": user.email, "role": user.role},
    )


@router.get("/me", response_model=MeResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return MeResponse(**current_user)
