"""Assembles the research agent's LangGraph.

For now the graph is a single generation step (``call_model``). As the agent
grows, additional nodes (routing, web search, note retrieval) can be added here
and wired through the ``route``/``search_results``/``retrieved_nodes`` channels
already defined on ``AgentState``.
"""
from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from workflow.nodes import call_model
from workflow.state import AgentState
from workflow.tools import tavily_search

tools = [tavily_search]


@lru_cache(maxsize=1)
def get_graph():
    """Build and compile the agent graph (once).

    A ``MemorySaver`` checkpointer keeps per-thread conversation history so each
    call only needs to supply the new message — prior turns are loaded by
    ``thread_id``. NOTE: ``MemorySaver`` is in-process only; history is lost on
    restart and is not shared across workers. For durable, multi-worker memory,
    swap in a Postgres checkpointer (``langgraph-checkpoint-postgres``), which
    fits this project's existing Postgres setup.

    Construction is lazy so importing this module doesn't build the Claude client
    (which needs ANTHROPIC_API_KEY) at app startup.
    """
    builder = StateGraph(AgentState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")
    builder.add_edge("call_model", END)
    return builder.compile(checkpointer=MemorySaver())
