from enum import Enum

from sqlalchemy import String
from sqlmodel import Field, SQLModel

from api.core.models import TimestampModel, UUIDModel

class UserRole(str, Enum):
    """Access level for an account.

    Drives which tabs the frontend renders and which endpoints the
    `require_admin` dependency lets through. Subclassing `str` means a role
    read back from the database compares equal to its enum member, so
    `user.role == UserRole.ADMIN` works whether the value came from the ORM or
    from raw SQL.
    """

    USER = "user"
    ADMIN = "admin"

# The single privileged account, seeded by the add_user_role migration. It is a
# well-formed address so it goes through the same EmailStr-validated login path
# as every other account.
ADMIN_EMAIL = "admin@acme.com"

class UserBase(SQLModel):
    email: str = Field(unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    # Stored as plain text rather than a database enum so that adding a role
    # later is a code change instead of a type migration on both Postgres and
    # SQLite.
    role: UserRole = Field(default=UserRole.USER, sa_type=String, nullable=False)

class User(UserBase, UUIDModel, TimestampModel, table=True):
    __tablename__ = "user"

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
