"""
The ROUTERS: the functions behind the two conditional edges (the dashed amber arrows in
svg/n03-query-graph.svg).

[LangGraph] A router has the shape   def router(s: QAState) -> str
It reads the state (which the node before it has just updated) and returns the NAME of the next node.
It does not return a state update: anything it changes is thrown away. Keeping decisions in routers
keeps nodes simple: a node does work and writes facts (grounded=False), a router reads the facts and
decides where to go. graph.py attaches each router with add_conditional_edges().

[LangGraph] A router may also return a list of names (run them all, in parallel) or Send(...) objects
(fan out with a different input each). Ours always return exactly one name.
"""
from __future__ import annotations

from .state import QAState


def route_intent(s: QAState) -> str:
    """After understand: answer it, or ask/refuse."""
    if s["intent"] == "out_of_scope":
        return "clarify_or_refuse"
    if s["intent"] in ("rule_value", "what_changed") and not s["products"]:
        return "clarify_or_refuse"                                       # "which product's limit?"
    return "retrieve"


def route_grounding(s: QAState) -> str:
    """After check_grounding: done, retry once with a wider search, or give up.
    [LangGraph] Returning "retrieve" sends the run BACKWARDS: that's how a loop is made. The loop always
    ends because check_grounding raises `retries` on every failure and we stop after the first retry.
    (LangGraph also stops any run after `recursion_limit` steps and raises GraphRecursionError; pass
    {"recursion_limit": N} in the config to change it. Ours never gets near it.)"""
    if s["grounded"]:
        return "cite_sources"
    return "retrieve" if s["retries"] <= 1 else "not_found"
