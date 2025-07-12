# app/api/routes/auth.py - Updated with welcome notifications
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.utils import generate_username, award_points
from app.core.websockets import notification_service
from app.models import User
from app.schemas import UserCreate, UserResponse, UserLogin, Token, UserUpdate
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user with welcome notifications
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        bio=user_data.bio,
        city=user_data.city,
        state=user_data.state,
        country=user_data.country,
        points_balance=settings.SIGNUP_BONUS_POINTS,
        total_points_earned=settings.SIGNUP_BONUS_POINTS
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Award signup bonus points transaction
    award_points(
        user=user,
        amount=settings.SIGNUP_BONUS_POINTS,
        transaction_type="signup_bonus",
        description="Welcome bonus for joining ReWear",
        db=db
    )
    
    # 🎉 Send Welcome Notifications (WebSocket + Email)
    try:
        await notification_service.send_welcome_notification(user.id)
        print(f"✅ Welcome notifications sent to {user.email}")
    except Exception as e:
        print(f"⚠️ Failed to send welcome notifications: {e}")
        # Don't fail registration if notifications fail
    
    return user


@router.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    }


@router.post("/login-json", response_model=Token)
def login_user_json(
    user_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    JSON login endpoint (alternative to OAuth2 form)
    """
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user profile
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user profile
    """
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Refresh access token
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
def logout_user(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout user (client should discard the token)
    """
    return {"message": "Successfully logged out"}


# Additional endpoints for welcome email management
@router.post("/resend-welcome")
async def resend_welcome_email(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Resend welcome email (for testing or if user didn't receive it)
    """
    try:
        await notification_service.send_welcome_notification(current_user.id)
        return {"message": "Welcome email resent successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send welcome email: {str(e)}"
        )


@router.post("/test-welcome-email")
async def test_welcome_email(
    test_email: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Send test welcome email to specified address (for development)
    """
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not available in production"
        )
    
    try:
        from app.services.email import email_service
        
        # Create a temporary user object for testing
        test_user = User(
            email=test_email,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        
        success = await email_service.send_welcome_email(test_user)
        
        return {
            "message": f"Test welcome email sent to {test_email}",
            "success": success
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test email: {str(e)}"
        )