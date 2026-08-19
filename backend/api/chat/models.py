import uuid as uuid_pkg


from api.core.models import TimestampModel, UUIDModel

class Chat(TimestampModel, UUIDModel, table = True):
    __tablename__ = "chat"
    user_id:uuid_pkg.UUID
