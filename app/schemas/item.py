from typing import Optional, List
from pydantic import BaseModel, validator
from datetime import datetime
from app.models import ItemCondition, ItemStatus, ItemSize


class ItemBase(BaseModel):
    """Base item schema"""
    title: str
    description: str
    brand: Optional[str] = None
    size: str
    condition: str
    color: Optional[str] = None
    material: Optional[str] = None
    tags: Optional[List[str]] = None
    pickup_location: Optional[str] = None
    shipping_available: bool = True
    original_price: Optional[int] = None  # In cents

    @validator('size')
    def validate_size(cls, v):
        valid_sizes = [size.value for size in ItemSize]
        if v not in valid_sizes:
            raise ValueError(f'Size must be one of: {", ".join(valid_sizes)}')
        return v

    @validator('condition')
    def validate_condition(cls, v):
        valid_conditions = [condition.value for condition in ItemCondition]
        if v not in valid_conditions:
            raise ValueError(f'Condition must be one of: {", ".join(valid_conditions)}')
        return v

    @validator('title')
    def validate_title(cls, v):
        if len(v) < 3:
            raise ValueError('Title must be at least 3 characters long')
        if len(v) > 200:
            raise ValueError('Title must be less than 200 characters')
        return v

    @validator('description')
    def validate_description(cls, v):
        if len(v) < 10:
            raise ValueError('Description must be at least 10 characters long')
        return v


class ItemCreate(ItemBase):
    """Schema for creating an item"""
    category_id: int
    points_value: Optional[int] = None  # Will be auto-calculated if not provided


class ItemUpdate(BaseModel):
    """Schema for updating an item"""
    title: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    condition: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    tags: Optional[List[str]] = None
    pickup_location: Optional[str] = None
    shipping_available: Optional[bool] = None
    original_price: Optional[int] = None

    @validator('size')
    def validate_size(cls, v):
        if v is not None:
            valid_sizes = [size.value for size in ItemSize]
            if v not in valid_sizes:
                raise ValueError(f'Size must be one of: {", ".join(valid_sizes)}')
        return v

    @validator('condition')
    def validate_condition(cls, v):
        if v is not None:
            valid_conditions = [condition.value for condition in ItemCondition]
            if v not in valid_conditions:
                raise ValueError(f'Condition must be one of: {", ".join(valid_conditions)}')
        return v


class CategoryResponse(BaseModel):
    """Category schema for responses"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon_name: Optional[str] = None
    color_code: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Public user information (for item listings, etc.)"""
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ItemResponse(ItemBase):
    """Schema for item responses"""
    id: int
    category_id: int
    owner_id: int
    status: str
    points_value: int
    image_urls: Optional[List[str]] = None
    primary_image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    # Nested relationships
    owner: UserPublic
    category: CategoryResponse
    
    class Config:
        from_attributes = True


class ItemPublic(BaseModel):
    """Public item information for listings"""
    id: int
    title: str
    description: str
    brand: Optional[str] = None
    size: str
    condition: str
    color: Optional[str] = None
    material: Optional[str] = None
    tags: Optional[List[str]] = None
    points_value: int
    primary_image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    shipping_available: bool
    created_at: datetime
    
    # Nested relationships
    owner: UserPublic
    category: CategoryResponse
    
    class Config:
        from_attributes = True


class ItemSummary(BaseModel):
    """Brief item summary for lists"""
    id: int
    title: str
    brand: Optional[str] = None
    size: str
    condition: str
    points_value: int
    primary_image_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    """Schema for creating categories"""
    name: str
    description: Optional[str] = None
    icon_name: Optional[str] = None
    color_code: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError('Category name must be at least 2 characters long')
        if len(v) > 100:
            raise ValueError('Category name must be less than 100 characters')
        return v


class CategoryUpdate(BaseModel):
    """Schema for updating categories"""
    name: Optional[str] = None
    description: Optional[str] = None
    icon_name: Optional[str] = None
    color_code: Optional[str] = None
    is_active: Optional[bool] = None