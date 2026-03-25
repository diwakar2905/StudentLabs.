"""
User service - business logic for user management.
Handles user creation, authentication, and profile operations.
"""

from sqlalchemy.orm import Session
from app.models import User
from app.utils import hash_password, verify_password, create_access_token
from app.core.config import settings
from datetime import timedelta
from typing import Optional, Tuple


class UserService:
    """Service for user-related business logic"""
    
    @staticmethod
    def create_user(db: Session, email: str, name: str, password: str) -> User:
        """
        Create a new user
        
        Args:
            db: Database session
            email: User email
            name: User name
            password: Plain text password
            
        Returns:
            Created User object
        """
        hashed_password = hash_password(password)
        user = User(
            email=email,
            name=name,
            password_hash=hashed_password,
            plan="free"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user
        
        Returns:
            User if credentials are valid, None otherwise
        """
        user = UserService.get_user_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def create_user_token(user: User) -> Tuple[str, str]:
        """
        Create JWT token for a user
        
        Args:
            user: User object
            
        Returns:
            Tuple of (access_token, token_type)
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )
        return access_token, "bearer"
    
    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> dict:
        """Get user profile with project count"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        projects_count = len(user.projects) if user.projects else 0
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "plan": user.plan,
            "created_at": user.created_at,
            "projects_count": projects_count
        }
