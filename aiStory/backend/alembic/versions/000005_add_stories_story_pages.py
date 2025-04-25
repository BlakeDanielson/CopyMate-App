"""Add stories and story_pages tables

Revision ID: 000005
Revises: 000004_add_ai_processing_fields
Create Date: 2025-04-22 22:32:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = '000005'
down_revision = '000004_add_ai_processing_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create stories and story_pages tables."""
    # Create stories table
    op.create_table(
        'stories',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('child_name', sa.String(), nullable=False),
        sa.Column('child_age', sa.Integer(), nullable=False),
        sa.Column('story_theme', sa.String(), nullable=False, index=True),
        sa.Column('protagonist_photo_id', UUID(as_uuid=True), sa.ForeignKey('photos.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default="'pending'", index=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Create story_pages table
    op.create_table(
        'story_pages',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('story_id', UUID(as_uuid=True), sa.ForeignKey('stories.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('page_number', sa.Integer(), nullable=False, index=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('base_image_key', sa.String(), nullable=True),
        sa.Column('personalized_image_key', sa.String(), nullable=True),
        sa.Column('text_generation_status', sa.String(), nullable=True, server_default="'pending'", index=True),
        sa.Column('image_generation_status', sa.String(), nullable=True, server_default="'pending'", index=True),
        sa.Column('personalization_status', sa.String(), nullable=True, server_default="'pending'", index=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('story_id', 'page_number', name='uix_story_page_number')
    )


def downgrade() -> None:
    """Drop stories and story_pages tables."""
    op.drop_table('story_pages')
    op.drop_table('stories')