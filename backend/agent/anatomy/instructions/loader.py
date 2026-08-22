"""
Load an agent's instructions from the json file into 
the iInstruction model. 
A missing file will still work. An agent with no instructions has no
instructions; the runtime will simply render nothing.
"""

from __future__ import annotations

import json

from agent.core.paths import agent_file
 
from .models import Instruction
 
PART = "instructions"
 
 
def load(agent_name: str) -> list[Instruction]:
    path = agent_file(agent_name, PART)
    if path is None:
        return []
    raw = json.loads(path.read_text())
    return [Instruction.model_validate(item) for item in raw]