from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.core.db import get_async_session
from api.chat.schemas import UserMessage, ChatCreate, ChatResponse, MessageRead
from api.chat.services import create_chat, generate_reply, save_turn
from workflow.models import Message

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def chat(data:UserMessage, request: Request, session: AsyncSession = Depends(get_async_session)):
    chat_data = ChatCreate(user_id = request.state.user, thread_id = data.thread_id)
    chat = await create_chat(chat_data, session)
    thread_id = chat["thread_id"]
    reply = await generate_reply(data.message, request.state.user, thread_id)
    await save_turn(request.state.user, thread_id, data.message, reply, session)
    return ChatResponse(thread_id=thread_id, response=reply)

@router.get("/threads/{thread_id}/messages", response_model=list[MessageRead])
async def get_messages(
    thread_id: str,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        select(Message)
        .where(Message.user_id == request.state.user, Message.thread_id == thread_id)
        .order_by(Message.created_at)
    )
    result = await session.execute(stmt)
    return result.scalars().all()