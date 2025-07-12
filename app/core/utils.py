import re
import secrets
import string
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, PointTransaction
from app.config import settings


def generate_username(email: str, db: Session) -> str:
    """Generate a unique username from email"""
    # Extract username part from email
    base_username = email.split("@")[0]
    
    # Clean username (alphanumeric and underscores only)
    base_username = re.sub(r'[^a-zA-Z0-9_]', '', base_username)
    
    # Ensure minimum length
    if len(base_username) < 3:
        base_username = f"user_{base_username}"
    
    # Check if username exists
    username = base_username
    counter = 1
    
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}_{counter}"
        counter += 1
    
    return username


def create_slug(text: str) -> str:
    """Create URL-friendly slug from text"""
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    return slug


def generate_random_string(length: int = 32) -> str:
    """Generate a random string"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def validate_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, List[str]]:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    return len(errors) == 0, errors


def award_points(
    user: User, 
    amount: int, 
    transaction_type: str, 
    description: str,
    db: Session,
    item_id: Optional[int] = None,
    swap_id: Optional[int] = None
) -> PointTransaction:
    """Award points to a user and create transaction record"""
    
    # Update user points
    user.points_balance += amount
    user.total_points_earned += amount
    
    # Create transaction record
    transaction = PointTransaction(
        user_id=user.id,
        amount=amount,
        transaction_type=transaction_type,
        description=description,
        item_id=item_id,
        swap_id=swap_id
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction


def deduct_points(
    user: User,
    amount: int,
    transaction_type: str,
    description: str,
    db: Session,
    item_id: Optional[int] = None,
    swap_id: Optional[int] = None
) -> Optional[PointTransaction]:
    """Deduct points from user if they have enough"""
    
    if user.points_balance < amount:
        return None  # Insufficient points
    
    # Update user points
    user.points_balance -= amount
    user.total_points_spent += amount
    
    # Create transaction record (negative amount)
    transaction = PointTransaction(
        user_id=user.id,
        amount=-amount,
        transaction_type=transaction_type,
        description=description,
        item_id=item_id,
        swap_id=swap_id
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction


def format_points(amount: int) -> str:
    """Format points for display"""
    if amount >= 1000:
        return f"{amount/1000:.1f}k points"
    return f"{amount} points"


def calculate_item_points(original_price: Optional[int] = None) -> int:
    """Calculate points value for an item"""
    if original_price:
        # Base points on original price (1 point per $5)
        return max(settings.DEFAULT_ITEM_POINTS, original_price // 500)
    
    return settings.DEFAULT_ITEM_POINTS


def is_expired(expires_at: Optional[datetime]) -> bool:
    """Check if a datetime has expired"""
    if expires_at is None:
        return False
    return datetime.utcnow() > expires_at


def time_until_expiry(expires_at: Optional[datetime]) -> Optional[timedelta]:
    """Get time remaining until expiry"""
    if expires_at is None:
        return None
    
    remaining = expires_at - datetime.utcnow()
    return remaining if remaining.total_seconds() > 0 else timedelta(0)