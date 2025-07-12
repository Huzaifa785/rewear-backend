from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Category Information
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Category Metadata
    icon_name = Column(String(50), nullable=True)  # For UI icons
    color_code = Column(String(7), nullable=True)  # Hex color code
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    items = relationship("Item", back_populates="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', slug='{self.slug}')>"
    
    @property
    def item_count(self):
        """Get count of active items in this category"""
        return self.items.filter_by(is_active=True).count()