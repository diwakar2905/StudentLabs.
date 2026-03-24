from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from database import get_db
from models import User
from auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    extract_token_from_header,
    TokenData,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()
users_router = APIRouter()

class UserSignup(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = extract_token_from_header(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = verify_access_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserSignup, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate email format (basic)
    if "@" not in user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Validate password strength
    if len(user.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Create new user
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
        plan="free"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.id, "email": db_user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "name": db_user.name,
            "plan": db_user.plan
        }
    }

@users_router.get("/me", response_model=dict)
async def get_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "plan": current_user.plan,
        "created_at": current_user.created_at,
        "projects_count": len(current_user.projects)
    }

from datetime import datetime

