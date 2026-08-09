from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from api.core.db import get_async_session
from api.core.stages import discover_stages
from api.chat.schemas import UserMessage, ChatCreate, ChatResponse, AgentInfo
from api.chat.services import create_chat

router = APIRouter()

@router.get("/agents", response_model=list[AgentInfo])
async def list_agents():
    """Stages available to talk to, for the frontend's agent picker."""
    return discover_stages()

@router.post("/agents/{name}", response_model=ChatResponse)
async def chat(name: str, data: UserMessage, request: Request, session: AsyncSession = Depends(get_async_session)):
    # StageSelectorMiddleware resolves /agents/stage-XX/{name} to this route and
    # attaches the stage's agent; without the stage segment there's nothing to
    # dispatch to.
    agent = getattr(request.state, "agent", None)
    if agent is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "No stage selected. Use /agents/stage-XX/{name} "
                "(e.g. /agents/stage-01/support)."
            ),
        )

    if agent.spec.name != name:
        raise HTTPException(
            status_code=404,
            detail=f"stage-{request.state.stage_id} has no agent named '{name}'",
        )

    chat_data = ChatCreate(user_id=request.state.user, thread_id=data.thread_id)
    chat = await create_chat(chat_data, session)
    thread_id = chat["thread_id"]

    reply = await agent.handle_message(data.message, thread_id=thread_id)
    return ChatResponse(
        response=reply,
        agent=agent.spec.name,
        stage=request.state.stage_id,
        thread_id=thread_id,
    )
