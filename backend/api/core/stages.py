"""Discovery and loading of the per-stage agents.

Stages live in ``backend/agents/stage_NN[_slug]/``. Each stage package exposes a
``SpecAgent`` class and a ``SPEC_PATH`` pointing at its default spec JSON, so
this module can treat every stage identically and the rest of the app never
imports a stage package directly.
"""

from __future__ import annotations

import importlib
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

# api/core/stages.py -> api/core -> api -> backend
AGENTS_ROOT = Path(__file__).resolve().parents[2] / "agents"

# stage_01 and stage_01_bare_call are both valid folder names for stage 01.
_STAGE_DIR_PATTERN = re.compile(r"^stage_(\d{2})(?:_.+)?$")


def stage_dirs() -> dict[str, Path]:
    """Map stage id ("01") to its folder. Rescanned on every call."""
    found: dict[str, Path] = {}
    if not AGENTS_ROOT.is_dir():
        return found
    for path in sorted(AGENTS_ROOT.iterdir()):
        match = _STAGE_DIR_PATTERN.match(path.name)
        if not path.is_dir() or not match:
            continue
        stage_id = match.group(1)
        if stage_id in found:
            # Two folders with the same numeric prefix — a build error, not a
            # runtime one. Fail loud so it's caught during development.
            raise RuntimeError(
                f"Ambiguous stage {stage_id}: both {found[stage_id].name} and "
                f"{path.name} match. Rename one; stage numbers must be unique."
            )
        found[stage_id] = path
    return found


def resolve_stage_module_name(stage_id: str) -> str:
    """Return the package name for a stage id, e.g. "01" -> "stage_01"."""
    dirs = stage_dirs()
    if stage_id not in dirs:
        raise ModuleNotFoundError(f"No stage folder matching stage_{stage_id}")
    return dirs[stage_id].name


def import_stage(stage_id: str) -> Any:
    """Import a stage's ``agent`` module."""
    module_name = resolve_stage_module_name(stage_id)
    return importlib.import_module(f"agents.{module_name}.agent")


def load_spec(stage_id: str) -> Any:
    """Load a stage's default spec without constructing the agent.

    Used by the discovery endpoint, which must not require an API key.
    """
    module = import_stage(stage_id)
    return module.SpecAgent.load_spec(module.SPEC_PATH)


@lru_cache(maxsize=None)
def load_stage(stage_id: str) -> Any:
    """Import the stage's SpecAgent and load its default spec into an instance.

    Cached per process. The cache clears on module reload (uvicorn --reload
    picks up code changes; spec-JSON changes need a restart to take effect).
    """
    module = import_stage(stage_id)
    return module.SpecAgent(module.SpecAgent.load_spec(module.SPEC_PATH))


def discover_stages() -> list[dict[str, str]]:
    """List every stage that loads cleanly, for the frontend's agent picker.

    Stages whose spec is missing or malformed are skipped rather than failing
    the whole listing — a half-built stage shouldn't hide the working ones.
    """
    stages: list[dict[str, str]] = []
    for stage_id in sorted(stage_dirs()):
        try:
            spec = load_spec(stage_id)
        except Exception:
            continue
        stages.append(
            {
                "stage": f"stage-{stage_id}",
                "agent": spec.name,
                "description": spec.description,
            }
        )
    return stages
