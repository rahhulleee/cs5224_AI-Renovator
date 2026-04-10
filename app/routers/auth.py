from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import DB
from app.models.orm import User
from app.models.schemas import AuthResponse
from app.services.auth import create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(body: RegisterRequest, db: DB):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=body.email,
        name=body.name,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(user_id=user.user_id, token=create_token(user.user_id))


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: DB):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return AuthResponse(user_id=user.user_id, token=create_token(user.user_id))
