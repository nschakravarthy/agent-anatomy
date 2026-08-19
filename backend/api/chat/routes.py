from fastapi import APIRouter, Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from api.core.db import get_async_session
from api.chat.schemas import UserMessage, ChatCreate, ChatResponse
from api.chat.services import create_chat, generate_reply

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def chat(data: UserMessage, request: Request, session: AsyncSession = Depends(get_async_session)):
    """Send one message to the agent.

    A request without a thread_id starts a new conversation; passing back the
    thread_id from an earlier response continues that one. AuthMiddleware has
    already resolved the caller, so the chat is always owned by request.state.user.
    """
    chat_data = ChatCreate(user_id=request.state.user, thread_id=data.thread_id)
    chat = await create_chat(chat_data, session)
    thread_id = chat["thread_id"]

    reply = await generate_reply(data.message, request.state.user, thread_id)
    return ChatResponse(thread_id=thread_id, response=reply)
