"""Add orders table

Revision ID: 000006
Revises: 000005_add_stories_story_pages
Create Date: 2025-04-22 22:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '000006'
down_revision: str = '000005_add_stories_story_pages'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('story_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('stories.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('product_type', sa.String(), nullable=False, index=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending_payment', index=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('shipping_address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('payment_provider', sa.String(), nullable=True),
        sa.Column('payment_intent_id', sa.String(), nullable=True, unique=True),
        sa.Column('pod_provider', sa.String(), nullable=True),
        sa.Column('pod_order_id', sa.String(), nullable=True, index=True),
        sa.Column('tracking_number', sa.String(), nullable=True),
        sa.Column('paid_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('fulfilled_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('shipped_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    
    # Create GIN index on shipping_address JSONB field for efficient querying
    op.create_index('ix_orders_shipping_address', 'orders', ['shipping_address'], postgresql_using='gin')


def downgrade() -> None:
    # Drop orders table
    op.drop_index('ix_orders_shipping_address', table_name='orders')
    op.drop_table('orders')