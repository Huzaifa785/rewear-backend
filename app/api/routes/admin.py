from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_

from app.api.deps import get_current_admin_user, get_db
from app.models import User, Item, Category, Swap, PointTransaction, ItemStatus, SwapStatus
from app.schemas import (
    UserResponse, ItemResponse, SwapResponse, 
    CategoryCreate, CategoryUpdate, CategoryResponse
)

router = APIRouter()


@router.get("/dashboard")
def get_admin_dashboard(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get admin dashboard with platform statistics
    """
    # User statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    
    # Item statistics
    total_items = db.query(Item).count()
    available_items = db.query(Item).filter(
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    ).count()
    pending_items = db.query(Item).filter(
        Item.status == ItemStatus.UNDER_REVIEW.value
    ).count()
    swapped_items = db.query(Item).filter(
        Item.status == ItemStatus.SWAPPED.value
    ).count()
    
    # Swap statistics
    total_swaps = db.query(Swap).count()
    pending_swaps = db.query(Swap).filter(Swap.status == SwapStatus.PENDING.value).count()
    completed_swaps = db.query(Swap).filter(Swap.status == SwapStatus.COMPLETED.value).count()
    
    # Points statistics
    total_points_in_system = db.query(func.sum(User.points_balance)).scalar() or 0
    total_points_earned = db.query(func.sum(User.total_points_earned)).scalar() or 0
    total_points_spent = db.query(func.sum(User.total_points_spent)).scalar() or 0
    
    # Recent activity
    recent_users = db.query(User).order_by(desc(User.created_at)).limit(5).all()
    recent_items = db.query(Item).order_by(desc(Item.created_at)).limit(5).all()
    recent_swaps = db.query(Swap).order_by(desc(Swap.created_at)).limit(5).all()
    
    # Items needing review
    items_pending_review = db.query(Item).filter(
        Item.status == ItemStatus.UNDER_REVIEW.value
    ).order_by(desc(Item.created_at)).limit(10).all()
    
    return {
        "statistics": {
            "users": {
                "total": total_users,
                "active": active_users,
                "verified": verified_users,
                "admins": admin_users
            },
            "items": {
                "total": total_items,
                "available": available_items,
                "pending_review": pending_items,
                "swapped": swapped_items
            },
            "swaps": {
                "total": total_swaps,
                "pending": pending_swaps,
                "completed": completed_swaps
            },
            "points": {
                "total_in_system": total_points_in_system,
                "total_earned": total_points_earned,
                "total_spent": total_points_spent
            }
        },
        "recent_activity": {
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at,
                    "is_active": user.is_active
                } for user in recent_users
            ],
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "owner_username": item.owner.username,
                    "status": item.status,
                    "created_at": item.created_at
                } for item in recent_items
            ],
            "swaps": [
                {
                    "id": swap.id,
                    "requester_username": swap.requester.username,
                    "owner_username": swap.item_owner.username,
                    "status": swap.status,
                    "swap_type": swap.swap_type,
                    "created_at": swap.created_at
                } for swap in recent_swaps
            ]
        },
        "items_pending_review": [
            {
                "id": item.id,
                "title": item.title,
                "owner_username": item.owner.username,
                "category": item.category.name,
                "created_at": item.created_at
            } for item in items_pending_review
        ]
    }


@router.get("/users", response_model=List[UserResponse])
def list_all_users(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_admin: Optional[bool] = Query(None, description="Filter by admin status"),
    search: Optional[str] = Query(None, description="Search in username or email"),
    limit: int = Query(50, le=200),
    offset: int = Query(0)
) -> Any:
    """
    List all users (admin only)
    """
    query = db.query(User)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)
    
    if search:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    users = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()
    return users


@router.put("/users/{user_id}/toggle-active")
def toggle_user_active_status(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Toggle user active status (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deactivating other admins
    if user.is_admin and user.id != admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate other admin users"
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    return {
        "message": f"User {user.username} {'activated' if user.is_active else 'deactivated'}",
        "user_id": user.id,
        "is_active": user.is_active
    }


@router.get("/items", response_model=List[ItemResponse])
def list_all_items(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, description="Filter by item status"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title or description"),
    limit: int = Query(50, le=200),
    offset: int = Query(0)
) -> Any:
    """
    List all items (admin only)
    """
    query = db.query(Item)
    
    if status_filter:
        query = query.filter(Item.status == status_filter)
    
    if category_id:
        query = query.filter(Item.category_id == category_id)
    
    if search:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Item.title.ilike(f"%{search}%"),
                Item.description.ilike(f"%{search}%")
            )
        )
    
    items = query.order_by(desc(Item.created_at)).offset(offset).limit(limit).all()
    return items


@router.put("/items/{item_id}/approve")
def approve_item(
    item_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    admin_notes: Optional[str] = None
) -> Any:
    """
    Approve an item listing (admin only)
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    item.status = ItemStatus.AVAILABLE.value
    item.admin_notes = admin_notes
    item.published_at = func.now()
    
    db.commit()
    
    return {
        "message": f"Item '{item.title}' approved",
        "item_id": item.id,
        "status": item.status
    }


@router.put("/items/{item_id}/reject")
def reject_item(
    item_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    rejection_reason: str = "Item does not meet platform guidelines",
    admin_notes: Optional[str] = None
) -> Any:
    """
    Reject an item listing (admin only)
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    item.status = ItemStatus.REJECTED.value
    item.rejection_reason = rejection_reason
    item.admin_notes = admin_notes
    
    db.commit()
    
    return {
        "message": f"Item '{item.title}' rejected",
        "item_id": item.id,
        "status": item.status,
        "rejection_reason": rejection_reason
    }


@router.get("/swaps", response_model=List[SwapResponse])
def list_all_swaps(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, description="Filter by swap status"),
    swap_type: Optional[str] = Query(None, description="Filter by swap type"),
    limit: int = Query(50, le=200),
    offset: int = Query(0)
) -> Any:
    """
    List all swaps (admin only)
    """
    query = db.query(Swap)
    
    if status_filter:
        query = query.filter(Swap.status == status_filter)
    
    if swap_type:
        query = query.filter(Swap.swap_type == swap_type)
    
    swaps = query.order_by(desc(Swap.created_at)).offset(offset).limit(limit).all()
    return swaps


@router.post("/categories", response_model=CategoryResponse)
def create_category(
    category_data: CategoryCreate,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new category (admin only)
    """
    from app.core.utils import create_slug
    
    # Check if category name already exists
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    category = Category(
        name=category_data.name,
        slug=create_slug(category_data.name),
        description=category_data.description,
        icon_name=category_data.icon_name,
        color_code=category_data.color_code
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


@router.put("/categories/{category_id}")
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a category (admin only)
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    update_data = category_update.dict(exclude_unset=True)
    
    # Update slug if name changes
    if "name" in update_data:
        from app.core.utils import create_slug
        update_data["slug"] = create_slug(update_data["name"])
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category


@router.get("/analytics")
def get_platform_analytics(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get detailed platform analytics (admin only)
    """
    # User registration over time (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    daily_signups = db.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('signups')
    ).filter(
        User.created_at >= thirty_days_ago
    ).group_by(func.date(User.created_at)).all()
    
    # Items by category
    items_by_category = db.query(
        Category.name,
        func.count(Item.id).label('item_count')
    ).join(Item).group_by(Category.name).all()
    
    # Swap success rate
    total_swaps = db.query(Swap).count()
    completed_swaps = db.query(Swap).filter(Swap.status == SwapStatus.COMPLETED.value).count()
    success_rate = (completed_swaps / total_swaps * 100) if total_swaps > 0 else 0
    
    # Top users by activity
    top_users = db.query(
        User.username,
        func.count(Item.id).label('items_listed'),
        User.total_points_earned
    ).join(Item, User.id == Item.owner_id).group_by(
        User.id, User.username, User.total_points_earned
    ).order_by(desc('items_listed')).limit(10).all()
    
    return {
        "daily_signups": [
            {"date": str(signup.date), "count": signup.signups}
            for signup in daily_signups
        ],
        "items_by_category": [
            {"category": item.name, "count": item.item_count}
            for item in items_by_category
        ],
        "swap_metrics": {
            "total_swaps": total_swaps,
            "completed_swaps": completed_swaps,
            "success_rate": round(success_rate, 2)
        },
        "top_users": [
            {
                "username": user.username,
                "items_listed": user.items_listed,
                "points_earned": user.total_points_earned
            }
            for user in top_users
        ]
    }