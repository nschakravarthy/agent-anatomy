"""Stage 01 smoke test.

Verifies that:
    1. The spec loads and validates.
    2. The runtime makes a real call and returns a non-empty string.

Run with:
    poetry run pytest agents/stage_01_bare_call/tests/smoke.py -v

Requires ANTHROPIC_API_KEY to be set, since the test actually hits the API.
"""

from __future__ import annotations

import asyncio
import os

import pytest

from agents.stage_01_bare_call.agent import SPEC_PATH, SpecAgent


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set; this smoke test hits the real API.",
)
def test_bare_call_returns_a_reply():
    spec = SpecAgent.load_spec(SPEC_PATH)
    agent = SpecAgent(spec)

    reply = asyncio.run(agent.handle_message("Say hello in one word."))

    assert isinstance(reply, str)
    assert reply.strip(), "reply should be non-empty"


def test_spec_loads_and_has_expected_fields():
    spec = SpecAgent.load_spec(SPEC_PATH)
    assert spec.name == "support"
    assert spec.model.startswith("claude-")
    assert spec.max_tokens > 0