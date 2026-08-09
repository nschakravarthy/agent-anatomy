"""
Specification to describe a basic agent.
Fields:
    name         — human-readable identifier
    description  — one-line summary
    version      — spec-shape version; updated when the shape changes
    generated_at — when this spec was built
    model        — the Anthropic model to call
    max_tokens   — cap on the reply length
This file is the reference point for future stages. Every stage's spec.py is
this file plus one or two more fields, with new docstrings explaining why the
addition earns its keep.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field

class AgentSpec(BaseModel):
    """
    Configuration of the Stage 1 basic agent
    """
    
    #identity
    name: str = Field(description="Human-readable name for this agent.")
    description: str = Field(
        default="",
        description=(
            "One-line summary of what the agent is meant for. Not consumed "
            "by the stage-01 runtime; later stages will use it as part of "
            "the system prompt."
        ),
    )

    # versioning
    version: str = Field(
        default="0.1",
        description="Spec shape version. Bump when fields are added or removed.",
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this spec was constructed.",
    )

    # model
    model: str = Field(
        default="claude-opus-4-7",
        description="Anthropic model identifier the runtime should call.",
    )
    max_tokens: int = Field(
        default=1000,
        gt=0,
        description="Maximum output tokens per reply.",
    )