"""
The graph's STATE: the one dict every node reads and writes.

[LangGraph] This is the state SCHEMA. Every key any node reads or writes is declared here, and
StateGraph(QAState) in graph.py is built from it. Each key becomes a "channel": a slot holding the
latest value. A node returns a dict with some of these keys; LangGraph merges it in.

[LangGraph] Merge rule: this schema has no reducers, so a returned key REPLACES the old value.
A reducer changes that for one key, e.g.
    from typing import Annotated
    import operator
    log: Annotated[list[str], operator.add]     # each node's returned list is APPENDED instead
Chat agents use one for their message list (langgraph.graph.message.add_messages). We don't need one:
each turn rebuilds everything, and understand() resets the per-turn keys (see nodes.py).

[Python] TypedDict: a normal dict at runtime, but with declared keys and types for editors and type
checkers. `total=False` means every key is optional: a run starts with only {"question": ...} and the
nodes fill in the rest as they go.

The keys, in the order the nodes fill them:
    question                            the input (from app.invoke / app.stream)
    intent, products, parameter, as_of  <- understand
    pinned, candidates                  <- retrieve      (candidates is replaced again by rerank)
    sources                             <- latest_wins
    answer, citations, found            <- generate
    grounded, retries                   <- check_grounding
    final                               <- cite_sources / clarify_or_refuse / not_found  (what the user sees)
"""
from __future__ import annotations

from datetime import date
from typing import TypedDict

# [Python] These imports look unused, but they are not: with `from __future__ import annotations` the
#          hints below are strings, and LangGraph resolves them against this module's names when it
#          builds the channels. Remove them and StateGraph(QAState) fails.
from .models import Chunk, Source


class QAState(TypedDict, total=False):
    question: str
    intent: str                         # rule_value / what_changed / explain / out_of_scope
    products: list[str]
    parameter: str | None
    as_of: date                         # the date the answer is "as of": today, or a date in the question
    pinned: list[Chunk]                 # every clause of the asked rule, fetched by metadata
    candidates: list[Chunk]             # search hits; after rerank: the 6 chosen ones
    sources: list[Source]               # the numbered evidence with roles (current / history / upcoming)
    answer: str
    citations: list[int]
    found: bool
    grounded: bool
    retries: int
    final: str
