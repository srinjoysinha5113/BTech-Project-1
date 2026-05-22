from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import AuthService
from app.config import settings

router = APIRouter()
security = HTTPBearer()


# Pydantic models for request/response
class UserRegister(BaseModel):
    """User registration request model."""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login request model."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str
    expires_in: int


class UserResponse(BaseModel):
    """User response model."""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    User registration endpoint.
    
    Creates a new user with hashed password.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    existing_user = AuthService.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = AuthService.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = AuthService.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    User login endpoint.
    
    Authenticates user and returns JWT access token.
    
    Args:
        user_data: User login credentials
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = AuthService.authenticate_user(
        db=db,
        username=user_data.username,
        password=user_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current user information.
    
    Requires valid JWT token in Authorization header.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Decode token
    token = credentials.credentials
    payload = AuthService.decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID from token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
