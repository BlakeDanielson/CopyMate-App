"""Add role field to User model.

Revision ID: 000002
Revises: 000001
Create Date: 2025-04-22

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '000002'
down_revision = '000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role column to user table with default value 'user'
    op.add_column('user', sa.Column('role', sa.String(), nullable=False, server_default='user'))


def downgrade() -> None:
    # Drop role column from user table
    op.drop_column('user', 'role')