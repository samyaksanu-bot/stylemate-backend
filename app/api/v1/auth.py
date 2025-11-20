from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select
from passlib.hash import bcrypt

from app.db.session import get_session_sync
from app.db.models import User

import uuid

router = APIRouter()

class RegisterIn(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(payload: RegisterIn):
    with get_session_sync() as session:
        stmt = select(User).where(User.email == payload.email)
        existing = session.exec(stmt).one_or_none()

        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed = bcrypt.hash(payload.password)
        new_user = User(
            id=str(uuid.uuid4()),
            email=payload.email,
            password_hash=hashed
        )

        session.add(new_user)
        session.commit()

        return {"message": "User registered successfully", "user_id": new_user.id}


class LoginIn(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(payload: LoginIn):
    with get_session_sync() as session:
        stmt = select(User).where(User.email == payload.email)
        user = session.exec(stmt).one_or_none()

        if not user or not bcrypt.verify(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        return {"message": "Login successful", "user_id": user.id}
