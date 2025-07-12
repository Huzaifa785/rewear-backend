from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime
from app.models import SwapType, SwapStatus


class SwapBase(BaseModel):
    """Base swap schema"""
    requester_message: Optional[str] = None


class SwapCreate(SwapBase):
    """Schema for creating a swap request"""
    item_id: int
    swap_type: str
    offered_item_id: Optional[int] = None  # For direct swaps
    points_offered: Optional[int] = None   # For points redemption

    @validator('swap_type')
    def validate_swap_type(cls, v):
        valid_types = [swap_type.value for swap_type in SwapType]
        if v not in valid_types:
            raise ValueError(f'Swap type must be one of: {", ".join(valid_types)}')
        return v

    @validator('offered_item_id', 'points_offered')
    def validate_swap_details(cls, v, values):
        swap_type = values.get('swap_type')
        if swap_type == SwapType.DIRECT_SWAP.value:
            if 'offered_item_id' in values and not values.get('offered_item_id'):
                raise ValueError('offered_item_id is required for direct swaps')
        elif swap_type == SwapType.POINTS_REDEMPTION.value:
            if 'points_offered' in values and not values.get('points_offered'):
                raise ValueError('points_offered is required for points redemption')
        return v


class SwapUpdate(BaseModel):
    """Schema for updating swap status"""
    status: str
    owner_response: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = [status.value for status in SwapStatus]
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class UserPublic(BaseModel):
    """Public user information (for swaps, etc.)"""
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


class ItemSummary(BaseModel):
    """Brief item summary for swaps"""
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


class SwapResponse(SwapBase):
    """Schema for swap responses"""
    id: int
    requester_id: int
    item_id: int
    item_owner_id: int
    swap_type: str
    status: str
    offered_item_id: Optional[int] = None
    points_offered: Optional[int] = None
    owner_response: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Nested relationships
    requester: UserPublic
    item_owner: UserPublic
    item: ItemSummary
    offered_item: Optional[ItemSummary] = None
    
    class Config:
        from_attributes = True


class SwapSummary(BaseModel):
    """Brief swap summary for lists"""
    id: int
    swap_type: str
    status: str
    points_offered: Optional[int] = None
    created_at: datetime
    
    # Basic item info
    item: ItemSummary
    offered_item: Optional[ItemSummary] = None
    
    class Config:
        from_attributes = True


class PointTransactionResponse(BaseModel):
    """Schema for point transaction responses"""
    id: int
    user_id: int
    amount: int
    transaction_type: str
    description: str
    swap_id: Optional[int] = None
    item_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PointTransactionSummary(BaseModel):
    """Brief point transaction summary"""
    id: int
    amount: int
    transaction_type: str
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True