"""
The three records the system passes around. None of them is LangGraph-specific.

    Chunk      one stored clause (a Weaviate object in the real design). Written once, never edited.
    QueryPlan  what the LLM reads out of the question (structured output).
    Source     one numbered piece of evidence for one question, with its role (current / history /
               upcoming). Built fresh by nodes.latest_wins for every question; never stored.

[Python] pydantic.BaseModel: a class whose fields are declared with type hints and VALIDATED when an
object is created. Chunk(page="one", ...) raises an error instead of storing a wrong type. That is
also how LLM structured output is checked: the model's JSON must fit the class.
"""
# [Python] Makes every type hint a lazy string, so hints like `str | None` never fail at import time.
#          Common at the top of modern Python files.
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel


class Chunk(BaseModel):
    """One clause of one circular: the unit we store, search and cite.
    [Real] One Weaviate object: these fields are its properties, plus a vector made from header + text.
    Every field is written ONCE at ingest and never edited (append-only)."""
    uuid: str
    circular_id: str                    # "UPI-OC-186A-2026-27"
    clause_path: str                    # "Key Guidelines > 3": where in the circular, for the proof
    text: str                           # the clause, word for word: this is what the user sees quoted
    header: str                         # contextual header, embedded together with the text
    products: list[str]                 # ["TAP_AND_PAY"]: lets search filter by product
    # [Python] `str | None = None`: may be a string or None, and is None when not given.
    rule_key: str | None = None         # "UPI_LITE.per_txn_limit": which rule this clause sets, if any
    page: int
    issue_date: date
    effective_from: date                # the EFFECTIVE date, not the issue date: "latest wins" sorts by this


class QueryPlan(BaseModel):
    """What the LLM extracts from the question (structured output).
    [Real] llm.with_structured_output(QueryPlan) makes Claude return exactly these fields, validated."""
    # [Python] Literal[...]: the value must be one of these strings; pydantic rejects anything else.
    intent: Literal["rule_value", "what_changed", "explain", "out_of_scope"]
    products: list[str]
    parameter: str | None               # "per_txn_limit", "response_days", ... or None
    as_of: date | None                  # "on 10 Dec 2024" -> that date; None means today


class Source(BaseModel):
    """A numbered piece of evidence. The LLM sees the sources as [1], [2]...; the user sees the
    cited ones as the proof block. Made fresh for every question by nodes.latest_wins."""
    n: int                              # the [n] number the answer cites
    circular_id: str
    clause_path: str
    rule_key: str | None
    page: int
    text: str
    effective_from: date
    role: Literal["current", "history", "upcoming"]   # decided at query time, never stored
    replaced_by: str | None = None      # worked out at query time, never stored
    replaced_on: date | None = None
    pdf_url: str | None
