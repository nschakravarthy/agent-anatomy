"""Workflow nodes for the research agent graph.

Each node receives the current ``AgentState`` and returns a partial update that
LangGraph merges back in (the ``messages`` key is reduced with ``add_messages``).
``call_model`` is the generation step: it runs the conversation through
Anthropic's Claude and appends the reply to the message history.
"""
from functools import lru_cache

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage

from workflow.state import AgentState
from workflow.tools import tavily_search

SYSTEM_PROMPT = (
    "You are Otto, a personal research assistant. Answer the user's questions "
    "using the conversation so far and any search results or retrieved notes "
    "available in the context. Be accurate and cite sources when they are "
    "provided; if you are unsure, say so rather than guessing."
)

tools = [tavily_search]

@lru_cache(maxsize=1)
def get_model() -> ChatAnthropic:
    return ChatAnthropic(
        model="claude-opus-4-7",
        max_tokens=16000,
        thinking={"type": "adaptive"},
    )

@lru_cache(maxsize=1)
def get_model_with_tools() -> ChatAnthropic:
    return get_model().bind_tools(tools)


async def call_model(state: AgentState) -> dict:
    """Invoke Claude on the running conversation and append its reply.

    The system prompt is sent on every call (marked with ``cache_control`` so it
    is served from cache once the prompt prefix exceeds the model's caching
    minimum) but is not written back into ``messages``, keeping the persisted
    history clean.
    """
    system = SystemMessage(
        content=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ]
    )
    response = await get_model_with_tools().ainvoke([system, *state["messages"]])
    return {"messages": [response]}
