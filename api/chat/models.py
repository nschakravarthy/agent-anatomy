import uuid as uuid_pkg

from sqlmodel import Field, SQLModel

from api.core.models import TimestampModel, UUIDModel

class Chat(TimestampModel, UUIDModel, table = True):
    __tablename__ = "chat"
    user_id:uuid_pkg.UUID
    thread_id:str = Field(primary_key = True, unique = True, index = True)
