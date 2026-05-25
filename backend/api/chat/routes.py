from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from api.core.db import get_async_session
from api.chat.schemas import UserMessage, ChatCreate, ChatResponse
from api.chat.services import create_chat, generate_reply

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def chat(data:UserMessage, request: Request, session: AsyncSession = Depends(get_async_session)):
    chat_data = ChatCreate(user_id = request.state.user, thread_id = data.thread_id)
    chat = await create_chat(chat_data, session)
    thread_id = chat["thread_id"]
    reply = await generate_reply(
        message=data.message,
        user_id=request.state.user,
        thread_id=thread_id,
    )
    return ChatResponse(thread_id=thread_id, response=reply)
