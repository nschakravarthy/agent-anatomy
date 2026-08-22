"""
Agent specification
"""

from __future__ import annotations

import json

from typing import List
from pydantic import BaseModel, Field

from agent.core.paths import agent_file
from agent.anatomy.instructions.models import Instruction
from agent.anatomy.instructions.loader import load as load_instructions

def load_identity(agent_name: str) -> dict:
    """
    Read the agent's identity card and set on the agent
    """
    path = agent_file(agent_name, "agent")
    if path is None:
        return {}
    raw = json.loads(path.read_text())
    raw.pop("name", None)  
    return raw

class AgentSpec(BaseModel):
    """
    Each field controls one aspect of the agent
    """

    # Identify
    name:str 
    description:str
    model:str = Field(default = "claude-opus-4-7")
    max_tokens:int = Field(default = 1000, gt=0)

    # Core capabilities
    instructions: List[Instruction] = Field(default_factory = list)

    @classmethod
    def compose(cls, agent_name:str) -> "AgentSpec":
        """
        Assemble the specification into an agent
        """
        identity = load_identity(agent_name)
        return cls(
            name = agent_name, 
            **identity,
            instructions=load_instructions(agent_name)
        )
    
    def coverage(self) -> dict[str, int]:
        """
        Shows the extent of specification covered in an agent
        """
        return {}
    
