"""The accessible surface of the agent
"""

from __future__ import annotations

from agent.anatomy.reasoning.runtime import run_turn
from agent.anatomy.spec import AgentSpec
from agent.core.paths import list_agents as _list_agents


async def handle_message(agent: str, message: str) -> str:
    """Run one message through the named agent and return its reply.

    Composition happens here rather than in the runtime because loading is a
    caller concern: it decides when specs are read and whether they're cached.
    The runtime stays a pure function of the spec it's given, which is what
    keeps it testable without touching disk.

    Composing per call re-reads JSON every request. That is deliberate for
    now — edit a file under agents/ and the change takes effect immediately,
    no restart. When there is enough to load that it matters, an @lru_cache
    goes on a _get_spec() helper here and nowhere else changes.
    """
    spec = AgentSpec.compose(agent)
    return await run_turn(spec, message)


def list_agents() -> list[str]:
    """Names of the agents available to serve. Useful for a picker in the UI."""
    return _list_agents()