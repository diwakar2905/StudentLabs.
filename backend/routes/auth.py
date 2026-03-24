from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter()
users_router = APIRouter()

class UserSignup(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/signup")
async def signup(user: UserSignup):
    # Mock signup
    return {"message": "User registered successfully", "user": {"email": user.email, "name": user.name}}

@router.post("/login")
async def login(user: UserLogin):
    # Mock login
    return {"access_token": "mock-jwt-token-123", "token_type": "bearer"}

@users_router.get("/me")
async def get_users_me():
    # Mock user profile
    return {"email": "student@university.edu", "name": "Student", "remaining_credits": 10}
