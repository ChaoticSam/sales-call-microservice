"""Initial schema with indexes

Revision ID: 23f265e436b4
Revises: 
Create Date: 2025-07-29 11:58:48.163170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '23f265e436b4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('calls_db',
    sa.Column('call_id', sa.String(), nullable=False),
    sa.Column('agent_id', sa.String(), nullable=False),
    sa.Column('customer_id', sa.String(), nullable=False),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('duration_seconds', sa.Integer(), nullable=True),
    sa.Column('transcript', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('call_id')
    )
    op.create_index(op.f('ix_calls_db_call_id'), 'calls_db', ['call_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_calls_db_call_id'), table_name='calls_db')
    op.drop_table('calls_db')
