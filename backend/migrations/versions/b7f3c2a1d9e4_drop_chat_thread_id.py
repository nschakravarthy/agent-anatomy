"""drop chat thread_id column

The chat.uuid column (auto-generated via uuid4) is used as the thread id, so the
separate thread_id column is redundant. Drop it and make uuid the sole primary key.

Revision ID: b7f3c2a1d9e4
Revises: caf3ae6b6370
Create Date: 2026-05-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b7f3c2a1d9e4'
down_revision: Union[str, Sequence[str], None] = 'caf3ae6b6370'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_chat_thread_id'), table_name='chat')
    op.drop_constraint('chat_pkey', 'chat', type_='primary')
    op.create_primary_key('chat_pkey', 'chat', ['uuid'])
    op.drop_column('chat', 'thread_id')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('chat', sa.Column('thread_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.drop_constraint('chat_pkey', 'chat', type_='primary')
    op.create_primary_key('chat_pkey', 'chat', ['uuid', 'thread_id'])
    op.create_index(op.f('ix_chat_thread_id'), 'chat', ['thread_id'], unique=True)
