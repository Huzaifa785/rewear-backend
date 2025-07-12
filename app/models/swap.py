from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class SwapType(enum.Enum):
    """Type of swap transaction"""
    DIRECT_SWAP = "direct_swap"      # Item for item
    POINTS_REDEMPTION = "points_redemption"  # Points for item


class SwapStatus(enum.Enum):
    """Swap request status"""
    PENDING = "pending"              # Waiting for response
    ACCEPTED = "accepted"            # Accepted, pending completion
    REJECTED = "rejected"            # Rejected by item owner
    COMPLETED = "completed"          # Successfully completed
    CANCELLED = "cancelled"          # Cancelled by requester
    EXPIRED = "expired"              # Request expired


class Swap(Base):
    __tablename__ = "swaps"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Swap Participants
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    item_owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Swap Details (using String instead of Enum)
    swap_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default="pending", nullable=False, index=True)
    
    # For Direct Swaps
    offered_item_id = Column(Integer, ForeignKey("items.id"), nullable=True, index=True)
    
    # For Points Redemption
    points_offered = Column(Integer, nullable=True)
    
    # Communication
    requester_message = Column(Text, nullable=True)
    owner_response = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Auto-expire pending requests
    responded_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_swaps")
    item_owner = relationship("User", foreign_keys=[item_owner_id], back_populates="received_swaps")
    item = relationship("Item", foreign_keys=[item_id], back_populates="swaps")
    offered_item = relationship("Item", foreign_keys=[offered_item_id])

    def __repr__(self):
        return f"<Swap(id={self.id}, requester_id={self.requester_id}, item_id={self.item_id}, status='{self.status}')>"
    
    @property
    def swap_type_enum(self):
        """Get swap type as enum"""
        try:
            return SwapType(self.swap_type)
        except ValueError:
            return None
    
    @property
    def status_enum(self):
        """Get status as enum"""
        try:
            return SwapStatus(self.status)
        except ValueError:
            return None
    
    @property
    def is_pending(self):
        """Check if swap is still pending"""
        return self.status == SwapStatus.PENDING.value
    
    @property
    def is_completed(self):
        """Check if swap is completed"""
        return self.status == SwapStatus.COMPLETED.value
    
    @property
    def is_direct_swap(self):
        """Check if this is a direct item-for-item swap"""
        return self.swap_type == SwapType.DIRECT_SWAP.value
    
    @property
    def is_points_redemption(self):
        """Check if this is a points redemption"""
        return self.swap_type == SwapType.POINTS_REDEMPTION.value


class PointTransaction(Base):
    __tablename__ = "point_transactions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Transaction Details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # Positive for earning, negative for spending
    transaction_type = Column(String(50), nullable=False, index=True)  # e.g., "signup_bonus", "item_swap", "points_redemption"
    
    # Related Records
    swap_id = Column(Integer, ForeignKey("swaps.id"), nullable=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True, index=True)
    
    # Description
    description = Column(String(200), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="point_transactions")
    swap = relationship("Swap")
    item = relationship("Item")

    def __repr__(self):
        return f"<PointTransaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, type='{self.transaction_type}')>"