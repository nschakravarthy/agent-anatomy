"""Render instructions into a block of the system prompt.

This function returns a block, not a whole prompt. Assembling blocks from
several parts into the final system prompt is reasoning's job.
"""

from __future__ import annotations

from .models import Instruction, InstructionKind

_ORDER: tuple[InstructionKind, ...] = (
    InstructionKind.SCOPE,
    InstructionKind.TONE,
    InstructionKind.FORMATTING,
    InstructionKind.ESCALATION,
    InstructionKind.SAFETY,
)

_LABEL: dict[InstructionKind, str] = {
    InstructionKind.SCOPE: "Scope",
    InstructionKind.TONE: "Tone",
    InstructionKind.FORMATTING: "Formatting",
    InstructionKind.ESCALATION: "Escalation",
    InstructionKind.SAFETY: "Safety",
}


def render(instructions: list[Instruction]) -> str:
    """Return a markdown block, or an empty string if there is nothing to say."""
    if not instructions:
        return ""

    grouped: dict[InstructionKind, list[Instruction]] = {k: [] for k in InstructionKind}
    for instruction in instructions:
        grouped[instruction.kind].append(instruction)

    lines: list[str] = []
    for kind in _ORDER:
        items = grouped[kind]
        if not items:
            continue
        lines.append(f"## {_LABEL[kind]}")
        lines.extend(f"- {item.text}" for item in items)
        lines.append("")
    return "\n".join(lines).rstrip()