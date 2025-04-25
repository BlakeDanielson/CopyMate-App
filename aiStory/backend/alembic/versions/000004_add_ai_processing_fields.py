"""add AI processing fields to photo

Revision ID: 000004_add_ai_processing_fields
Revises: 000003_add_photos_table
Create Date: 2025-04-22 20:58:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '000004_add_ai_processing_fields'
down_revision = '000003_add_photos_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create Enum for AI processing status
    ai_processing_status_enum = sa.Enum(
        'pending', 'processing', 'completed', 'failed',
        name='ai_processing_status'
    )
    ai_processing_status_enum.create(op.get_bind())
    
    # Add the AI processing fields
    op.add_column('photo', sa.Column('ai_processing_status', sa.String(), 
                                    nullable=False, server_default='pending'))
    op.add_column('photo', sa.Column('ai_error_message', sa.String(), nullable=True))
    op.add_column('photo', sa.Column('ai_provider_used', sa.String(), nullable=True))
    
    # Add JSON column, with handling for different DB types
    try:
        # Try PostgreSQL JSONB first
        op.add_column('photo', sa.Column('ai_results', postgresql.JSONB(), nullable=True))
    except Exception:
        # Fall back to regular JSON for other databases
        op.add_column('photo', sa.Column('ai_results', sa.JSON(), nullable=True))
    
    # Create an index on the AI processing status
    op.create_index(op.f('ix_photo_ai_processing_status'), 'photo', ['ai_processing_status'], unique=False)


def downgrade() -> None:
    # Drop the index
    op.drop_index(op.f('ix_photo_ai_processing_status'), table_name='photo')
    
    # Drop the columns
    op.drop_column('photo', 'ai_results')
    op.drop_column('photo', 'ai_provider_used')
    op.drop_column('photo', 'ai_error_message')
    op.drop_column('photo', 'ai_processing_status')
    
    # Drop the enum
    ai_processing_status_enum = sa.Enum(
        'pending', 'processing', 'completed', 'failed',
        name='ai_processing_status'
    )
    ai_processing_status_enum.drop(op.get_bind())