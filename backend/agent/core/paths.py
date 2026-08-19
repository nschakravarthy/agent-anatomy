"""Where an agent's authored data lives.

Every part loader calls agent_file(name, part) to find its JSON. Centralising
the path convention means changing the layout is a one-line edit rather than
twelve.

Convention:

    types/<agent_name>/<part>.json

Agent-first rather than part-first: creating a new agent means copying one
folder, and everything about an agent is readable in one place.
"""

from __future__ import annotations

from pathlib import Path

AGENTS_ROOT = Path(__file__).resolve().parent.parent / "types"


def agent_dir(agent_name: str) -> Path:
    path = AGENTS_ROOT / agent_name
    if not path.is_dir():
        available = sorted(p.name for p in AGENTS_ROOT.iterdir() if p.is_dir())
        raise FileNotFoundError(
            f"No agent named '{agent_name}'. Available: {available or '(none)'}"
        )
    return path


def agent_file(agent_name: str, part: str) -> Path | None:
    """Path to one part's data file, or None if the agent doesn't define it.

    A missing file is not an error: an agent with no tools simply has no
    tools.json, and the loader returns an empty list.
    """
    path = agent_dir(agent_name) / f"{part}.json"
    return path if path.is_file() else None


def list_agents() -> list[str]:
    if not AGENTS_ROOT.is_dir():
        return []
    return sorted(p.name for p in AGENTS_ROOT.iterdir() if p.is_dir())