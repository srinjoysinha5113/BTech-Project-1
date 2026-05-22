from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify JWT token and return current user.
    
    This dependency can be used in protected routes to ensure
    the request is authenticated and provide the user object.
    
    Args:
        credentials: HTTP Bearer credentials containing the JWT token
        db: Database session
        
    Returns:
        Current user object
        
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
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_user_id(
    current_user: User = Depends(get_current_user)
) -> int:
    """
    Get current user ID from authenticated user.
    
    This is a convenience dependency for routes that only need
    the user ID rather than the full user object.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User ID
    """
    return current_user.id


async def verify_token_only(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify JWT token without fetching user from database.
    
    This is a lightweight dependency for routes that only need
    to verify token validity without user data.
    
    Args:
        credentials: HTTP Bearer credentials containing the JWT token
        
    Returns:
        Token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = AuthService.decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload
