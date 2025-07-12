# app/api/routes/swaps.py - Enhanced with real-time notifications
from typing import Any, List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.utils import deduct_points, award_points
from app.core.websockets import notification_service
from app.models import User, Item, Swap, SwapType, SwapStatus, ItemStatus
from app.schemas import SwapCreate, SwapUpdate, SwapResponse

router = APIRouter()


@router.post("/", response_model=SwapResponse, status_code=status.HTTP_201_CREATED)
async def create_swap_request(
    swap_data: SwapCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new swap request with real-time notification
    """
    # Get the item being requested
    item = db.query(Item).filter(
        Item.id == swap_data.item_id,
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or not available for swapping"
        )
    
    # Can't swap with yourself
    if item.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create swap request for your own item"
        )
    
    # Validate swap type specific requirements
    if swap_data.swap_type == SwapType.DIRECT_SWAP.value:
        if not swap_data.offered_item_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="offered_item_id is required for direct swaps"
            )
        
        # Verify offered item exists and belongs to requester
        offered_item = db.query(Item).filter(
            Item.id == swap_data.offered_item_id,
            Item.owner_id == current_user.id,
            Item.status == ItemStatus.AVAILABLE.value,
            Item.is_active == True
        ).first()
        
        if not offered_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offered item not found or not available"
            )
    
    elif swap_data.swap_type == SwapType.POINTS_REDEMPTION.value:
        if not swap_data.points_offered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="points_offered is required for points redemption"
            )
        
        # Check if user has enough points
        if current_user.points_balance < swap_data.points_offered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient points balance"
            )
        
        # Points should be reasonable (at least 50% of item value)
        min_points = item.points_value // 2
        if swap_data.points_offered < min_points:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Points offered too low. Minimum: {min_points} points"
            )
    
    # Check if there's already a pending swap for this item from this user
    existing_swap = db.query(Swap).filter(
        Swap.item_id == swap_data.item_id,
        Swap.requester_id == current_user.id,
        Swap.status == SwapStatus.PENDING.value
    ).first()
    
    if existing_swap:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending swap request for this item"
        )
    
    # Create swap request
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # Expire in 7 days
    
    swap = Swap(
        requester_id=current_user.id,
        item_id=swap_data.item_id,
        item_owner_id=item.owner_id,
        swap_type=swap_data.swap_type,
        status=SwapStatus.PENDING.value,
        offered_item_id=swap_data.offered_item_id,
        points_offered=swap_data.points_offered,
        requester_message=swap_data.requester_message,
        expires_at=expires_at
    )
    
    db.add(swap)
    db.commit()
    db.refresh(swap)
    
    # 🔔 Send real-time notification to item owner
    await notification_service.notify_swap_request(
        requester_id=current_user.id,
        owner_id=item.owner_id,
        swap_data={
            "swap_id": swap.id,
            "item_id": item.id,
            "item_title": item.title,
            "swap_type": swap.swap_type,
            "points_offered": swap.points_offered,
            "requester_username": current_user.username
        }
    )
    
    return SwapResponse.model_validate(swap)


@router.put("/{swap_id}/accept", response_model=SwapResponse)
async def accept_swap(
    swap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    owner_response: Optional[str] = None
) -> Any:
    """
    Accept a swap request with real-time notification
    """
    swap = db.query(Swap).filter(
        Swap.id == swap_id,
        Swap.item_owner_id == current_user.id,
        Swap.status == SwapStatus.PENDING.value
    ).first()
    
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found or cannot be accepted"
        )
    
    # Check if swap hasn't expired
    if swap.expires_at and datetime.now(timezone.utc) > swap.expires_at:
        swap.status = SwapStatus.EXPIRED.value
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Swap request has expired"
        )
    
    # Update swap status
    swap.status = SwapStatus.ACCEPTED.value
    swap.owner_response = owner_response
    swap.responded_at = datetime.now(timezone.utc)
    
    # Update item status
    item = swap.item
    item.status = ItemStatus.PENDING_SWAP.value
    
    # If direct swap, also update offered item
    if swap.swap_type == SwapType.DIRECT_SWAP.value and swap.offered_item:
        swap.offered_item.status = ItemStatus.PENDING_SWAP.value
    
    db.commit()
    db.refresh(swap)
    
    # 🔔 Send real-time notification to requester
    await notification_service.notify_swap_response(
        requester_id=swap.requester_id,
        owner_id=current_user.id,
        swap_data={
            "swap_id": swap.id,
            "item_id": item.id,
            "item_title": item.title,
            "owner_response": owner_response
        },
        accepted=True
    )
    
    return SwapResponse.model_validate(swap)


@router.put("/{swap_id}/reject", response_model=SwapResponse)
async def reject_swap(
    swap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    owner_response: Optional[str] = None
) -> Any:
    """
    Reject a swap request with real-time notification
    """
    swap = db.query(Swap).filter(
        Swap.id == swap_id,
        Swap.item_owner_id == current_user.id,
        Swap.status == SwapStatus.PENDING.value
    ).first()
    
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found or cannot be rejected"
        )
    
    # Update swap status
    swap.status = SwapStatus.REJECTED.value
    swap.owner_response = owner_response
    swap.responded_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(swap)
    
    # 🔔 Send real-time notification to requester
    await notification_service.notify_swap_response(
        requester_id=swap.requester_id,
        owner_id=current_user.id,
        swap_data={
            "swap_id": swap.id,
            "item_id": swap.item.id,
            "item_title": swap.item.title,
            "owner_response": owner_response
        },
        accepted=False
    )
    
    return SwapResponse.model_validate(swap)


@router.put("/{swap_id}/complete", response_model=SwapResponse)
async def complete_swap(
    swap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Mark swap as completed with real-time notifications and points handling
    """
    swap = db.query(Swap).filter(
        Swap.id == swap_id,
        Swap.item_owner_id == current_user.id,
        Swap.status == SwapStatus.ACCEPTED.value
    ).first()
    
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap not found or cannot be completed"
        )
    
    # Complete the swap
    swap.status = SwapStatus.COMPLETED.value
    swap.completed_at = datetime.now(timezone.utc)
    
    # Update item statuses
    item = swap.item
    item.status = ItemStatus.SWAPPED.value
    
    points_earned = {}
    
    if swap.swap_type == SwapType.DIRECT_SWAP.value and swap.offered_item:
        # Direct swap: both items are swapped
        swap.offered_item.status = ItemStatus.SWAPPED.value
        
        # Award points to both users
        requester_points = item.points_value // 4  # 25% of item value
        owner_points = swap.offered_item.points_value // 4
        
        award_points(
            user=swap.requester,
            amount=requester_points,
            transaction_type="swap_completed",
            description=f"Points earned from swapping for '{item.title}'",
            db=db,
            swap_id=swap.id,
            item_id=item.id
        )
        
        award_points(
            user=current_user,
            amount=owner_points,
            transaction_type="swap_completed", 
            description=f"Points earned from swapping '{swap.offered_item.title}'",
            db=db,
            swap_id=swap.id,
            item_id=swap.offered_item.id
        )
        
        points_earned = {
            "requester_points": requester_points,
            "owner_points": owner_points
        }
    
    elif swap.swap_type == SwapType.POINTS_REDEMPTION.value:
        # Points redemption: deduct points from requester, award to owner
        deduct_points(
            user=swap.requester,
            amount=swap.points_offered,
            transaction_type="points_redemption",
            description=f"Points spent on '{item.title}'",
            db=db,
            swap_id=swap.id,
            item_id=item.id
        )
        
        award_points(
            user=current_user,
            amount=swap.points_offered,
            transaction_type="points_received",
            description=f"Points received for '{item.title}'",
            db=db,
            swap_id=swap.id,
            item_id=item.id
        )
        
        points_earned = {
            "owner_points": swap.points_offered
        }
    
    db.commit()
    db.refresh(swap)
    
    # 🔔 Send real-time notifications to both parties
    await notification_service.notify_swap_completed(
        user_ids=[swap.requester_id, current_user.id],
        swap_data={
            "swap_id": swap.id,
            "item_id": item.id,
            "item_title": item.title,
            "points_earned": points_earned.get("requester_points", points_earned.get("owner_points", 0))
        }
    )
    
    # Send individual points notifications if applicable
    if "requester_points" in points_earned:
        await notification_service.notify_points_earned(
            user_id=swap.requester_id,
            points=points_earned["requester_points"],
            reason=f"Completed swap for '{item.title}'"
        )
    
    if "owner_points" in points_earned:
        await notification_service.notify_points_earned(
            user_id=current_user.id,
            points=points_earned["owner_points"],
            reason=f"Completed swap of '{item.title}'"
        )
    
    return SwapResponse.model_validate(swap)


@router.get("/", response_model=List[SwapResponse])
def list_user_swaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    swap_type: Optional[str] = Query(None, description="Filter by 'sent' or 'received'"),
    status_filter: Optional[str] = Query(None, description="Filter by swap status"),
    limit: int = Query(20, le=100),
    offset: int = Query(0)
) -> Any:
    """
    List current user's swaps (sent and received)
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
    
    swaps = query.order_by(Swap.created_at.desc()).offset(offset).limit(limit).all()
    
    return [SwapResponse.model_validate(swap) for swap in swaps]


@router.get("/{swap_id}", response_model=SwapResponse)
def get_swap(
    swap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get swap details (only if user is involved)
    """
    swap = db.query(Swap).filter(Swap.id == swap_id).first()
    
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap not found"
        )
    
    # Check if user is involved in this swap
    if swap.requester_id != current_user.id and swap.item_owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this swap"
        )
    
    return SwapResponse.model_validate(swap)


@router.put("/{swap_id}/cancel", response_model=SwapResponse)
async def cancel_swap(
    swap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Cancel a swap request (only by requester, only if pending)
    """
    swap = db.query(Swap).filter(
        Swap.id == swap_id,
        Swap.requester_id == current_user.id,
        Swap.status == SwapStatus.PENDING.value
    ).first()
    
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found or cannot be cancelled"
        )
    
    # Cancel the swap
    swap.status = SwapStatus.CANCELLED.value
    
    db.commit()
    db.refresh(swap)
    
    # 🔔 Optional: Notify item owner of cancellation
    await notification_service.notify_swap_response(
        requester_id=current_user.id,
        owner_id=swap.item_owner_id,
        swap_data={
            "swap_id": swap.id,
            "item_id": swap.item.id,
            "item_title": swap.item.title
        },
        accepted=False  # Cancellation is treated as a negative response
    )
    
    return SwapResponse.model_validate(swap)


@router.get("/stats/summary")
async def get_swap_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get swap statistics for the current user
    """
    from sqlalchemy import func, or_
    
    # Count swaps by status for user
    sent_stats = db.query(
        Swap.status,
        func.count(Swap.id).label('count')
    ).filter(
        Swap.requester_id == current_user.id
    ).group_by(Swap.status).all()
    
    received_stats = db.query(
        Swap.status,
        func.count(Swap.id).label('count')
    ).filter(
        Swap.item_owner_id == current_user.id
    ).group_by(Swap.status).all()
    
    # Calculate success rate
    total_completed = db.query(Swap).filter(
        or_(
            Swap.requester_id == current_user.id,
            Swap.item_owner_id == current_user.id
        ),
        Swap.status == SwapStatus.COMPLETED.value
    ).count()
    
    total_swaps = db.query(Swap).filter(
        or_(
            Swap.requester_id == current_user.id,
            Swap.item_owner_id == current_user.id
        )
    ).count()
    
    success_rate = (total_completed / total_swaps * 100) if total_swaps > 0 else 0
    
    # Recent activity
    recent_swaps = db.query(Swap).filter(
        or_(
            Swap.requester_id == current_user.id,
            Swap.item_owner_id == current_user.id
        )
    ).order_by(Swap.created_at.desc()).limit(5).all()
    
    return {
        "sent_swaps": {status: count for status, count in sent_stats},
        "received_swaps": {status: count for status, count in received_stats},
        "total_completed": total_completed,
        "total_swaps": total_swaps,
        "success_rate": round(success_rate, 2),
        "recent_activity": [
            {
                "id": swap.id,
                "type": "sent" if swap.requester_id == current_user.id else "received",
                "status": swap.status,
                "item_title": swap.item.title,
                "created_at": swap.created_at,
                "other_user": (
                    swap.item_owner.username if swap.requester_id == current_user.id 
                    else swap.requester.username
                )
            }
            for swap in recent_swaps
        ]
    }