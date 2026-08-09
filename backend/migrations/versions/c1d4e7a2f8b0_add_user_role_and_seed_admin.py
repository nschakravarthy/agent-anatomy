"""add user.role and seed the admin account

Every existing row becomes a `user`; the single privileged account
(admin@acme.com / test1234) is inserted here so a fresh `alembic upgrade head`
yields a working admin login with no manual step.

Revision ID: c1d4e7a2f8b0
Revises: b7f3c2a1d9e4
Create Date: 2026-08-10 00:00:00.000000

"""
import uuid as uuid_pkg
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

from api.user.models import ADMIN_EMAIL, UserRole
from api.user.utils import get_password_hash


# revision identifiers, used by Alembic.
revision: str = 'c1d4e7a2f8b0'
down_revision: Union[str, Sequence[str], None] = 'b7f3c2a1d9e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Bootstrap credential. It is a well-known default, so treat it as a
# first-login-then-change password rather than a secret.
ADMIN_PASSWORD = "test1234"

# Ad-hoc table definition for the seed insert — the ORM model is not used here
# so this migration keeps working if the model changes later.
user_table = sa.table(
    "user",
    sa.column("uuid", sa.Uuid()),
    sa.column("email", sqlmodel.sql.sqltypes.AutoString()),
    sa.column("hashed_password", sqlmodel.sql.sqltypes.AutoString()),
    sa.column("is_active", sa.Boolean()),
    sa.column("role", sqlmodel.sql.sqltypes.AutoString()),
    sa.column("created_at", sa.DateTime()),
    sa.column("updated_at", sa.DateTime()),
)


def upgrade() -> None:
    """Upgrade schema."""
    # server_default both backfills existing rows and lets SQLite accept a NOT
    # NULL column added to a populated table.
    op.add_column(
        "user",
        sa.Column(
            "role",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default=UserRole.USER.value,
        ),
    )

    # Idempotent: re-running against a database that already has the account
    # (for example one seeded by hand) leaves it untouched.
    bind = op.get_bind()
    existing = bind.execute(
        sa.text('SELECT 1 FROM "user" WHERE email = :email'),
        {"email": ADMIN_EMAIL},
    ).first()
    if existing is None:
        now = datetime.utcnow()
        op.bulk_insert(
            user_table,
            [
                {
                    "uuid": uuid_pkg.uuid4(),
                    "email": ADMIN_EMAIL,
                    "hashed_password": get_password_hash(ADMIN_PASSWORD),
                    "is_active": True,
                    "role": UserRole.ADMIN.value,
                    "created_at": now,
                    "updated_at": now,
                }
            ],
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        sa.text('DELETE FROM "user" WHERE email = :email').bindparams(email=ADMIN_EMAIL)
    )
    op.drop_column("user", "role")
