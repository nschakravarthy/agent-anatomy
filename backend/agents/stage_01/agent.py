"""
Stage 01 runtime driven by the model specification
"""

from __future__ import annotations

from agents.core.llm import get_client
from agents.stage_01.spec import AgentSpec

class SpecAgent:
    """
    Loads a specification, holds an Anthropic client and 
    generates a response to a message
    """

    def __init__(self, spec: AgentSpec):
        self.spec = spec
        self.client = get_client()
    
    async def handle_message(
        self,
        message: str,
        thread_id: str | None = None,  # accepted but ignored at this stage
    ) -> str:
        response = await self.client.messages.create(
            model=self.spec.model,
            max_tokens=self.spec.max_tokens,
            messages=[{"role": "user", "content": message}],
        )
        return response.content[0].text