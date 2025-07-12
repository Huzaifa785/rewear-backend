from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ItemCondition(enum.Enum):
    """Item condition enumeration"""
    NEW_WITH_TAGS = "new_with_tags"
    LIKE_NEW = "like_new"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class ItemStatus(enum.Enum):
    """Item availability status"""
    AVAILABLE = "available"
    PENDING_SWAP = "pending_swap"
    SWAPPED = "swapped"
    WITHDRAWN = "withdrawn"
    UNDER_REVIEW = "under_review"
    REJECTED = "rejected"


class ItemSize(enum.Enum):
    """Clothing size enumeration"""
    XXS = "xxs"
    XS = "xs"
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"
    XXL = "xxl"
    XXXL = "xxxl"
    ONE_SIZE = "one_size"
    
    # Numeric sizes for shoes, etc.
    SIZE_6 = "6"
    SIZE_7 = "7"
    SIZE_8 = "8"
    SIZE_9 = "9"
    SIZE_10 = "10"
    SIZE_11 = "11"
    SIZE_12 = "12"


class Item(Base):
    __tablename__ = "items"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    brand = Column(String(100), nullable=True, index=True)
    
    # Classification (using String instead of Enum for PostgreSQL compatibility)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    size = Column(String(50), nullable=False, index=True)  # Store enum value as string
    condition = Column(String(50), nullable=False, index=True)  # Store enum value as string
    
    # Ownership & Status
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(50), default="available", nullable=False, index=True)  # Store enum value as string
    
    # Images (array of image URLs/paths)
    image_urls = Column(ARRAY(String), nullable=True)
    primary_image_url = Column(String(500), nullable=True)
    
    # Points & Pricing
    points_value = Column(Integer, nullable=False, index=True)
    original_price = Column(Integer, nullable=True)  # In cents
    
    # Additional Details
    color = Column(String(50), nullable=True, index=True)
    material = Column(String(100), nullable=True)
    tags = Column(ARRAY(String), nullable=True)  # e.g., ["vintage", "designer", "casual"]
    
    # Location (for local swaps)
    pickup_location = Column(String(200), nullable=True)
    shipping_available = Column(Boolean, default=True, nullable=False)
    
    # Moderation
    is_active = Column(Boolean, default=True, nullable=False)
    admin_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="items")
    category = relationship("Category", back_populates="items")
    swaps = relationship("Swap", foreign_keys="Swap.item_id", back_populates="item", lazy="dynamic")
    offered_in_swaps = relationship("Swap", foreign_keys="Swap.offered_item_id", lazy="dynamic")

    def __repr__(self):
        return f"<Item(id={self.id}, title='{self.title}', owner_id={self.owner_id}, status='{self.status}')>"
    
    @property
    def size_enum(self):
        """Get size as enum"""
        try:
            return ItemSize(self.size)
        except ValueError:
            return None
    
    @property
    def condition_enum(self):
        """Get condition as enum"""
        try:
            return ItemCondition(self.condition)
        except ValueError:
            return None
    
    @property
    def status_enum(self):
        """Get status as enum"""
        try:
            return ItemStatus(self.status)
        except ValueError:
            return None
    
    @property
    def is_available(self):
        """Check if item is available for swapping"""
        return self.status == ItemStatus.AVAILABLE.value and self.is_active
    
    @property
    def primary_image(self):
        """Get primary image URL or first image if primary not set"""
        if self.primary_image_url:
            return self.primary_image_url
        elif self.image_urls and len(self.image_urls) > 0:
            return self.image_urls[0]
        return None
    
    @property
    def formatted_price(self):
        """Get formatted original price"""
        if self.original_price:
            return f"${self.original_price / 100:.2f}"
        return None