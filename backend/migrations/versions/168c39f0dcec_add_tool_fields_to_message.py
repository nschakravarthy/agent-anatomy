"""add tool fields to message

Revision ID: 168c39f0dcec
Revises: 6d4ad435cc5b
Create Date: 2026-05-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '168c39f0dcec'
down_revision: Union[str, Sequence[str], None] = '6d4ad435cc5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('message', sa.Column('tool_calls', postgresql.JSONB(astext_type=Text()), nullable=True))
    op.add_column('message', sa.Column('tool_call_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('message', sa.Column('tool_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('message', 'tool_name')
    op.drop_column('message', 'tool_call_id')
    op.drop_column('message', 'tool_calls')
