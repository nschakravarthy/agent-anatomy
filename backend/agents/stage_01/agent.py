"""
Stage 01 runtime driven by the model specification
"""

from __future__ import annotations

from pathlib import Path

from agents.core.llm import get_client
from agents.stage_01.spec import AgentSpec

# The spec every stage-01 agent is built from by default. The loader is a
# classmethod so later stages can point SPEC_PATH elsewhere without the app
# needing to know where a stage keeps its spec.
SPEC_PATH = Path(__file__).resolve().parent / "spec.json"

class SpecAgent:
    """
    Loads a specification, holds an Anthropic client and
    generates a response to a message
    """

    def __init__(self, spec: AgentSpec):
        self.spec = spec
        self.client = get_client()

    @classmethod
    def load_spec(cls, path: str | Path = SPEC_PATH) -> AgentSpec:
        """Read and validate a spec JSON file."""
        return AgentSpec.model_validate_json(Path(path).read_text(encoding="utf-8"))

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
        # Thinking is on by default on current models, so the reply is not
        # necessarily the first content block — keep only the text ones.
        return "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()
