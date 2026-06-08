"""Authentication API — registration, login with JWT."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from jose import jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.models.base import get_db
from app.models.student import Student

settings = get_settings()
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new student account."""
    # Check existing user
    result = await db.execute(select(Student).where(Student.username == data.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already exists")

    student_id = uuid.uuid4()
    student = Student(
        id=student_id,
        username=data.username,
        email=data.email,
        hashed_password=pwd_context.hash(data.password),
        major=data.major,
        grade=data.grade,
    )
    db.add(student)
    await db.commit()

    token = create_access_token({"sub": str(student_id), "username": data.username})
    return TokenResponse(
        access_token=token,
        user_id=str(student_id),
        username=data.username,
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login and receive JWT token."""
    result = await db.execute(select(Student).where(Student.username == data.username))
    student = result.scalars().first()

    if not student or not pwd_context.verify(data.password, student.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": str(student.id), "username": student.username})
    return TokenResponse(
        access_token=token,
        user_id=str(student.id),
        username=student.username,
    )
