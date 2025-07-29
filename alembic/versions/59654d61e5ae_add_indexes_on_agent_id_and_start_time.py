"""add indexes on agent_id and start_time

Revision ID: 59654d61e5ae
Revises: 23f265e436b4
Create Date: 2025-07-29 12:09:58.874676

"""
from alembic import op
import sqlalchemy as sa

revision = '59654d61e5ae'
down_revision = '23f265e436b4'
branch_labels = None
depends_on = None
table = 'calls_db'

def upgrade():
    # Index on agent_id for fast filtering by agent
    op.create_index(
        'ix_calls_agent_id',
        table,
        ['agent_id'],
        unique=False
    )

    # Index on start_time for efficient date-range queries
    op.create_index(
        'ix_calls_start_time',
        table,
        ['start_time'],
        unique=False
    )

def downgrade():
    op.drop_index('ix_calls_agent_id', table_name=table)
    op.drop_index('ix_calls_start_time', table_name=table)