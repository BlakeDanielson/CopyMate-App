"""Add photos table.

Revision ID: 000003_add_photos_table
Revises: 000002_add_user_role
Create Date: 2025-04-22 18:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP


# revision identifiers, used by Alembic.
revision: str = '000003_add_photos_table'
down_revision: Union[str, None] = '000002_add_user_role'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add photos table."""
    op.create_table(
        'photos',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('storage_provider', sa.String(), nullable=False),
        sa.Column('bucket', sa.String(), nullable=True),
        sa.Column('object_key', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default=sa.text("'pending_upload'")),
        sa.Column('ai_processing_status', sa.String(), nullable=True, server_default=sa.text("'pending'")),
        sa.Column('ai_error_message', sa.Text(), nullable=True),
        sa.Column('detected_objects', JSONB(), nullable=True),
        sa.Column('detected_labels', JSONB(), nullable=True),
        sa.Column('face_details', JSONB(), nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('object_key')
    )
    
    # Create indexes
    op.create_index(op.f('ix_photos_user_id'), 'photos', ['user_id'], unique=False)
    op.create_index(op.f('ix_photos_object_key'), 'photos', ['object_key'], unique=True)
    op.create_index(op.f('ix_photos_status'), 'photos', ['status'], unique=False)
    op.create_index(op.f('ix_photos_ai_processing_status'), 'photos', ['ai_processing_status'], unique=False)
    op.create_index(op.f('ix_photos_detected_objects'), 'photos', ['detected_objects'], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_photos_detected_labels'), 'photos', ['detected_labels'], unique=False, postgresql_using='gin')


def downgrade() -> None:
    """Drop photos table."""
    op.drop_index(op.f('ix_photos_detected_labels'), table_name='photos')
    op.drop_index(op.f('ix_photos_detected_objects'), table_name='photos')
    op.drop_index(op.f('ix_photos_ai_processing_status'), table_name='photos')
    op.drop_index(op.f('ix_photos_status'), table_name='photos')
    op.drop_index(op.f('ix_photos_object_key'), table_name='photos')
    op.drop_index(op.f('ix_photos_user_id'), table_name='photos')
    op.drop_table('photos')