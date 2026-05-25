"""add chat table

Revision ID: 14bcdb2a60d7
Revises: 8642274d53d2
Create Date: 2026-05-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '14bcdb2a60d7'
down_revision: Union[str, Sequence[str], None] = '8642274d53d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('chat',
    sa.Column('uuid', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('thread_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('uuid', 'thread_id')
    )
    op.create_index(op.f('ix_chat_thread_id'), 'chat', ['thread_id'], unique=True)
    op.create_index(op.f('ix_chat_uuid'), 'chat', ['uuid'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_chat_uuid'), table_name='chat')
    op.drop_index(op.f('ix_chat_thread_id'), table_name='chat')
    op.drop_table('chat')
