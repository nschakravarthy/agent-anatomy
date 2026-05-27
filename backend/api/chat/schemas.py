import uuid as uuid_pkg
from pydantic import BaseModel

class UserMessage(BaseModel):
    message: str
    thread_id: uuid_pkg.UUID | None = None

class ChatCreate(BaseModel):
    user_id: uuid_pkg.UUID
    thread_id: uuid_pkg.UUID | None = None

class ChatResponse(BaseModel):
    thread_id: uuid_pkg.UUID
    response: str

class MessageRead(BaseModel):
    role: str
    content: str

    model_config = {"from_attributes": True}

