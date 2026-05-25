import uuid as uuid_pkg

from fastapi import HTTPException, Depends
from fastapi import status as http_status
from langchain_core.messages import BaseMessage, HumanMessage
from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.chat.schemas import ChatCreate
from api.chat.models import Chat
from workflow.graph import get_graph

async def create_chat(data: ChatCreate, session: AsyncSession):
    if data.thread_id:
        statement = select(
        Chat
        ).where(
            Chat.uuid == data.thread_id
        )
        results = await session.execute(statement=statement)
        db_chat = results.scalar_one_or_none()
        if db_chat:
            return {
                "thread_id": str(db_chat.uuid),
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid thread id")
    else:
        new_chat = Chat(user_id = data.user_id)
        session.add(new_chat)
        await session.commit()
        await session.refresh(new_chat)
        return {
            "thread_id": str(new_chat.uuid)
        }


def _message_text(message: BaseMessage) -> str:
    """Flatten an assistant message to plain text.

    With adaptive thinking enabled, ``content`` is a list of blocks (thinking +
    text) rather than a string, so pull out only the text blocks.
    """
    content = message.content
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )


async def generate_reply(
    message: str,
    user_id: uuid_pkg.UUID,
    thread_id: str,
) -> str:
    """Run the user's message through the agent graph and return Claude's reply.

    The graph's checkpointer keys conversation history on ``thread_id``, so only
    the new message is supplied; earlier turns are loaded automatically.
    """
    graph = get_graph()
    config = {"configurable": {"thread_id": str(thread_id)}}
    result = await graph.ainvoke(
        {
            "messages": [HumanMessage(content=message)],
            "user_id": str(user_id),
            "thread_id": str(thread_id),
        },
        config=config,
    )
    return _message_text(result["messages"][-1])