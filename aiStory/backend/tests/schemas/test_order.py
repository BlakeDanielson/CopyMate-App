"""Tests for Order schema validation."""
import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from schemas.order import OrderBase, OrderCreate, OrderRead, OrderUpdate
from models.order import OrderStatus


class TestOrderSchema:
    """Test suite for Order schemas."""
    
    def test_order_base_required_fields(self):
        """Test that OrderBase requires product_type, amount, and currency."""
        # Should fail without required fields
        with pytest.raises(ValidationError):
            OrderBase()
        
        # Should fail with partial fields
        with pytest.raises(ValidationError):
            OrderBase(product_type="hardcover_book")
            
        # Should fail with partial fields
        with pytest.raises(ValidationError):
            OrderBase(product_type="hardcover_book", amount=1999)
        
        # Should succeed with all required fields
        order_data = {
            "product_type": "hardcover_book",
            "amount": 1999,
            "currency": "usd"
        }
        order = OrderBase(**order_data)
        assert order.product_type == "hardcover_book"
        assert order.amount == 1999
        assert order.currency == "usd"
    
    def test_order_base_field_validation(self):
        """Test validation of fields in OrderBase."""
        # Test amount validation (must be positive)
        with pytest.raises(ValidationError):
            OrderBase(product_type="hardcover_book", amount=-100, currency="usd")
        
        # Test currency validation (must be 3 characters)
        with pytest.raises(ValidationError):
            OrderBase(product_type="hardcover_book", amount=1999, currency="usdd")
            
        with pytest.raises(ValidationError):
            OrderBase(product_type="hardcover_book", amount=1999, currency="us")
    
    def test_order_create_required_fields(self):
        """Test that OrderCreate requires user_id and story_id in addition to base fields."""
        # Should fail without user_id and story_id
        with pytest.raises(ValidationError):
            OrderCreate(product_type="hardcover_book", amount=1999, currency="usd")
        
        # Should fail with only user_id
        with pytest.raises(ValidationError):
            OrderCreate(
                product_type="hardcover_book",
                amount=1999,
                currency="usd",
                user_id=uuid.uuid4()
            )
        
        # Should succeed with all required fields
        user_id = uuid.uuid4()
        story_id = uuid.uuid4()
        order = OrderCreate(
            product_type="hardcover_book",
            amount=1999,
            currency="usd",
            user_id=user_id,
            story_id=story_id
        )
        assert order.product_type == "hardcover_book"
        assert order.amount == 1999
        assert order.currency == "usd"
        assert order.user_id == user_id
        assert order.story_id == story_id
        assert order.status == OrderStatus.PENDING_PAYMENT.value  # Default value
    
    def test_order_update_schema(self):
        """Test OrderUpdate schema."""
        # Empty update should be valid
        update = OrderUpdate()
        assert update.status is None
        assert update.shipping_address is None
        
        # Update with valid status
        update = OrderUpdate(status=OrderStatus.PAID.value)
        assert update.status == OrderStatus.PAID.value
        
        # Update with invalid status
        with pytest.raises(ValidationError):
            OrderUpdate(status="invalid_status")
            
        # Update with shipping address
        shipping_address = {
            "name": "John Doe",
            "address1": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postal_code": "12345",
            "country": "US"
        }
        update = OrderUpdate(shipping_address=shipping_address)
        assert update.shipping_address == shipping_address
    
    def test_order_read_fields(self):
        """Test that OrderRead has all expected fields."""
        user_id = uuid.uuid4()
        story_id = uuid.uuid4()
        order_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        
        order_data = {
            "id": order_id,
            "user_id": user_id,
            "story_id": story_id,
            "product_type": "hardcover_book",
            "status": OrderStatus.PENDING_PAYMENT.value,
            "amount": 1999,
            "currency": "usd",
            "created_at": now,
            "updated_at": now
        }
        
        order = OrderRead(**order_data)
        
        # Verify required fields
        assert order.id == order_id
        assert order.user_id == user_id
        assert order.story_id == story_id
        assert order.product_type == "hardcover_book"
        assert order.status == OrderStatus.PENDING_PAYMENT.value
        assert order.amount == 1999
        assert order.currency == "usd"
        
        # Verify optional fields have correct default values
        assert order.shipping_address is None
        assert order.payment_provider is None
        assert order.payment_intent_id is None
        assert order.pod_provider is None
        assert order.pod_order_id is None
        assert order.tracking_number is None
        assert order.paid_at is None
        assert order.fulfilled_at is None
        assert order.shipped_at is None
        
        # Verify timestamps
        assert order.created_at == now
        assert order.updated_at == now
    
    def test_order_status_validation(self):
        """Test validation of order status."""
        # Should accept valid statuses
        for status in [status.value for status in OrderStatus]:
            order = OrderCreate(
                product_type="hardcover_book",
                amount=1999,
                currency="usd",
                user_id=uuid.uuid4(),
                story_id=uuid.uuid4(),
                status=status
            )
            assert order.status == status
        
        # Should reject invalid statuses
        with pytest.raises(ValidationError):
            OrderCreate(
                product_type="hardcover_book",
                amount=1999,
                currency="usd",
                user_id=uuid.uuid4(),
                story_id=uuid.uuid4(),
                status="invalid_status"
            )