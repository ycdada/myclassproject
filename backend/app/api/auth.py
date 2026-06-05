from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Schemas ---
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    major: Optional[str] = None
    grade: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


# --- Routes ---
@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister):
    # TODO: Implement with database
    return {
        "access_token": "placeholder",
        "token_type": "bearer",
        "user_id": "placeholder",
        "username": data.username,
    }


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    # TODO: Implement with database
    return {
        "access_token": "placeholder",
        "token_type": "bearer",
        "user_id": "placeholder",
        "username": data.username,
    }


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
