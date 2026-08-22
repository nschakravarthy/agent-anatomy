"""
The model and execution harness for planning and taking action
"""

from __future__ import annotations

from agent.core.llm import get_client
from agent.anatomy.spec import AgentSpec
from agent.anatomy.instructions import runtime as instructions_runtime

async def run_turn(spec: AgentSpec, message: str)-> str:
    """
    Handle one message and return the response
    """
    client = get_client()
    system = build_system_prompt(spec)
    response = await client.messages.create(
        model = spec.model,
        max_tokens = spec.max_tokens,
        system = system,
        messages = [{"role":"user", "content": message}]
    )
    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )

def build_system_prompt(spec: AgentSpec) -> str:
    """Assemble the system prompt from the parts that contribute to it.
 
    Each part renders its own block; this function decides which blocks
    appear and in what order. Blocks arrive as parts land — knowledge at
    Step 2, the memory policy at Step 4, permissions at Step 5.
    """
    blocks: list[str] = [_preamble(spec)]
 
    instructions = instructions_runtime.render(spec.instructions)
    if instructions:
        blocks.append(instructions)
 
    return "\n\n".join(blocks)
 
 
def _preamble(spec: AgentSpec) -> str:
    line = f"You are {spec.name}."
    if spec.description:
        line += f" {spec.description}"
    return line
 
 
def _text_of(response) -> str:
    """Pull plain text out of a response whose content is a list of blocks.
 
    A response can contain several block types. Right now only text blocks
    are possible; from Step 3 tool_use blocks appear alongside them, and this
    helper is what keeps the rest of the code from caring.
    """
    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )