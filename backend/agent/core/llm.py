"""
LLM client factory to construct the client for every stage.
Tests can reset the cached client with `get_client.cache_clear()` after
monkey-patching the env or the SDK.
"""
from __future__ import annotations

import os
from functools import lru_cache

from anthropic import AsyncAnthropic

@lru_cache(maxsize = 1)
def get_client() -> AsyncAnthropic:
    """
    Return the process wide Anthropic client.
    Requires ANTHROPIC_API_KEY in the environment. Raises RuntimeError with a
    clear message if it's missing, since the SDK's own error is less obvious.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Export it in your shell or add it to "
            "your .env before starting the app."
        )
    return AsyncAnthropic()
