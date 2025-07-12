# app/api/routes/search.py
from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.api.deps import get_db, get_optional_current_user
from app.models import User, Item, Category, ItemStatus
from app.services.search import SearchService
from app.schemas import ItemPublic

router = APIRouter()


@router.get("/items", response_model=Dict[str, Any])
def advanced_search_items(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    
    # Search query
    q: Optional[str] = Query(None, description="Search query"),
    
    # Category and basic filters
    category_id: Optional[int] = Query(None, description="Filter by category"),
    size: Optional[str] = Query(None, description="Filter by size"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    
    # Price/Points filters
    min_points: Optional[int] = Query(None, description="Minimum points value"),
    max_points: Optional[int] = Query(None, description="Maximum points value"),
    
    # Item attributes
    brand: Optional[str] = Query(None, description="Filter by brand"),
    color: Optional[str] = Query(None, description="Filter by color"),
    material: Optional[str] = Query(None, description="Filter by material"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    
    # Location
    location: Optional[str] = Query(None, description="Filter by pickup location"),
    
    # Pagination
    limit: int = Query(20, le=100, description="Number of items to return"),
    offset: int = Query(0, description="Number of items to skip"),
    
    # Additional options
    include_shipping: Optional[bool] = Query(None, description="Include items with shipping"),
    sort_by: str = Query("relevance", description="Sort by: relevance, date, points_asc, points_desc")
) -> Any:
    """
    Advanced search for items with comprehensive filtering and ranking
    """
    
    # Parse tags if provided
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    # Build filters dictionary
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
    
    # Add shipping filter
    if include_shipping is not None:
        filters["shipping_available"] = include_shipping
    
    # Exclude current user's items if logged in
    exclude_user_id = current_user.id if current_user else None
    
    # Perform search
    search_results = SearchService.search_items(
        db=db,
        search_query=q,
        filters=filters,
        limit=limit,
        offset=offset,
        exclude_user_id=exclude_user_id
    )
    
    # Apply sorting if not relevance-based
    items = search_results["items"]
    if sort_by != "relevance" and not q:
        if sort_by == "date":
            items = sorted(items, key=lambda x: x.created_at, reverse=True)
        elif sort_by == "points_asc":
            items = sorted(items, key=lambda x: x.points_value)
        elif sort_by == "points_desc":
            items = sorted(items, key=lambda x: x.points_value, reverse=True)
    
    return {
        "items": items,
        "pagination": {
            "total_count": search_results["total_count"],
            "limit": limit,
            "offset": offset,
            "has_more": search_results["search_metadata"]["has_more"],
            "current_page": (offset // limit) + 1,
            "total_pages": (search_results["total_count"] + limit - 1) // limit
        },
        "search_metadata": search_results["search_metadata"],
        "filters_applied": search_results["search_metadata"]["filters_applied"]
    }


@router.get("/suggestions")
def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Partial search query"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get search suggestions for autocomplete
    """
    suggestions = SearchService.get_search_suggestions(db, q)
    return suggestions


@router.get("/popular")
def get_popular_searches(
    db: Session = Depends(get_db),
    limit: int = Query(10, le=20, description="Number of popular terms to return")
) -> Any:
    """
    Get popular search terms and trending items
    """
    popular_terms = SearchService.get_popular_searches(db, limit)
    
    return {
        "popular_searches": popular_terms,
        "trending_categories": popular_terms[:limit//2],
        "trending_brands": popular_terms[limit//2:]
    }


@router.get("/recommendations")
def get_personalized_recommendations(
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, le=20, description="Number of recommendations")
) -> Any:
    """
    Get personalized item recommendations for the user
    """
    if not current_user:
        # Return popular items for anonymous users
        popular_items = SearchService.search_items(
            db=db,
            limit=limit,
            filters={}
        )["items"]
        
        return {
            "recommended_items": popular_items,
            "recommendation_type": "popular",
            "message": "Popular items on ReWear"
        }
    
    # Get personalized recommendations
    recommended_items = SearchService.get_recommended_items(
        db=db,
        user_id=current_user.id,
        limit=limit
    )
    
    return {
        "recommended_items": recommended_items,
        "recommendation_type": "personalized",
        "message": f"Recommended for {current_user.username}"
    }


@router.get("/filters/options")
def get_filter_options(
    db: Session = Depends(get_db)
) -> Any:
    """
    Get available filter options for the search interface
    """
    
    # Get unique values for filter dropdowns
    sizes = db.query(distinct(Item.size)).filter(
        Item.size.isnot(None),
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    ).all()
    
    conditions = db.query(distinct(Item.condition)).filter(
        Item.condition.isnot(None),
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    ).all()
    
    brands = db.query(distinct(Item.brand)).filter(
        Item.brand.isnot(None),
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    ).order_by(Item.brand).limit(50).all()
    
    colors = db.query(distinct(Item.color)).filter(
        Item.color.isnot(None),
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    ).all()
    
    materials = db.query(distinct(Item.material)).filter(
        Item.material.isnot(None),
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    ).all()
    
    # Get categories
    categories = db.query(Category).filter(Category.is_active == True).all()
    
    # Get point ranges for slider
    point_stats = db.query(
        func.min(Item.points_value).label('min_points'),
        func.max(Item.points_value).label('max_points'),
        func.avg(Item.points_value).label('avg_points')
    ).filter(
        Item.status == ItemStatus.AVAILABLE.value,
        Item.is_active == True
    ).first()
    
    return {
        "categories": [{"id": cat.id, "name": cat.name, "slug": cat.slug} for cat in categories],
        "sizes": [size[0] for size in sizes if size[0]],
        "conditions": [condition[0] for condition in conditions if condition[0]],
        "brands": [brand[0] for brand in brands if brand[0]],
        "colors": [color[0] for color in colors if color[0]],
        "materials": [material[0] for material in materials if material[0]],
        "point_range": {
            "min": int(point_stats.min_points) if point_stats.min_points else 0,
            "max": int(point_stats.max_points) if point_stats.max_points else 1000,
            "average": int(point_stats.avg_points) if point_stats.avg_points else 100
        },
        "sort_options": [
            {"value": "relevance", "label": "Most Relevant"},
            {"value": "date", "label": "Newest First"},
            {"value": "points_asc", "label": "Lowest Points"},
            {"value": "points_desc", "label": "Highest Points"}
        ]
    }