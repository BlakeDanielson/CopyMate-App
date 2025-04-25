"""Schemas for Order model."""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import Field, validator

from .base import BaseSchema
from models.order import OrderStatus


class OrderBase(BaseSchema):
    """Base schema for an order."""
    
    product_type: str = Field(..., description="Identifier for the physical product (e.g., 'hardcover_book')")
    amount: int = Field(..., gt=0, description="Total price of the order in the smallest currency unit (e.g., cents)")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO currency code (e.g., 'usd')")
    status: Optional[str] = Field(
        default=OrderStatus.PENDING_PAYMENT.value,
        description="Tracks the order lifecycle"
    )
    shipping_address: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Structured shipping address details"
    )
    payment_provider: Optional[str] = Field(
        default=None, 
        description="Identifier for the payment gateway used (e.g., 'stripe')"
    )
    payment_intent_id: Optional[str] = Field(
        default=None, 
        description="The unique transaction ID from the payment provider"
    )
    pod_provider: Optional[str] = Field(
        default=None, 
        description="Identifier for the Print-on-Demand provider used (e.g., 'lulu')"
    )
    pod_order_id: Optional[str] = Field(
        default=None, 
        description="The order ID assigned by the POD provider"
    )
    tracking_number: Optional[str] = Field(
        default=None, 
        description="Shipping tracking number, provided by POD provider"
    )
    paid_at: Optional[datetime] = Field(
        default=None, 
        description="Timestamp when the payment was successfully confirmed"
    )
    fulfilled_at: Optional[datetime] = Field(
        default=None, 
        description="Timestamp when the POD provider confirmed fulfillment/production"
    )
    shipped_at: Optional[datetime] = Field(
        default=None, 
        description="Timestamp when the order was shipped by the POD provider"
    )
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status value against the enum."""
        if v is not None and v not in [status.value for status in OrderStatus]:
            raise ValueError(f"Invalid status: {v}. Must be one of {[status.value for status in OrderStatus]}")
        return v


class OrderCreate(OrderBase):
    """Schema for creating a new order."""
    
    user_id: UUID = Field(..., description="ID of the user placing the order")
    story_id: UUID = Field(..., description="ID of the story being ordered")


class OrderUpdate(BaseSchema):
    """Schema for updating an order."""
    
    status: Optional[str] = None
    shipping_address: Optional[Dict[str, Any]] = None
    payment_provider: Optional[str] = None
    payment_intent_id: Optional[str] = None
    pod_provider: Optional[str] = None
    pod_order_id: Optional[str] = None
    tracking_number: Optional[str] = None
    paid_at: Optional[datetime] = None
    fulfilled_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status value against the enum."""
        if v is not None and v not in [status.value for status in OrderStatus]:
            raise ValueError(f"Invalid status: {v}. Must be one of {[status.value for status in OrderStatus]}")
        return v


class OrderRead(OrderBase):
    """Schema for reading an order, including all fields."""
    
    id: UUID
    user_id: UUID
    story_id: UUID
    created_at: datetime
    updated_at: datetime