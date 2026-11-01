"""Schema-only tools: Pydantic classes given to `bind_tools` that have no code behind them.

The model "calls" `AskUser` like any tool, but nothing executes it. Instead the graph's route
function sees the call and goes to the `ask_user` node, which shows the question and ends the
turn. The user's reply arrives as the next message and the agent continues from there.

This is the LLM-driven version of `clarify`: `clarify` asks with a fixed question decided by
regex; `AskUser` lets the model decide when it is stuck and what to ask.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AskUser(BaseModel):
    """Ask the user one question and stop until they answer. Use only when you cannot continue
    without something only the user knows (which txn, which time window, which cluster)."""

    question: str = Field(description="One short, specific question.")
