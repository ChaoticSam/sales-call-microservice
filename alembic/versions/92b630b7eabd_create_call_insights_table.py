"""create call_insights table

Revision ID: 92b630b7eabd
Revises: bcc4ec678733
Create Date: 2025-07-29 13:58:40.608078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '92b630b7eabd'
down_revision: Union[str, Sequence[str], None] = 'feb1f63d1ca3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create the call_insights table
    op.create_table(
        'call_insights',
        sa.Column('call_id', sa.String(), sa.ForeignKey('calls_db.call_id'), primary_key=True),
        sa.Column('embedding', postgresql.ARRAY(sa.Float), nullable=False),
        sa.Column('customer_sentiment', sa.Float(), nullable=False),
        sa.Column('agent_talk_ratio', sa.Float(), nullable=False),
    )
    # Add an index on customer_sentiment (optional)
    op.create_index('ix_call_insights_customer_sentiment', 'call_insights', ['customer_sentiment'])
    op.create_index('ix_call_insights_talk_ratio',       'call_insights', ['agent_talk_ratio'])

def downgrade():
    # Drop indexes and table
    op.drop_index('ix_call_insights_talk_ratio',       table_name='call_insights')
    op.drop_index('ix_call_insights_customer_sentiment', table_name='call_insights')
    op.drop_table('call_insights')