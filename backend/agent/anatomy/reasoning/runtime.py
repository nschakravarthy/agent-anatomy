"""
The model and execution harness for planning and taking action
"""

from __future__ import annotations

from agent.core.llm import get_client
from agent.anatomy.spec import AgentSpec

async def run_turn(spec: AgentSpec, message: str)-> str:
    """
    Handle one message and return the response
    """
    client = get_client()
    response = await client.messages.create(
        model = spec.model,
        max_tokens = spec.max_tokens,
        messages = [{"role":"user", "content": message}]
    )
    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )