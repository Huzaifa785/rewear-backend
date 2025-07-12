# app/api/routes/items.py - Enhanced with notifications and better search integration
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from app.api.deps import get_current_user, get_db, get_optional_current_user
from app.core.utils import calculate_item_points, award_points
from app.core.websockets import notification_service
from app.services.search import SearchService
from app.models import User, Item, Category, ItemStatus, ItemCondition, ItemSize
from app.schemas import (
    ItemCreate, ItemUpdate, ItemResponse, ItemPublic, ItemSummary,
    CategoryResponse
)

router = APIRouter()


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new item listing with enhanced validation and notifications
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
        status=ItemStatus.AVAILABLE.value  # Auto-approve for now, can add moderation later
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
    
    # 🔔 Send notification about points earned
    await notification_service.notify_points_earned(
        user_id=current_user.id,
        points=listing_points,
        reason=f"Listed new item: {item.title}"
    )
    
    # 🔔 Send approval notification (if auto-approved)
    await notification_service.notify_item_approved(
        user_id=current_user.id,
        item_data={
            "item_id": item.id,
            "title": item.title
        }
    )
    
    return item


@router.get("/", response_model=List[ItemPublic])
def list_items(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    
    # Search parameters
    q: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    size: Optional[str] = Query(None, description="Filter by size"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    min_points: Optional[int] = Query(None, description="Minimum points value"),
    max_points: Optional[int] = Query(None, description="Maximum points value"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    color: Optional[str] = Query(None, description="Filter by color"),
    material: Optional[str] = Query(None, description="Filter by material"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    location: Optional[str] = Query(None, description="Filter by location"),
    
    # Sorting and pagination
    sort_by: str = Query("created_at", description="Sort by: created_at, points_value, title, relevance"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    limit: int = Query(20, le=100, description="Number of items to return"),
    offset: int = Query(0, description="Number of items to skip"),
    
    # Additional filters
    include_shipping: Optional[bool] = Query(None, description="Include items with shipping")
) -> Any:
    """
    Enhanced item listing with integrated search and filtering
    """
    
    # Use enhanced search service if we have a search query
    if q:
        # Parse tags if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Build filters
        filters = {
            "category_id": category_id,
            "size": size,
            "condition": condition,
            "min_points": min_points,
            "max_points": max_points,
            "brand": brand,
            "color": color,
            "material": material,
            "tags": tag_list,
            "location": location
        }
        
        if include_shipping is not None:
            filters["shipping_available"] = include_shipping
        
        # Use search service
        search_results = SearchService.search_items(
            db=db,
            search_query=q,
            filters=filters,
            limit=limit,
            offset=offset,
            exclude_user_id=current_user.id if current_user else None
        )
        
        return search_results["items"]
    
    # Fallback to traditional filtering if no search query
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
        query = query.filter(Item.size.ilike(f"%{size}%"))
    
    if condition:
        query = query.filter(Item.condition.ilike(f"%{condition}%"))
    
    if min_points:
        query = query.filter(Item.points_value >= min_points)
    
    if max_points:
        query = query.filter(Item.points_value <= max_points)
    
    if brand:
        query = query.filter(Item.brand.ilike(f"%{brand}%"))
    
    if color:
        query = query.filter(Item.color.ilike(f"%{color}%"))
    
    if material:
        query = query.filter(Item.material.ilike(f"%{material}%"))
    
    if location:
        query = query.filter(Item.pickup_location.ilike(f"%{location}%"))
    
    if include_shipping is not None:
        query = query.filter(Item.shipping_available == include_shipping)
    
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        tag_conditions = []
        for tag in tag_list:
            tag_conditions.append(Item.tags.ilike(f"%{tag}%"))
        query = query.filter(or_(*tag_conditions))
    
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


@router.get("/trending")
def get_trending_items(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    limit: int = Query(10, le=50, description="Number of trending items")
) -> Any:
    """
    Get trending items based on recent swap activity and views
    """
    from sqlalchemy import func
    from app.models import Swap
    
    # Get items that have recent swap activity (indicating popularity)
    trending_query = db.query(
        Item,
        func.count(Swap.id).label('swap_count')
    ).outerjoin(Swap).filter(
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    )
    
    # Exclude current user's items
    if current_user:
        trending_query = trending_query.filter(Item.owner_id != current_user.id)
    
    # Group by item and order by swap activity and recency
    trending_items = trending_query.group_by(Item.id).order_by(
        desc('swap_count'),
        desc(Item.created_at)
    ).limit(limit).all()
    
    # Extract just the items from the query results
    items = [result[0] for result in trending_items]
    
    return {
        "trending_items": items,
        "metadata": {
            "algorithm": "swap_activity_and_recency",
            "total_items": len(items)
        }
    }


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> Any:
    """
    Get item details with enhanced information
    """
    item = db.query(Item).filter(Item.id == item_id, Item.is_active == True).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Track view (in a real app, you might want to track this in analytics)
    # For now, we'll just return the item
    
    return item


@router.get("/{item_id}/similar")
def get_similar_items(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    limit: int = Query(5, le=20, description="Number of similar items")
) -> Any:
    """
    Get items similar to the specified item
    """
    # Get the target item
    target_item = db.query(Item).filter(
        Item.id == item_id,
        Item.is_active == True
    ).first()
    
    if not target_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Find similar items based on category, brand, and size
    similar_query = db.query(Item).filter(
        Item.id != item_id,
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    )
    
    # Exclude current user's items
    if current_user:
        similar_query = similar_query.filter(Item.owner_id != current_user.id)
    
    # Prioritize by category, then brand, then size
    similar_items = similar_query.filter(
        or_(
            Item.category_id == target_item.category_id,
            Item.brand.ilike(f"%{target_item.brand}%") if target_item.brand else False,
            Item.size == target_item.size if target_item.size else False
        )
    ).order_by(
        # Exact category match gets highest priority
        desc(Item.category_id == target_item.category_id),
        # Then brand match
        desc(Item.brand.ilike(f"%{target_item.brand}%") if target_item.brand else False),
        # Then recent items
        desc(Item.created_at)
    ).limit(limit).all()
    
    return {
        "similar_items": similar_items,
        "based_on": {
            "item_id": target_item.id,
            "category": target_item.category.name,
            "brand": target_item.brand,
            "size": target_item.size
        }
    }


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item_update: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update item (only by owner) with validation
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
    include_inactive: bool = Query(False, description="Include inactive categories"),
    with_counts: bool = Query(False, description="Include item counts per category")
) -> Any:
    """
    List all categories with optional item counts
    """
    query = db.query(Category)
    
    if not include_inactive:
        query = query.filter(Category.is_active == True)
    
    categories = query.order_by(Category.name).all()
    
    if with_counts:
        # Add item counts to each category
        from sqlalchemy import func
        
        category_counts = db.query(
            Category.id,
            func.count(Item.id).label('item_count')
        ).outerjoin(Item).filter(
            Item.status == ItemStatus.AVAILABLE.value,
            Item.is_active == True
        ).group_by(Category.id).all()
        
        # Create a mapping of category_id to count
        count_map = {cat_id: count for cat_id, count in category_counts}
        
        # Add counts to category objects
        for category in categories:
            category.item_count = count_map.get(category.id, 0)
    
    return categories


@router.get("/categories/{category_id}/items", response_model=List[ItemPublic])
def list_category_items(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    sort_by: str = Query("created_at", description="Sort by: created_at, points_value, title"),
    limit: int = Query(20, le=100, description="Number of items to return"),
    offset: int = Query(0, description="Number of items to skip")
) -> Any:
    """
    List items in a specific category with enhanced sorting
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
    
    # Apply sorting
    if sort_by == "points_value":
        query = query.order_by(desc(Item.points_value))
    elif sort_by == "title":
        query = query.order_by(Item.title)
    else:  # default to created_at
        query = query.order_by(desc(Item.created_at))
    
    items = query.offset(offset).limit(limit).all()
    
    return items