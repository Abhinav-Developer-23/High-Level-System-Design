"""The chat model: Claude through the Anthropic API, wrapped by LangChain's `ChatAnthropic`.

Every LLM node (plan, agent, review) goes through `call()`:

    model = chat_model()                       # ChatAnthropic(model=..., api_key=...)
    model = model.bind_tools(tools)            # only the agent node does this
    ai, run = await call(model, messages, node="agent")

`call()` streams the reply token by token (so the UI can show text as it is written), glues the
chunks back into one `AIMessage`, and returns it together with a small `run` record (tokens,
time, cost) for `state.runs`.

What ChatAnthropic does for us
------------------------------
* Converts LangChain messages to the Anthropic Messages API: `SystemMessage` → the `system`
  field, `HumanMessage` → a user turn, `AIMessage` → an assistant turn (text + `tool_use`
  blocks), `ToolMessage` → a `tool_result` block inside a user turn.
* `bind_tools([...])` turns `@tool` functions, `BaseTool` objects and Pydantic classes into
  Anthropic's tool JSON schema. When Claude wants a tool, the reply comes back as
  `AIMessage.tool_calls = [{"name": ..., "args": {...}, "id": ...}]` — that is what the graph's
  `ToolNode` runs.
* Retries on rate limits / 5xx (`max_retries`) and reports token usage in `usage_metadata`.

Prompt caching (see `system_message` and `with_cache`)
------------------------------------------------------
The API is stateless: every call resends tools + system prompt + the whole conversation. Anthropic
can keep the *processed* prefix of a request for a few minutes; a later request that starts with
the same bytes reads it at a fraction of the input price. We switch it on per request:
  * an explicit `cache_control` marker on the skills block of the system prompt → tools + skills
    (render order is tools → system → messages) are cached; they never change;
  * a top-level `cache_control` on the agent's request (automatic caching) → the API puts a
    second breakpoint on the last message, so the growing conversation is cached too.
`run_record` reads `cache_read` / `cache_creation` from the usage to price the call correctly.

Background for beginners
------------------------
* **Streaming**: `model.astream(messages)` yields small `AIMessageChunk`s as tokens arrive.
  Chunks can be added with `+`; adding all of them gives the full message, including the
  tool calls (whose JSON arguments also arrive in pieces).
"""

from __future__ import annotations

import time
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, message_chunk_to_message
from langgraph.config import get_stream_writer

from .config import get_settings


def chat_model(model: str | None = None) -> BaseChatModel:
    """A fresh ChatAnthropic client with the settings from `.env` (`model` overrides AGENT_MODEL).

    Callers use `llm.chat_model()` (module attribute), not `from .llm import chat_model`, so a
    fake model can be swapped in for an offline run.
    """
    s = get_settings()
    return ChatAnthropic(
        model=model or s.model,
        max_tokens=s.max_tokens,
        timeout=s.llm_timeout_s,
        max_retries=2,
        # None → ChatAnthropic falls back to the ANTHROPIC_API_KEY environment variable itself.
        api_key=s.anthropic_api_key or None,
    )


def cache_control() -> dict[str, str] | None:
    """The `cache_control` marker for this run, or None when AGENT_PROMPT_CACHE=0."""
    s = get_settings()
    if not s.prompt_cache:
        return None
    return {"type": "ephemeral", "ttl": "1h"} if s.cache_ttl == "1h" else {"type": "ephemeral"}


def system_message(stable: str, extra: str = "") -> SystemMessage:
    """System prompt as content blocks: the stable part carries the cache breakpoint.

    `extra` (e.g. the compaction summary) goes in a second block *after* the breakpoint, so a
    new summary never invalidates the cached tools + skills.
    """
    first: dict[str, Any] = {"type": "text", "text": stable}
    if cc := cache_control():
        first["cache_control"] = cc
    blocks: list[str | dict[Any, Any]] = [first]
    if extra:
        blocks.append({"type": "text", "text": extra})
    return SystemMessage(content=blocks)


def with_cache(model: Any) -> Any:
    """Turn on automatic caching for the conversation tail (a top-level `cache_control` field)."""
    cc = cache_control()
    return model.bind(cache_control=cc) if cc else model


def emit(ev: dict[str, Any]) -> None:
    """Push a live event to whoever streams the graph (`stream_mode="custom"`). No-op outside a run."""
    try:
        get_stream_writer()(ev)
    except Exception:  # noqa: BLE001 — outside a streaming run there is no writer
        pass


def _block_text(content: Any, kind: str) -> str:
    """Text of one kind ("text" or "thinking") from a chunk's content (a str or a list of blocks)."""
    if isinstance(content, str):
        return content if kind == "text" else ""
    out = []
    for b in content or []:
        if isinstance(b, dict) and b.get("type") == kind:
            out.append(b.get(kind, "") or "")
    return "".join(out)


async def call(model: Any, messages: list[BaseMessage], *, node: str,
               model_name: str | None = None) -> tuple[AIMessage, dict[str, Any]]:
    """Run one LLM call, streaming text deltas to the UI. Returns (the full AIMessage, run record)."""
    name = model_name or get_settings().model
    t0 = time.monotonic()
    emit({"type": "agent_start", "node": node, "model": name})
    full: Any = None
    async for chunk in model.astream(messages):
        # Chunks add up: "Hel" + "lo" → "Hello"; partial tool-call JSON is merged the same way.
        full = chunk if full is None else full + chunk
        if text := _block_text(chunk.content, "text"):
            emit({"type": "text_delta", "node": node, "text": text})
        if thinking := _block_text(chunk.content, "thinking"):
            emit({"type": "thinking_delta", "node": node, "text": thinking})
    if full is None:
        raise RuntimeError(f"{node}: the model returned nothing")
    # AIMessageChunk → AIMessage (the form that is stored in state and sent back to the API).
    ai = message_chunk_to_message(full)
    assert isinstance(ai, AIMessage)
    run = run_record(node, ai, t0, model=name)
    emit({"type": "agent_end", "node": node, **run})
    return ai, run


def run_record(node: str, ai: AIMessage, t0: float, model: str | None = None) -> dict[str, Any]:
    """One row for `state.runs`: tokens, time, cost and tool calls of a single LLM call.

    LangChain's `input_tokens` is the whole prompt; `input_token_details` splits off the part read
    from the cache (cheap) and the part written to it (1.25x, or 2x with the 1-hour TTL).
    """
    s = get_settings()
    usage = ai.usage_metadata or {}
    details = usage.get("input_token_details") or {}
    prompt, tout = int(usage.get("input_tokens", 0)), int(usage.get("output_tokens", 0))
    read = int(details.get("cache_read") or 0)
    write = int(details.get("cache_creation") or 0) + int(details.get("ephemeral_5m_input_tokens") or 0) \
        + int(details.get("ephemeral_1h_input_tokens") or 0)
    plain = max(prompt - read - write, 0)
    write_mult = 2.0 if s.cache_ttl == "1h" else 1.25
    cost = (plain * s.price_in_per_mtok + write * s.price_in_per_mtok * write_mult
            + read * s.price_cache_read_per_mtok + tout * s.price_out_per_mtok) / 1e6
    return {"node": node, "model": model or s.model, "duration_ms": int((time.monotonic() - t0) * 1000),
            "input_tokens": prompt, "cache_read_tokens": read, "cache_write_tokens": write,
            "output_tokens": tout, "cost_usd": round(cost, 4), "tool_calls": len(ai.tool_calls),
            "num_turns": 1, "is_error": False}
