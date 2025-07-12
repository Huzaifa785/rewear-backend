from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_current_user, get_db
from app.models import User, Item, Swap, PointTransaction
from app.schemas import (
    UserResponse, UserPublic, ItemSummary, SwapSummary, 
    PointTransactionSummary
)

router = APIRouter()


@router.get("/me/dashboard")
def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user dashboard data
    """
    # Get user's items
    user_items = db.query(Item).filter(Item.owner_id == current_user.id).all()
    
    # Get user's swaps (sent and received)
    sent_swaps = db.query(Swap).filter(Swap.requester_id == current_user.id).all()
    received_swaps = db.query(Swap).filter(Swap.item_owner_id == current_user.id).all()
    
    # Get recent point transactions
    recent_transactions = db.query(PointTransaction).filter(
        PointTransaction.user_id == current_user.id
    ).order_by(desc(PointTransaction.created_at)).limit(10).all()
    
    # Calculate statistics
    total_items = len(user_items)
    available_items = len([item for item in user_items if item.status == "available"])
    total_swaps = len(sent_swaps) + len(received_swaps)
    pending_swaps = len([swap for swap in sent_swaps + received_swaps if swap.status == "pending"])
    
    # Convert models to dictionaries for JSON serialization
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "points_balance": current_user.points_balance,
            "total_points_earned": current_user.total_points_earned,
            "total_points_spent": current_user.total_points_spent,
            "created_at": current_user.created_at
        },
        "statistics": {
            "total_items": total_items,
            "available_items": available_items,
            "total_swaps": total_swaps,
            "pending_swaps": pending_swaps,
            "points_balance": current_user.points_balance,
            "total_points_earned": current_user.total_points_earned,
            "total_points_spent": current_user.total_points_spent
        },
        "recent_items": [
            {
                "id": item.id,
                "title": item.title,
                "condition": item.condition,
                "points_value": item.points_value,
                "status": item.status,
                "created_at": item.created_at
            } for item in user_items[:5]
        ],
        "recent_sent_swaps": [
            {
                "id": swap.id,
                "swap_type": swap.swap_type,
                "status": swap.status,
                "points_offered": swap.points_offered,
                "created_at": swap.created_at
            } for swap in sent_swaps[:5]
        ],
        "recent_received_swaps": [
            {
                "id": swap.id,
                "swap_type": swap.swap_type,
                "status": swap.status,
                "points_offered": swap.points_offered,
                "created_at": swap.created_at
            } for swap in received_swaps[:5]
        ],
        "recent_transactions": [
            {
                "id": trans.id,
                "amount": trans.amount,
                "transaction_type": trans.transaction_type,
                "description": trans.description,
                "created_at": trans.created_at
            } for trans in recent_transactions
        ]
    }


@router.get("/me/items", response_model=List[ItemSummary])
def get_user_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: str = Query(None, description="Filter by item status"),
    limit: int = Query(20, le=100, description="Number of items to return"),
    offset: int = Query(0, description="Number of items to skip")
) -> Any:
    """
    Get current user's items
    """
    query = db.query(Item).filter(Item.owner_id == current_user.id)
    
    if status_filter:
        query = query.filter(Item.status == status_filter)
    
    items = query.order_by(desc(Item.created_at)).offset(offset).limit(limit).all()
    
    return items


@router.get("/me/swaps", response_model=List[SwapSummary])
def get_user_swaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    swap_type: str = Query(None, description="Filter by 'sent' or 'received'"),
    status_filter: str = Query(None, description="Filter by swap status"),
    limit: int = Query(20, le=100, description="Number of swaps to return"),
    offset: int = Query(0, description="Number of swaps to skip")
) -> Any:
    """
    Get current user's swaps (sent and received)
    """
    if swap_type == "sent":
        query = db.query(Swap).filter(Swap.requester_id == current_user.id)
    elif swap_type == "received":
        query = db.query(Swap).filter(Swap.item_owner_id == current_user.id)
    else:
        # Get both sent and received swaps
        from sqlalchemy import or_
        query = db.query(Swap).filter(
            or_(
                Swap.requester_id == current_user.id,
                Swap.item_owner_id == current_user.id
            )
        )
    
    if status_filter:
        query = query.filter(Swap.status == status_filter)
    
    swaps = query.order_by(desc(Swap.created_at)).offset(offset).limit(limit).all()
    
    return swaps


@router.get("/me/points", response_model=List[PointTransactionSummary])
def get_user_point_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    transaction_type: str = Query(None, description="Filter by transaction type"),
    limit: int = Query(50, le=200, description="Number of transactions to return"),
    offset: int = Query(0, description="Number of transactions to skip")
) -> Any:
    """
    Get current user's point transaction history
    """
    query = db.query(PointTransaction).filter(PointTransaction.user_id == current_user.id)
    
    if transaction_type:
        query = query.filter(PointTransaction.transaction_type == transaction_type)
    
    transactions = query.order_by(desc(PointTransaction.created_at)).offset(offset).limit(limit).all()
    
    return transactions


@router.get("/{user_id}", response_model=UserPublic)
def get_user_public_profile(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get public user profile
    """
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/{user_id}/items", response_model=List[ItemSummary])
def get_user_public_items(
    user_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(20, le=100, description="Number of items to return"),
    offset: int = Query(0, description="Number of items to skip")
) -> Any:
    """
    Get public user's available items
    """
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only show available items to public
    items = db.query(Item).filter(
        Item.owner_id == user_id,
        Item.status == "available",
        Item.is_active == True
    ).order_by(desc(Item.created_at)).offset(offset).limit(limit).all()
    
    return items