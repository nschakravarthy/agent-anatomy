import uuid as uuid_pkg
from typing import Optional

from sqlalchemy import Column, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field
from pgvector.sqlalchemy import Vector

from api.core.models import TimestampModel, UUIDModel

class Note(UUIDModel, TimestampModel, table=True):
    __tablename__ = "note"
    user_id: uuid_pkg.UUID = Field(foreign_key = "user.uuid", index = True)
    thread_id: str = Field(index=True)
    content: str
    embedding: list[float] = Field(sa_column=Column(Vector(1536)))
    meta: dict = Field(default_factory=dict, sa_column=Column(JSONB))

