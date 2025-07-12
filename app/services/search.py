# app/services/search.py
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc, case
from app.models import Item, Category, User, ItemStatus
import re


class SearchService:
    """Advanced search service for items with ranking and filters"""
    
    @staticmethod
    def normalize_search_query(query: str) -> List[str]:
        """Normalize and tokenize search query"""
        if not query:
            return []
        
        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^\w\s]', ' ', query.lower())
        
        # Split into tokens and remove empty strings
        tokens = [token.strip() for token in normalized.split() if token.strip()]
        
        return tokens
    
    @staticmethod
    def build_search_filters(
        db: Session,
        search_query: Optional[str] = None,
        category_id: Optional[int] = None,
        size: Optional[str] = None,
        condition: Optional[str] = None,
        min_points: Optional[int] = None,
        max_points: Optional[int] = None,
        brand: Optional[str] = None,
        color: Optional[str] = None,
        material: Optional[str] = None,
        tags: Optional[List[str]] = None,
        location: Optional[str] = None,
        shipping_available: Optional[bool] = None,
        exclude_user_id: Optional[int] = None
    ):
        """Build complex search query with filters and ranking"""
        
        # Base query for available items
        query = db.query(Item).filter(
            Item.status == ItemStatus.AVAILABLE.value,
            Item.is_active == True
        )
        
        # Exclude specific user's items (usually current user)
        if exclude_user_id:
            query = query.filter(Item.owner_id != exclude_user_id)
        
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
        
        if shipping_available is not None:
            query = query.filter(Item.shipping_available == shipping_available)
        
        # Tag filtering (assuming tags is stored as array or comma-separated)
        if tags:
            tag_conditions = []
            for tag in tags:
                # Assuming tags are stored as JSON array or comma-separated string
                tag_conditions.append(Item.tags.ilike(f"%{tag}%"))
            query = query.filter(or_(*tag_conditions))
        
        # Text search with ranking
        if search_query:
            search_tokens = SearchService.normalize_search_query(search_query)
            
            if search_tokens:
                # Create search conditions with ranking
                search_conditions = []
                rank_conditions = []
                
                for token in search_tokens:
                    token_pattern = f"%{token}%"
                    
                    # Search in multiple fields
                    token_condition = or_(
                        Item.title.ilike(token_pattern),
                        Item.description.ilike(token_pattern),
                        Item.brand.ilike(token_pattern),
                        Item.tags.ilike(token_pattern) if Item.tags else False
                    )
                    search_conditions.append(token_condition)
                    
                    # Ranking: title matches score higher than description
                    rank_condition = case(
                        (Item.title.ilike(token_pattern), 3),  # Title match = 3 points
                        (Item.brand.ilike(token_pattern), 2),  # Brand match = 2 points
                        (Item.description.ilike(token_pattern), 1),  # Description = 1 point
                        else_=0
                    )
                    rank_conditions.append(rank_condition)
                
                # Apply search conditions (OR for flexibility)
                query = query.filter(or_(*search_conditions))
                
                # Add ranking score
                ranking_score = sum(rank_conditions)
                query = query.add_columns(ranking_score.label('search_rank'))
                
                # Order by relevance then by recency
                query = query.order_by(
                    desc('search_rank'),
                    desc(Item.created_at)
                )
            else:
                # No search terms, just order by recency
                query = query.order_by(desc(Item.created_at))
        else:
            # No search query, order by recency
            query = query.order_by(desc(Item.created_at))
        
        return query
    
    @staticmethod
    def search_items(
        db: Session,
        search_query: Optional[str] = None,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
        exclude_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive item search with filters and pagination
        
        Returns:
            - items: List of matching items
            - total_count: Total number of matching items
            - search_metadata: Information about the search
        """
        
        filters = filters or {}
        
        # Build the search query
        query = SearchService.build_search_filters(
            db=db,
            search_query=search_query,
            exclude_user_id=exclude_user_id,
            **filters
        )
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination
        items_query = query.offset(offset).limit(limit)
        
        # Execute query
        if search_query and SearchService.normalize_search_query(search_query):
            # If we have search ranking, extract items and scores
            results = items_query.all()
            items = []
            search_scores = []
            
            for result in results:
                if hasattr(result, 'Item'):
                    # Result is a tuple with Item and search_rank
                    items.append(result.Item)
                    search_scores.append(getattr(result, 'search_rank', 0))
                else:
                    # Result is just an Item
                    items.append(result)
                    search_scores.append(0)
        else:
            # No search ranking, just get items
            items = items_query.all()
            search_scores = [0] * len(items)
        
        # Prepare search metadata
        search_metadata = {
            "query": search_query,
            "total_results": total_count,
            "page_size": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count,
            "filters_applied": {k: v for k, v in filters.items() if v is not None},
            "search_tokens": SearchService.normalize_search_query(search_query) if search_query else []
        }
        
        return {
            "items": items,
            "search_scores": search_scores,
            "total_count": total_count,
            "search_metadata": search_metadata
        }
    
    @staticmethod
    def get_search_suggestions(db: Session, partial_query: str, limit: int = 10) -> Dict[str, List[str]]:
        """Get search suggestions based on partial query"""
        
        if len(partial_query) < 2:
            return {"suggestions": []}
        
        pattern = f"%{partial_query.lower()}%"
        
        # Get suggestions from different fields
        title_suggestions = db.query(Item.title).filter(
            Item.title.ilike(pattern),
            Item.status == ItemStatus.AVAILABLE.value,
            Item.is_active == True
        ).distinct().limit(limit//3).all()
        
        brand_suggestions = db.query(Item.brand).filter(
            Item.brand.ilike(pattern),
            Item.brand.isnot(None),
            Item.status == ItemStatus.AVAILABLE.value,
            Item.is_active == True
        ).distinct().limit(limit//3).all()
        
        category_suggestions = db.query(Category.name).filter(
            Category.name.ilike(pattern),
            Category.is_active == True
        ).distinct().limit(limit//3).all()
        
        # Flatten and combine suggestions
        suggestions = []
        suggestions.extend([item[0] for item in title_suggestions])
        suggestions.extend([brand[0] for brand in brand_suggestions])
        suggestions.extend([cat[0] for cat in category_suggestions])
        
        # Remove duplicates and limit
        unique_suggestions = list(dict.fromkeys(suggestions))[:limit]
        
        return {
            "suggestions": unique_suggestions,
            "categories": [cat[0] for cat in category_suggestions],
            "brands": [brand[0] for brand in brand_suggestions],
            "titles": [item[0] for item in title_suggestions]
        }
    
    @staticmethod
    def get_popular_searches(db: Session, limit: int = 10) -> List[str]:
        """Get popular search terms (this would typically come from search analytics)"""
        
        # For now, return popular categories and brands
        popular_categories = db.query(Category.name).join(Item).filter(
            Category.is_active == True,
            Item.status == ItemStatus.AVAILABLE.value
        ).group_by(Category.name).order_by(
            desc(func.count(Item.id))
        ).limit(limit//2).all()
        
        popular_brands = db.query(Item.brand).filter(
            Item.brand.isnot(None),
            Item.status == ItemStatus.AVAILABLE.value,
            Item.is_active == True
        ).group_by(Item.brand).order_by(
            desc(func.count(Item.id))
        ).limit(limit//2).all()
        
        popular = []
        popular.extend([cat[0] for cat in popular_categories])
        popular.extend([brand[0] for brand in popular_brands])
        
        return popular[:limit]
    
    @staticmethod
    def get_recommended_items(
        db: Session, 
        user_id: int, 
        limit: int = 10
    ) -> List[Item]:
        """Get recommended items for a user based on their activity"""
        
        # Simple recommendation: items from categories user has shown interest in
        user_categories = db.query(Item.category_id).filter(
            Item.owner_id == user_id
        ).distinct().subquery()
        
        # Get items from those categories that are not the user's
        recommended = db.query(Item).filter(
            Item.category_id.in_(user_categories),
            Item.owner_id != user_id,
            Item.status == ItemStatus.AVAILABLE.value,
            Item.is_active == True
        ).order_by(desc(Item.created_at)).limit(limit).all()
        
        # If not enough recommendations, fill with recent popular items
        if len(recommended) < limit:
            remaining = limit - len(recommended)
            recent_popular = db.query(Item).filter(
                Item.owner_id != user_id,
                Item.status == ItemStatus.AVAILABLE.value,
                Item.is_active == True
            ).order_by(desc(Item.created_at)).limit(remaining).all()
            
            recommended.extend(recent_popular)
        
        return recommended