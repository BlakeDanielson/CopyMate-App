"""Tests for the Order model."""
import uuid
from datetime import datetime
from typing import Dict, Any

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from models.user import User
from models.story import Story
from models.order import Order, OrderStatus
from tests.test_database import test_db

# Helper function to create test user and story
async def create_test_data(session):
    """Create and return a test user and story for use in tests."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password="fakehashedpassword"
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    # Create a basic story for testing
    story = Story(
        user_id=user.id,
        child_name="Test Child",
        child_age=8,
        story_theme="space_adventure",
        protagonist_photo_id=uuid.uuid4()  # Mock a photo ID
    )
    
    session.add(story)
    await session.commit()
    await session.refresh(story)
    
    return user, story


class TestOrderModel:
    """Test suite for the Order model."""
    
    @pytest.mark.asyncio
    async def test_order_model_attributes(self, test_db):
        """Test that the Order model has the expected attributes."""
        # Create test data
        user, story = await create_test_data(test_db)
        
        # Create an order instance
        order = Order(
            user_id=user.id,
            story_id=story.id,
            product_type="hardcover_book",
            amount=1999,  # $19.99
            currency="usd"
        )
        
        test_db.add(order)
        await test_db.commit()
        await test_db.refresh(order)
        
        # Verify attributes
        assert order.id is not None
        assert order.user_id == user.id
        assert order.story_id == story.id
        assert order.product_type == "hardcover_book"
        assert order.status == OrderStatus.PENDING_PAYMENT.value
        assert order.amount == 1999
        assert order.currency == "usd"
        assert order.shipping_address is None
        assert order.payment_provider is None
        assert order.payment_intent_id is None
        assert order.pod_provider is None
        assert order.pod_order_id is None
        assert order.tracking_number is None
        assert order.paid_at is None
        assert order.fulfilled_at is None
        assert order.shipped_at is None
        assert order.created_at is not None
        assert order.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_order_relationships(self, test_db):
        """Test that Order has the correct relationships with User and Story."""
        # Create test data
        user, story = await create_test_data(test_db)
        
        # Create an order instance
        order = Order(
            user_id=user.id,
            story_id=story.id,
            product_type="hardcover_book",
            amount=1999,
            currency="usd"
        )
        
        test_db.add(order)
        await test_db.commit()
        await test_db.refresh(order)
        
        # Check relationships
        assert order.user.id == user.id
        assert order.story.id == story.id
        
    @pytest.mark.asyncio
    async def test_order_required_fields(self, test_db):
        """Test that required fields are enforced."""
        # Attempt to create an order without required fields
        order = Order()
        test_db.add(order)
        
        # Expect an integrity error
        with pytest.raises(IntegrityError):
            await test_db.commit()
        
        await test_db.rollback()
        
    @pytest.mark.asyncio
    async def test_order_to_dict(self, test_db):
        """Test the to_dict method returns a dictionary with all attributes."""
        # Create test data
        user, story = await create_test_data(test_db)
        
        # Create an order with required attributes
        order = Order(
            user_id=user.id,
            story_id=story.id,
            product_type="hardcover_book",
            amount=1999,
            currency="usd"
        )
        
        test_db.add(order)
        await test_db.commit()
        await test_db.refresh(order)
        
        # Convert to dictionary
        order_dict = order.to_dict()
        
        # Check that it's a dictionary
        assert isinstance(order_dict, dict)
        
        # Check that all required attributes are in the dictionary
        assert "id" in order_dict
        assert "user_id" in order_dict
        assert "story_id" in order_dict
        assert "product_type" in order_dict
        assert "status" in order_dict
        assert "amount" in order_dict
        assert "currency" in order_dict