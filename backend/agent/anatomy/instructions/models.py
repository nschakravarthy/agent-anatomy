"""
Instructions are guidelines that direct how the agent behaves.
"""

from __future__ import annotations

from enum import StrEnum
from pydantic import BaseModel, Field 

class InstructionKind(StrEnum):
    SCOPE = "scope"
    TONE = "tone"
    FORMATTING = "formatting"
    ESCALATION = "escalation"
    SAFETY = "safety"

class Instruction(BaseModel):
    kind: InstructionKind = Field(description = "Which aspect of behavior this guideline directs")
    text: str = Field(description = "One behavioral guideline")