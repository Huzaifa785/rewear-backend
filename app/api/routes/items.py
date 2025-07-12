from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from app.api.deps import get_current_user, get_db, get_optional_current_user
from app.core.utils import calculate_item_points, award_points
from app.models import User, Item, Category, ItemStatus, ItemCondition, ItemSize
from app.schemas import (
    ItemCreate, ItemUpdate, ItemResponse, ItemPublic, ItemSummary,
    CategoryResponse
)

router = APIRouter()


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_data: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new item listing
    """
    # Verify category exists
    category = db.query(Category).filter(Category.id == item_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Calculate points value if not provided
    points_value = item_data.points_value
    if not points_value:
        points_value = calculate_item_points(item_data.original_price)
    
    # Create new item
    item = Item(
        title=item_data.title,
        description=item_data.description,
        brand=item_data.brand,
        category_id=item_data.category_id,
        owner_id=current_user.id,
        size=item_data.size,
        condition=item_data.condition,
        color=item_data.color,
        material=item_data.material,
        tags=item_data.tags,
        pickup_location=item_data.pickup_location,
        shipping_available=item_data.shipping_available,
        original_price=item_data.original_price,
        points_value=points_value,
        status=ItemStatus.AVAILABLE.value
    )
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    # Award points for listing an item
    listing_points = max(5, points_value // 4)  # 25% of item value, minimum 5
    award_points(
        user=current_user,
        amount=listing_points,
        transaction_type="item_listed",
        description=f"Points earned for listing '{item.title}'",
        db=db,
        item_id=item.id
    )
    
    return item


@router.get("/", response_model=List[ItemPublic])
def list_items(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    size: Optional[str] = Query(None, description="Filter by size"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    min_points: Optional[int] = Query(None, description="Minimum points value"),
    max_points: Optional[int] = Query(None, description="Maximum points value"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    color: Optional[str] = Query(None, description="Filter by color"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query("created_at", description="Sort by: created_at, points_value, title"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    limit: int = Query(20, le=100, description="Number of items to return"),
    offset: int = Query(0, description="Number of items to skip")
) -> Any:
    """
    List available items with filtering and search
    """
    query = db.query(Item).filter(
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    )
    
    # Exclude current user's items if logged in
    if current_user:
        query = query.filter(Item.owner_id != current_user.id)
    
    # Apply filters
    if category_id:
        query = query.filter(Item.category_id == category_id)
    
    if size:
        query = query.filter(Item.size == size)
    
    if condition:
        query = query.filter(Item.condition == condition)
    
    if min_points:
        query = query.filter(Item.points_value >= min_points)
    
    if max_points:
        query = query.filter(Item.points_value <= max_points)
    
    if brand:
        query = query.filter(Item.brand.ilike(f"%{brand}%"))
    
    if color:
        query = query.filter(Item.color.ilike(f"%{color}%"))
    
    if search:
        search_filter = or_(
            Item.title.ilike(f"%{search}%"),
            Item.description.ilike(f"%{search}%"),
            Item.brand.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Apply sorting
    if sort_by == "points_value":
        order_column = Item.points_value
    elif sort_by == "title":
        order_column = Item.title
    else:  # default to created_at
        order_column = Item.created_at
    
    if sort_order == "asc":
        query = query.order_by(order_column)
    else:
        query = query.order_by(desc(order_column))
    
    items = query.offset(offset).limit(limit).all()
    
    return items


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> Any:
    """
    Get item details
    """
    item = db.query(Item).filter(Item.id == item_id, Item.is_active == True).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item_update: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update item (only by owner)
    """
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.owner_id == current_user.id,
        Item.is_active == True
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or you don't have permission to edit it"
        )
    
    # Check if item can be updated (not in pending/completed swaps)
    if item.status in [ItemStatus.PENDING_SWAP.value, ItemStatus.SWAPPED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update item that is involved in active swaps"
        )
    
    # Update item fields
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return item


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete/deactivate item (only by owner)
    """
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.owner_id == current_user.id,
        Item.is_active == True
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or you don't have permission to delete it"
        )
    
    # Check if item can be deleted (not in pending/completed swaps)
    if item.status in [ItemStatus.PENDING_SWAP.value, ItemStatus.SWAPPED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete item that is involved in active swaps"
        )
    
    # Soft delete by deactivating
    item.is_active = False
    item.status = ItemStatus.WITHDRAWN.value
    
    db.commit()
    
    return {"message": "Item successfully deleted"}


@router.get("/categories/", response_model=List[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    include_inactive: bool = Query(False, description="Include inactive categories")
) -> Any:
    """
    List all categories
    """
    query = db.query(Category)
    
    if not include_inactive:
        query = query.filter(Category.is_active == True)
    
    categories = query.order_by(Category.name).all()
    
    return categories


@router.get("/categories/{category_id}/items", response_model=List[ItemPublic])
def list_category_items(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    limit: int = Query(20, le=100, description="Number of items to return"),
    offset: int = Query(0, description="Number of items to skip")
) -> Any:
    """
    List items in a specific category
    """
    # Verify category exists
    category = db.query(Category).filter(Category.id == category_id, Category.is_active == True).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    query = db.query(Item).filter(
        Item.category_id == category_id,
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    )
    
    # Exclude current user's items if logged in
    if current_user:
        query = query.filter(Item.owner_id != current_user.id)
    
    items = query.order_by(desc(Item.created_at)).offset(offset).limit(limit).all()
    
    return items