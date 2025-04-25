"""Order model for the application."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSONB
from sqlalchemy.sql import text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class OrderStatus(str, Enum):
    """Enum for order status values."""
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    FULFILLED = "fulfilled"
    SHIPPED = "shipped"
    FAILED = "failed"


class Order(Base):
    """Order model for storing purchase information."""
    
    __tablename__ = "orders"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    
    # Foreign key relationship with User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Foreign key relationship with Story
    story_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("stories.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Product information
    product_type: Mapped[str] = mapped_column(
        String, 
        nullable=False,
        index=True
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String, 
        default=OrderStatus.PENDING_PAYMENT.value,
        nullable=False,
        index=True
    )
    
    # Payment information
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    
    # Shipping information
    shipping_address: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, 
        nullable=True,
        index=True
    )
    
    # Payment processing
    payment_provider: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    payment_intent_id: Mapped[Optional[str]] = mapped_column(
        String, 
        nullable=True,
        unique=True,
        index=True
    )
    
    # Print-on-demand provider details
    pod_provider: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pod_order_id: Mapped[Optional[str]] = mapped_column(
        String, 
        nullable=True,
        index=True
    )
    tracking_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Timestamps for order lifecycle
    paid_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    fulfilled_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    shipped_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    story = relationship("Story", back_populates="orders")
    
    def __repr__(self) -> str:
        """String representation of the Order model."""
        return f"<Order {self.id} - {self.product_type} - {self.status}>"