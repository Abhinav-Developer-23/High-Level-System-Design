"""The LangGraph debugging pipeline.

    START → triage ─┬─ clarify → END                         (system unknown)
                    └─ npci ─┬─ report → END                  (pure NPCI code lookup, no LLM)
                             └─ plan → investigate → (compact) → agent ⇄ tools
                                                       │  ├─ ask_user → END      (model needs input)
                                                       │  └─ npci_enrich ─┬─ review ─┬─ investigate (gaps)
                                                       │                  │          └─ report → END
                                                       │                  └─ report → END

LLM nodes (plan, agent, review) call Claude through the Anthropic API (`llm.py`, ChatAnthropic).
The investigation is a tool loop *inside the graph*: `agent` asks the model, the model answers
with tool calls, `tools` (a prebuilt `ToolNode`) runs them, and the results go back to `agent`,
until the model answers without a tool call. Every round is its own checkpoint.

Long threads: every call resends the whole conversation, so two things keep the cost down:
prompt caching (`llm.system_message` / `llm.with_cache`: Anthropic re-reads the unchanged prefix
at a fraction of the price) and `compact`, which runs at the start of a turn once the last
prompt passed AGENT_COMPACT_TRIGGER_TOKENS and replaces all but the last few turns with a
summary written by a cheaper model (high/low watermark).

How to read this file
---------------------
1. `DebugState` — the one dict that flows through every node. Each node returns a *partial*
   update; LangGraph merges it into the state with the field's reducer (append, merge, or
   overwrite — see the class docstring).
2. The nodes, in pipeline order: `triage` → `clarify` / `npci_node` → `plan` → `investigate`
   → (`compact`) → `agent` ⇄ `tools` → `npci_enrich` → `review` → `report`. Each is an `async def` taking the state.
3. The `route_after_*` functions — they look at the state and return the *name* of the next
   node. That is how the conditional arrows in the diagram above are implemented.
4. `build_graph(belt)` at the bottom — wires nodes and routes together into a `StateGraph`.
   The tools themselves live in `tools/` (DB tools, file tools, MCP tools).

Pure-Python nodes (triage, clarify, npci, investigate, npci_enrich, ask_user, report) cost
nothing and are instant. Only plan / agent / review (and compact, rarely) call the model.

LangGraph in plain words (read this if you have never used it)
---------------------------------------------------------------
Think of a flowchart on a whiteboard. Each box does one job; arrows say which box runs next.
LangGraph is a library that lets you draw that flowchart in Python and then run it.

* **State**  – one Python dict that is carried from box to box. Every box can read anything in
  it and write new values into it. Here the dict's shape is `DebugState` (below).
* **Node**   – one box. It is just a Python function: it receives the current state and
  returns a *small* dict containing only the keys it wants to change. LangGraph merges that
  small dict into the big state for you. A node never has to copy the whole state.
* **Edge**   – an arrow. `add_edge("a", "b")` means "after a, always run b".
* **Conditional edge** – an arrow with a decision. `add_conditional_edges("a", pick, [...])`
  means "after a, call `pick(state)`; it returns the name of the next node as a string".
* **Tool**   – a function the *model* may ask to run (`@tool`, `BaseTool`, MCP tools…). The model
  only names the tool and its arguments; the `tools` node (`ToolNode`) actually runs it.
* **START / END** – special built-in names for "the flowchart begins here" and "stop here".
* **compile()** – turns the drawn flowchart into something you can run.
* **Checkpointer** – a save-file. After every node, LangGraph writes the whole state into a
  SQLite database under a *thread id* (one id per conversation). Next time you run the graph
  with the same thread id, it loads that saved state first, so it "remembers" earlier turns.
* **astream()** – runs the graph and hands you events as they happen (node started, node
  finished, custom messages), instead of making you wait for the very end.

A full run therefore looks like: load saved state → merge in the new question → run `triage`
→ merge its output → ask the route function where to go → run that node → … → reach END →
save. The web server (`server.py`) and the CLI (`cli.py`) both do exactly that.
Python you will see a lot in this file
--------------------------------------
* `async def f(...)` / `await g(...)` – an *asynchronous* function. `await` means "wait for
  this slow thing (a network call, a subprocess) without freezing the whole program", so the
  web server can keep answering other requests meanwhile. You can only `await` inside an
  `async def`. LangGraph knows how to run async nodes.
* `x: str`, `-> dict[str, Any]` – *type hints*. They document what a variable or function
  returns. Python does not enforce them at runtime; the `mypy` tool checks them.
* `str | None` – "either a string or None (nothing)".
* `state.get("key")` – read a dict key, returning None instead of crashing if it is missing.
  `state["key"]` crashes (KeyError) if it is missing — used only when the key must exist.
* `a or b` – gives `a` if `a` is "truthy" (not None / "" / 0 / empty list), otherwise `b`.
  So `state.get("options") or {}` means "the options dict, or an empty dict if there is none".
* `[x for x in items if cond]` – a *list comprehension*: build a new list in one line.
  `{...}` with the same syntax builds a set (no duplicates), `{k: v for ...}` builds a dict.
* `f"hello {name}"` – an *f-string*: Python puts the value of `name` inside the text.
* `items[:10]` – *slicing*: the first 10 items (fewer if the list is shorter).
"""

# Makes all type hints lazy strings, so we can use modern syntax like `str | None` freely.
from __future__ import annotations

# --- Python standard library (comes with Python, nothing to install) ---
import json  # convert between Python dicts and JSON text
import operator  # `operator.add` is the `+` operator as a function; used as a list reducer below
import re  # regular expressions: text pattern matching
import time  # stopwatch for tool-call timing
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone  # dates and times
from typing import Annotated, Any, Literal, TypedDict  # building blocks for type hints

# --- LangGraph / LangChain (installed from pyproject.toml) ---
from langchain_core.messages import (  # the message types the chat model reads and writes
    AIMessage,
    AnyMessage,
    HumanMessage,
    RemoveMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, START, StateGraph  # the flowchart builder and its start/end markers
from langgraph.graph.message import REMOVE_ALL_MESSAGES, add_messages  # the reducer for message lists
from langgraph.prebuilt import ToolNode  # prebuilt node that runs the model's tool calls
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command

# --- this project's own modules. The leading "." means "from the same package (ai_debugger)" ---
from . import llm, mcp_config, npci, prompts
from .config import get_settings
from .tools import AskUser, ToolBelt

# India Standard Time = UTC + 5h30m. Used to timestamp messages the way the team reads them.
IST = timezone(timedelta(hours=5, minutes=30))

# What kind of question this is. Decided by regex in `classify()`; it only steers the prompts and
# the `npci_lookup` shortcut — the investigator itself is free to use any tool.
# `Literal[...]` is a type hint meaning "only one of these exact strings is allowed".
Intent = Literal["txn", "alert", "metrics", "logs", "db", "code", "npci_lookup", "general"]


# `class X(TypedDict)` does NOT create a new kind of object. At runtime a Msg is a plain dict like
# {"role": "user", "content": "...", "ts": "...", "node": "triage"}. The class only documents which
# keys the dict has and what type each value is, so editors and mypy can catch typos.
class Msg(TypedDict):
    """One chat bubble, as shown in the UI and stored in the checkpoint."""
    role: str      # "user" | "assistant"
    content: str   # markdown
    ts: str        # ISO time in IST
    node: str      # which graph node produced it


def merge_dicts(old: dict[str, Any] | None, new: dict[str, Any] | None) -> dict[str, Any]:
    """Reducer for `txn_rows`: keep the old keys, add / replace the new ones."""
    return {**(old or {}), **(new or {})}


class DebugState(TypedDict, total=False):
    """The state of one conversation thread. Saved after every node by the SQLite checkpointer.

    How a node's update is merged, per field (the second part of `Annotated[...]` is the reducer):
      * `Annotated[list, operator.add]` — appended: `runs = [A]` + update `[B]` → `[A, B]`.
      * `Annotated[list, add_messages]` — appended too, but a message with an existing `id`
        replaces it, and `RemoveMessage(id=REMOVE_ALL_MESSAGES)` empties the list.
      * `Annotated[dict, merge_dicts]` — dict merge: new keys added, existing ones replaced.
      * everything else — simply overwritten.

    Example. Saved state has `runs = [A]`. The `plan` node returns `{"plan": "1. …", "runs": [B]}`.
    After merging: `plan` is replaced with the new text, and `runs` becomes `[A] + [B] = [A, B]`
    (that `+` is `operator.add`).

    `total=False` means every key is optional: on the very first run most of them do not exist
    yet, which is why the code reads them with `state.get(...)`.
    """
    # --- append-only history (grows across turns) ---
    messages: Annotated[list[Msg], operator.add]           # chat transcript shown in the UI
    runs: Annotated[list[dict[str, Any]], operator.add]     # one entry per LLM call (tokens, cost, time)
    tool_log: Annotated[list[dict[str, Any]], operator.add]  # every tool call the agent made

    # --- inputs for the current turn ---
    question: str                  # the user's message (or the parked one, after a clarify reply)
    options: dict[str, Any]        # per-request overrides from UI/CLI: system, plan, review, servers
    pending_question: str | None   # question parked by `clarify` while we wait for "tpap"/"tsp"

    # --- triage output ---
    system: str | None             # "tpap" | "tsp" | None (unknown → clarify). Tools read it via InjectedState.
    intent: Intent
    entities: dict[str, Any]       # txn ids, RRNs, clusters, incident ids, times, NPCI codes
    now_ist: str                   # wall clock handed to the LLM so "last 1h" means something
    turn: int                      # 1, 2, 3… one per user message in this thread

    # --- NPCI code translation (deterministic, from data/npci_error_codes.json) ---
    npci: list[npci.Resolved]
    npci_md: str                   # the same, rendered as a markdown table for prompts/report

    # --- the investigator's conversation with the model (the tool loop) ---
    # HumanMessage (task) → AIMessage (tool calls) → ToolMessage (results) → AIMessage → …
    # Kept across turns, so a follow-up continues the same conversation.
    agent_messages: Annotated[list[AnyMessage], add_messages]
    agent_system: str | None       # system that conversation belongs to (never continued across systems)
    tool_calls: int                # tool calls made this turn (budget: AGENT_MAX_TOOL_CALLS)
    evidence_nudges: int           # times this turn the agent was sent back for missing evidence
    txn_rows: Annotated[dict[str, dict[str, Any]], merge_dicts]  # written by the get_txn tool (Command)
    agent_summary: str             # older turns, summarized by `compact` (sent in the system prompt)
    context_tokens: int            # prompt size of the agent's last call; compact's trigger
    servers: list[str]             # MCP servers whose tools the agent was given

    # --- LLM outputs ---
    plan: str                      # planner's numbered plan
    findings: str                  # investigator's full markdown answer
    review: dict[str, Any] | None  # parsed reviewer verdict: {verdict, score, gaps, summary}
    loops: int                     # how many review rounds ran this turn
    report: str                    # final markdown shown to the user

    needs_input: bool              # True when the turn ended by asking the user something



# --------------------------------------------------------------------------------------------
# triage (deterministic)
#
# No LLM here: plain regexes decide which system the question is about, what kind of question it
# is, and pull out ids (txn, RRN, incident…) so later prompts can quote them back to the model.
# --------------------------------------------------------------------------------------------

# Regex crash course for the patterns below:
#   re.compile(r"...")  pre-builds a pattern once so it can be reused fast. The `r` before the quote
#                       makes a "raw string", so backslashes are passed to the regex as-is.
#   (?i)                ignore upper/lower case
#   \b                  a word boundary (so "tsp" matches "tsp:" but not "itspace")
#   \d  \s              a digit / a whitespace character
#   a|b                 a or b
#   ( ... )             a group; `findall` returns what each group matched
#   (?: ... )           a group that only groups, nothing is captured
#   x? x* x+ x{2,4}     x optional / zero or more / one or more / 2 to 4 times
#   [A-Za-z0-9]         any one letter or digit
#   (?=...)             "look ahead": must be followed by ..., but don't consume it
# Names starting with `_` are a convention for "private to this file, don't import from outside".
#
# Words that only make sense on one estate. A hit on exactly one side decides the system.
_TPAP_HINT = re.compile(r"(?i)\b(tpap|paytm\s*caller|paytmcaller|ptyes|ptaxis|pthdfc|ptsbi|gwts|mindgate|"
                        r"juspay|ocil|hss|metis|trino|archival)\b")
_TSP_HINT = re.compile(r"(?i)\b(tsp|paytmybl|zenduty|argo\s*cd|argocd|switch\s*c[236]|c[236]\s*cluster|"
                       r"cluster\s*c?[236]|finmate\s*jenkins)\b")
# Entity patterns. _TXN: a 24–48 char token with at least one digit AND one letter (UPI txn ids).
_TXN = re.compile(r"\b(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{24,48}\b")
_RRN = re.compile(r"\b\d{12}\b")                     # RRN = exactly 12 digits
_CLUSTER = re.compile(r"(?i)\bc([1236])\b")          # "c3" / "C6" → captures "3" / "6"
# "incident 381614", "zenduty #381614" or a bare "#381614"; two groups, only one matches
_INCIDENT = re.compile(r"(?i)(?:incident|zenduty)\s*#?\s*(\d{5,7})\b|#(\d{5,7})\b")
_ALT = re.compile(r"\bALT_[A-Za-z0-9]+\b")           # PaytmCaller alert ids look like ALT_xxxx
# times like "14:05", "2.30 pm", "10:15:00 IST"
_TIME = re.compile(r"(?i)\b(\d{1,2}[:.]\d{2}(?::\d{2})?\s*(?:am|pm)?(?:\s*ist|\s*utc)?)\b")
# Intent keywords, checked in priority order by `classify()`.
_NPCI_Q = re.compile(r"(?i)\b(what\s+(?:does|is)|meaning|mean|explain|decode|translate|stand\s+for|lookup|look\s+up)\b")
_ALERT_Q = re.compile(r"(?i)\b(alert|alerts|incident|page[sd]?|paged|firing|fired|zenduty|paytm\s*caller)\b")
_METRIC_Q = re.compile(r"(?i)\b(latency|p9[59]|sr\b|success\s*rate|spike|tps|throughput|cpu|memory|grafana|"
                       r"prometheus|dashboard|metric)")
_DB_Q = re.compile(r"(?i)\b(mysql|database|db\b|replica|replication|lag|hikari|connection\s*pool|pmm|percona|"
                   r"redash|sql)\b")
_LOG_Q = re.compile(r"(?i)\b(log|logs|kibana|elk|exception|stack\s*trace|error\s+spike)\b")
_CODE_Q = re.compile(r"(?i)\b(code\s+flow|source|class|repo|bitbucket|pull\s*request|\bpr\b|commit|deploy(?:ed|ment)?|"
                     r"jenkins|build)\b")


def detect_system(text: str) -> str | None:
    """Return "tpap", "tsp", or None when the text gives no (or contradictory) hints."""
    # `.search()` returns a match object if the pattern appears anywhere, else None.
    # `bool(...)` turns that into True / False. `a, b = x, y` assigns two variables at once.
    tp, ts = bool(_TPAP_HINT.search(text)), bool(_TSP_HINT.search(text))
    if tp and not ts:
        return "tpap"
    if ts and not tp:
        return "tsp"
    if tp and ts:
        # Both sides hinted. If the user literally typed only "tpap" or only "tsp", trust that.
        # `{... for ...}` is a set comprehension: collects lower-cased matches, duplicates removed.
        words = {w.lower() for w in re.findall(r"(?i)\b(tpap|tsp)\b", text)}
        if len(words) == 1:
            return words.pop()  # take the only element out of the set
    # Reaching the end of a function without `return x` would also give None; this says it explicitly.
    return None


def extract_entities(text: str) -> dict[str, Any]:
    """Pull ids out of the question. `dict.fromkeys` de-duplicates while keeping order.

    Example: "tsp: debug PTMabc…123 at 14:05, C3" →
        {"txn_ids": ["PTMabc…123"], "clusters": ["C3"], "times": ["14:05"], ...}
    """
    # `findall` returns a list of every match. `dict.fromkeys(list)` makes a dict whose keys are the
    # list items — dict keys are unique and keep insertion order, so this is "remove duplicates".
    # `if not t.isdigit()` skips all-digit tokens (those are not txn ids).
    txns = [t for t in dict.fromkeys(_TXN.findall(text)) if not t.isdigit()]
    # _INCIDENT has two groups, so findall gives pairs like ("381614", "") — keep whichever is filled.
    incidents = [a or b for a, b in _INCIDENT.findall(text)]
    # The [:N] slices cap each list so a giant pasted log can't blow up the prompt.
    return {
        "txn_ids": txns[:10],
        "rrns": list(dict.fromkeys(_RRN.findall(text)))[:10],
        "clusters": sorted({f"C{c}" for c in _CLUSTER.findall(text)}),
        "incidents": list(dict.fromkeys(incidents))[:5],
        "paytmcaller_alerts": list(dict.fromkeys(_ALT.findall(text)))[:5],
        "times": list(dict.fromkeys(m.strip() for m in _TIME.findall(text)))[:5],
        "npci_codes": npci.extract_codes(text, loose=True),
    }


def classify(text: str, ent: dict[str, Any]) -> Intent:
    """First match wins: an id beats keywords, and a short "what is ZM?" becomes a pure lookup."""
    if ent["txn_ids"] or ent["rrns"]:
        return "txn"
    if ent["npci_codes"] and _NPCI_Q.search(text) and len(text) < 240 and not _ALERT_Q.search(text):
        return "npci_lookup"
    if ent["incidents"] or ent["paytmcaller_alerts"] or _ALERT_Q.search(text):
        return "alert"
    # Loop over (pattern, intent) pairs in priority order; the first pattern that matches wins.
    for pat, intent in ((_DB_Q, "db"), (_METRIC_Q, "metrics"), (_LOG_Q, "logs"), (_CODE_Q, "code")):
        if pat.search(text):
            return intent  # type: ignore[return-value]
    return "general"


def _msg(role: str, content: str, node: str) -> Msg:
    """Build one chat-message dict stamped with the current IST time."""
    return {"role": role, "content": content, "ts": datetime.now(IST).isoformat(timespec="seconds"), "node": node}


def _emit(ev: dict[str, Any]) -> None:
    """Push a live event (tool call, text token, warning…) to whoever is streaming the graph.

    Inside `graph.astream(..., stream_mode=["custom"])` these come out as `("custom", ev)` chunks;
    `server.py` forwards them to the browser over SSE and `cli.py` prints them. The work is done
    by `llm.emit` (it uses LangGraph's `get_stream_writer()`); this name keeps the nodes short.
    """
    llm.emit(ev)


async def triage(state: DebugState) -> dict[str, Any]:
    """Node 1. Decide system + intent, extract entities, and reset the per-turn fields.

    This is a LangGraph node: it gets the whole state and returns only the keys it changes.
    It is `async` because LangGraph expects that shape, even though nothing here waits on I/O.
    """
    q = state["question"].strip()  # .strip() removes spaces/newlines at both ends
    opts = state.get("options") or {}
    # "X if condition else Y" is Python's one-line if/else. If the UI forced a system, use it.
    forced = opts.get("system") if opts.get("system") in {"tpap", "tsp"} else None
    pending = state.get("pending_question")
    detected = forced or detect_system(q)
    # answer to a clarify prompt: "tsp" → re-run the question that was waiting
    if pending and (detected or q.lower() in {"tpap", "tsp"}) and len(q) <= 40:
        detected = detected or q.lower()
        q = pending
    # nothing detected this turn → keep the system from the previous turn of the thread
    system = detected or state.get("system")
    ent = extract_entities(q)
    # C2/C3/C6 are TSP switch clusters. `any(...)` is True if at least one item satisfies the test.
    if not detected and ent["clusters"] and any(c in {"C2", "C3", "C6"} for c in ent["clusters"]):
        system = system or "tsp"
    intent = classify(q, ent)
    # Per-turn fields (review, loops, plan…) are reset here so a follow-up starts clean;
    # history lists (messages/runs/tool_log) are appended to, not reset.
    out: dict[str, Any] = {
        "question": q, "system": system, "intent": intent, "entities": ent, "pending_question": None,
        "needs_input": False, "review": None, "loops": 0, "plan": "", "findings": "", "tool_calls": 0, "evidence_nudges": 0,
        "turn": (state.get("turn") or 0) + 1,
        "now_ist": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST (%a)"),
        # A one-item list: the `operator.add` reducer appends it to the saved message history.
        "messages": [_msg("user", state["question"], "triage")],
    }
    _emit({"type": "triage", "system": system, "intent": intent, "entities": ent})
    # LangGraph merges `out` into the state, then calls `route_after_triage` to pick the next node.
    return out


def route_after_triage(state: DebugState) -> str:
    """NPCI lookups need no system; everything else needs one, or we ask the user.

    A *route function*: not a node. It runs right after `triage`, receives the updated state,
    and returns the name (a string) of the node to run next. It must not change the state.
    """
    if state.get("intent") == "npci_lookup":
        return "npci"
    return "npci" if state.get("system") else "clarify"


async def clarify(state: DebugState) -> dict[str, Any]:
    """Ask "tpap or tsp?" and end the turn. The question is parked in `pending_question`;
    the user's next message ("tsp") is picked up by `triage`, which re-runs the parked question."""
    # Strings written side by side inside ( ) are glued into one string by Python.
    text = ("Which system is this on — **TPAP** or **TSP**? They are separate estates with separate "
            "databases, logs and metrics, and I never query both for one question. Reply `tpap` or `tsp` "
            "and I will start.")
    return {"needs_input": True, "pending_question": state["question"], "report": text,
            "messages": [_msg("assistant", text, "clarify")]}


# --------------------------------------------------------------------------------------------
# npci
# --------------------------------------------------------------------------------------------

async def npci_node(state: DebugState) -> dict[str, Any]:
    """Translate NPCI codes found in the question (ZM, U30…) so the prompts can carry the meaning."""
    # `.get(key, default)` returns `default` when the key is missing; chained here twice.
    codes = state.get("entities", {}).get("npci_codes", [])
    resolved = npci.resolve(codes)
    # No exact code found for a "what does X mean" question → fall back to a word search.
    if state.get("intent") == "npci_lookup" and not resolved:
        resolved = npci.search(state["question"], limit=10)
    md = npci.as_markdown(resolved) if resolved else ""
    _emit({"type": "npci", "codes": [r["code"] for r in resolved]})
    return {"npci": resolved, "npci_md": md}


def route_after_npci(state: DebugState) -> str:
    """Pure lookup → straight to report. Otherwise plan first, except on follow-ups, where the
    agent's earlier conversation (with all its tool results) is still in the state and a fresh
    plan would only cost time."""
    if state.get("intent") == "npci_lookup":
        return "report"
    s = get_settings()
    # per-request option wins over the AGENT_PLAN setting
    plan_on = (state.get("options") or {}).get("plan", s.plan_enabled)
    if plan_on and not _is_follow_up(state):
        return "plan"
    return "investigate"


def _is_follow_up(state: DebugState) -> bool:
    """An agent conversation exists from an earlier turn, and it was for the same system."""
    return bool(state.get("agent_messages")) and state.get("agent_system") == state.get("system")


# --------------------------------------------------------------------------------------------
# LLM nodes and the tool loop
#
# plan and review: one model call each, no tools. The investigation is split over nodes:
#   investigate  plain Python: adds the task (question / follow-up / reviewer gaps) as a message
#   agent        one model call with the tools bound; the reply may contain tool calls
#   tools        LangGraph's prebuilt ToolNode: runs those tool calls, adds ToolMessages
#   ask_user     the model called AskUser: show its question and end the turn
# route_after_agent decides between them. Nodes that need the tool belt are built by small
# factory functions (`make_*`), because a node only receives the state, not the belt.
# --------------------------------------------------------------------------------------------

def make_plan_node(belt: ToolBelt) -> Callable[[DebugState], Awaitable[dict[str, Any]]]:
    async def plan(state: DebugState) -> dict[str, Any]:
        """LLM node. Writes a short numbered plan (which tool, which query). No tool calls."""
        tools = belt.for_state(dict(state))
        msgs = [llm.system_message(prompts.system_prompt("plan")), HumanMessage(prompts.plan_prompt(dict(state), tools))]
        ai, run = await llm.call(llm.chat_model(), msgs, node="plan")
        return {"plan": ai.text, "runs": [run]}
    return plan


async def investigate(state: DebugState) -> dict[str, Any]:
    """Start (or continue) the agent's conversation with one new HumanMessage.

    Three situations, each with a different prompt (see `prompts.investigate_prompt`):
      * first pass of a new question,
      * follow-up question in the same thread (the earlier tool results are still in the messages),
      * second pass after the reviewer found gaps.
    """
    system = state.get("system")
    follow = _is_follow_up(state)
    task = HumanMessage(prompts.investigate_prompt(dict(state), follow_up=follow and not state.get("review")))
    new: list[AnyMessage] = [task]
    out: dict[str, Any] = {"agent_messages": new, "agent_system": system}
    if state.get("agent_messages") and not follow:
        # A conversation from the other system: drop it so TPAP evidence never leaks into a TSP run.
        out.update(agent_messages=[RemoveMessage(id=REMOVE_ALL_MESSAGES), task], agent_summary="", context_tokens=0)
    return out


def route_before_agent(state: DebugState) -> str:
    """High watermark: compact first when the agent's last prompt was at or over the trigger.

    Checked once per turn (investigate → here), so compaction always cuts at a turn boundary and
    happens rarely: each compaction rewrites the start of the prompt, which costs one cache miss.
    """
    return "compact" if (state.get("context_tokens") or 0) >= get_settings().compact_trigger_tokens else "agent"


_SUMMARY_SYSTEM = """You compress the history of a production investigation so the investigator can
continue without it. Keep, exactly as written: every txn id, RRN, status, NPCI / response code,
cluster or shard, timestamp and number; every query, log search or metric already run, with its
key result (so it is not repeated); the conclusions so far; open questions. Drop raw rows, log lines
and anything already superseded. If an earlier summary is given, merge it in. Plain markdown, at
most 400 words."""


def _transcript(msgs: list[AnyMessage], tool_chars: int = 1500) -> str:
    """Render messages as plain text for the summarizer (tool results cut to `tool_chars`)."""
    lines = []
    for m in msgs:
        if isinstance(m, HumanMessage):
            lines.append(f"## TASK\n{m.content}")
        elif isinstance(m, AIMessage):
            if m.text:
                lines.append(f"## INVESTIGATOR\n{m.text}")
            lines += [f"→ called {tc['name']}({json.dumps(tc['args'], ensure_ascii=False, default=str)})"
                      for tc in m.tool_calls]
        elif isinstance(m, ToolMessage):
            body = m.content if isinstance(m.content, str) else json.dumps(m.content, default=str)
            lines.append(f"← {m.name or 'tool'} result: {body[:tool_chars]}")
    return "\n".join(lines)


async def compact(state: DebugState) -> dict[str, Any]:
    """Low watermark: summarize everything before the last AGENT_COMPACT_KEEP_TURNS turns.

    A turn starts at a HumanMessage, so the cut never separates a tool call from its result (the
    API rejects a tool_use without its tool_result). The summary goes into the system prompt and
    the old messages are deleted from the state with RemoveMessage.
    """
    s = get_settings()
    msgs = list(state.get("agent_messages") or [])
    starts = [i for i, m in enumerate(msgs) if isinstance(m, HumanMessage)]
    cut = starts[-s.compact_keep_turns] if len(starts) > s.compact_keep_turns else 0
    if cut == 0:
        return {"context_tokens": 0}  # nothing old enough to fold away yet
    old = msgs[:cut]
    previous = state.get("agent_summary") or ""
    prompt = (f"Earlier summary:\n{previous}\n\n" if previous else "") + "History to compress:\n" + _transcript(old)
    ai, run = await llm.call(llm.chat_model(s.summary_model),
                             [SystemMessage(_SUMMARY_SYSTEM), HumanMessage(prompt)],
                             node="compact", model_name=s.summary_model)
    _emit({"type": "warning", "text": f"compacted {len(old)} older messages into a summary"})
    return {"agent_messages": [RemoveMessage(id=m.id) for m in old if m.id],
            "agent_summary": ai.text, "context_tokens": 0, "runs": [run]}


def make_agent_node(belt: ToolBelt) -> Callable[[DebugState], Awaitable[dict[str, Any]]]:
    async def agent(state: DebugState) -> dict[str, Any]:
        """LLM node with tools. One model call; the reply either asks for tools or is the answer."""
        s = get_settings()
        tools = belt.for_state(dict(state))
        used = state.get("tool_calls") or 0
        summary = state.get("agent_summary")
        extra = f"<earlier-turns-summary>\n{summary}\n</earlier-turns-summary>" if summary else ""
        # Skills carry the cache breakpoint; the summary sits after it (see llm.system_message).
        msgs: list[AnyMessage] = [llm.system_message(prompts.system_prompt("investigate"), extra)]
        msgs += state.get("agent_messages") or []
        if used >= s.max_tool_calls:
            # Budget spent: tell the model, and forbid tool calls for this one request.
            msgs.append(HumanMessage("Tool budget for this turn is used up. Write the final answer now "
                                     "from the evidence you already have."))
            model = llm.chat_model().bind_tools([*tools, AskUser], tool_choice={"type": "none"})
        else:
            # bind_tools sends every tool's name, description and JSON schema with the request.
            model = llm.chat_model().bind_tools([*tools, AskUser])
        # Automatic caching: a second breakpoint on the last message caches the conversation so far.
        ai, run = await llm.call(llm.with_cache(model), msgs, node="agent")
        out: dict[str, Any] = {"agent_messages": [ai], "tool_calls": used + len(ai.tool_calls), "runs": [run],
                               "servers": belt.servers_for(dict(state)), "context_tokens": run["input_tokens"]}
        if not ai.tool_calls:
            missing = missing_evidence(state)
            if missing and not state.get("evidence_nudges") and used < s.max_tool_calls:
                # Required-evidence gate: an answer about a txn must rest on its DB data. Send the
                # agent back once to fetch it; route_after_agent sees the HumanMessage and loops.
                out["agent_messages"] = [ai, HumanMessage(
                    "Before answering, fetch the evidence a correct answer needs: " + "; ".join(missing)
                    + ". Then write the full answer again, ending with the ## Proof section.")]
                out["evidence_nudges"] = 1
            else:
                out["findings"] = ai.text  # no tool calls = the model's final answer
        return out
    return agent


def missing_evidence(state: DebugState) -> list[str]:
    """What a correct answer must be based on, but the agent hasn't fetched yet.

    A txn id in the question needs its DB rows (get_txn); an RRN needs find_txn_by_rrn. Checked in
    code, so "the answer is based on the DB data" doesn't depend on the model remembering.
    """
    ent = state.get("entities") or {}
    fetched = set(state.get("txn_rows") or {})  # get_txn records every txn it looked up, found or not
    called = {tc["name"] for m in state.get("agent_messages") or [] if isinstance(m, AIMessage)
              for tc in m.tool_calls}
    missing = [f"the DB rows for txn {t} (call get_txn)" for t in ent.get("txn_ids", []) if t not in fetched]
    if ent.get("rrns") and "find_txn_by_rrn" not in called:
        missing.append(f"the txn for RRN {', '.join(ent['rrns'])} (call find_txn_by_rrn)")
    return missing


def route_after_agent(state: DebugState) -> str:
    """Tool calls → run them (or ask the user, for AskUser). Sent back for missing evidence → the
    agent again. No tool calls → the answer is done."""
    msgs = state.get("agent_messages") or []
    last = msgs[-1] if msgs else None
    if isinstance(last, HumanMessage):
        return "agent"  # the evidence gate added an instruction
    if isinstance(last, AIMessage) and last.tool_calls:
        if any(tc["name"] == AskUser.__name__ for tc in last.tool_calls):
            return "ask_user"
        return "tools"
    return "npci_enrich"


def make_tool_guard(belt: ToolBelt) -> Callable[..., Awaitable[ToolMessage | Command]]:
    """Wrap every tool call ToolNode makes (`awrap_tool_call`). Around the real call it:
      * refuses tools that aren't allowed for this system (the model could invent a name),
      * sends tool_use / tool_result events to the UI,
      * cuts long results to AGENT_TOOL_OUTPUT_CHARS so the conversation and checkpoints stay small,
      * appends a record to `state.tool_log` (by returning a Command instead of a bare ToolMessage).
    """
    async def guard(request: ToolCallRequest, execute: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command]]):
        tc = request.tool_call
        state = request.state if isinstance(request.state, dict) else {}
        t0 = time.monotonic()
        llm.emit({"type": "tool_use", "node": "tools", "id": tc["id"], "name": tc["name"], "input": tc["args"]})
        if tc["name"] not in belt.names_for(state):
            out: ToolMessage | Command = ToolMessage(
                f"Tool {tc['name']!r} is not available for system {state.get('system')!r}.",
                tool_call_id=tc["id"], name=tc["name"], status="error")
        else:
            out = await execute(request)
        update = dict(out.update) if isinstance(out, Command) and isinstance(out.update, dict) else {}
        msg = out if isinstance(out, ToolMessage) else next(
            (m for m in update.get("agent_messages", []) if isinstance(m, ToolMessage)), None)
        text = ""
        if msg is not None:
            text = msg.content if isinstance(msg.content, str) else json.dumps(msg.content, default=str)
            limit = get_settings().tool_output_chars
            if len(text) > limit:
                msg.content = text[:limit] + f"\n… cut: {len(text) - limit} more characters. Narrow the query."
        ms = int((time.monotonic() - t0) * 1000)
        is_error = msg is not None and msg.status == "error"
        llm.emit({"type": "tool_result", "node": "tools", "id": tc["id"], "is_error": is_error,
                  "preview": text[:3000], "chars": len(text), "ms": ms})
        record = {"node": "tools", "turn": state.get("turn"), "name": tc["name"], "is_error": is_error,
                  "chars": len(text), "ms": ms,
                  "input": json.dumps(tc["args"], ensure_ascii=False, default=str)[:1500], "preview": text[:600]}
        if isinstance(out, Command):
            return Command(update={**update, "tool_log": [record]})
        return Command(update={"agent_messages": [out], "tool_log": [record]})
    return guard


async def ask_user(state: DebugState) -> dict[str, Any]:
    """The model called AskUser: show its question and end the turn.

    Every tool_use in the last AIMessage must get a ToolMessage answer, or the next API call is
    rejected, so each call is answered here (AskUser with "asked", anything else with "not run").
    """
    last = state["agent_messages"][-1]
    assert isinstance(last, AIMessage)
    question = next(tc["args"].get("question", "") for tc in last.tool_calls if tc["name"] == AskUser.__name__)
    replies = [ToolMessage("Question shown to the user; their answer arrives as the next message."
                           if tc["name"] == AskUser.__name__ else "Not run: waiting for the user's answer first.",
                           tool_call_id=tc["id"], name=tc["name"]) for tc in last.tool_calls]
    text = f"**I need one thing from you before I go on:** {question}"
    return {"agent_messages": replies, "needs_input": True, "report": text,
            "messages": [_msg("assistant", text, "ask_user")]}


async def npci_enrich(state: DebugState) -> dict[str, Any]:
    """Second NPCI pass: translate codes the investigator found in logs/DB (not in the question)."""
    known = {r["code"] for r in state.get("npci") or []}  # codes already translated
    found = npci.extract_codes(state.get("findings", ""))
    # Old list + only the NEW codes. `npci` has no reducer, so returning it replaces the old list.
    merged = (state.get("npci") or []) + npci.resolve([c for c in found if c not in known])
    _emit({"type": "npci", "codes": [r["code"] for r in merged]})
    return {"npci": merged, "npci_md": npci.as_markdown(merged) if merged else ""}


def route_after_enrich(state: DebugState) -> str:
    """Run the reviewer unless it is switched off (UI checkbox or AGENT_REVIEW=0)."""
    on = (state.get("options") or {}).get("review", get_settings().review_enabled)
    return "review" if on else "report"


# Everything from the first "{" to the last "}". re.S lets "." also match newlines.
_JSON_OBJ = re.compile(r"\{.*\}", re.S)


def parse_review(text: str) -> dict[str, Any]:
    """Pull the reviewer's JSON verdict out of its reply. Anything unparseable counts as "pass",
    so a chatty reviewer can never trap the graph in an investigate ↔ review loop."""
    m = _JSON_OBJ.search(text or "")
    if m:
        try:
            data = json.loads(m.group(0))  # JSON text → Python dict; raises JSONDecodeError if broken
            if isinstance(data, dict):     # isinstance(x, T) = "is x of type T?"
                gaps = [str(g) for g in data.get("gaps") or []][:6]
                verdict = "gaps" if data.get("verdict") == "gaps" and gaps else "pass"
                return {"verdict": verdict, "score": data.get("score"), "gaps": gaps,
                        "summary": str(data.get("summary", ""))[:300]}
        except json.JSONDecodeError:
            pass
    return {"verdict": "pass", "score": None, "gaps": [], "summary": "reviewer reply was not JSON; accepted as is"}


async def review(state: DebugState) -> dict[str, Any]:
    """LLM node. Grades the investigator's answer and lists missing evidence. No tool calls."""
    msgs = [llm.system_message(prompts.system_prompt("review")), HumanMessage(prompts.review_prompt(dict(state)))]
    ai, run = await llm.call(llm.chat_model(), msgs, node="review")
    verdict = parse_review(ai.text)
    _emit({"type": "review", **verdict})
    # `loops` counts review rounds; route_after_review uses it to stop after the allowed number.
    return {"review": verdict, "loops": (state.get("loops") or 0) + 1, "runs": [run]}


def route_after_review(state: DebugState) -> str:
    """Gaps found and loop budget left (AGENT_MAX_REVIEW_LOOPS) → investigate again; else report."""
    rv = state.get("review") or {}
    if rv.get("verdict") == "gaps" and (state.get("loops") or 0) <= get_settings().max_review_loops:
        return "investigate"
    return "report"


# --------------------------------------------------------------------------------------------
# report (deterministic)
# --------------------------------------------------------------------------------------------


def _proof_from_state(state: DebugState) -> str:
    """The proof appended by code, from the state, so it's there even if the model forgets.

    The DB data comes from `txn_rows` (written by the get_txn tool, not by the model) and the tool
    list from `tool_log`. A txn question without DB data gets a visible warning.
    """
    lines = ["## Proof from the system", "_Built from the tool results in the graph state, not written by the model._"]
    rows = state.get("txn_rows") or {}
    found = {k: v for k, v in rows.items() if v.get("found")}
    if found:
        lines += ["", "**Database (`txn_info`, via `get_txn`)**", "",
                  "| txn_id | shard | status | NPCI code | amount | created_on | participants |",
                  "|---|---|---|---|---|---|---|"]
        lines += [f"| `{k}` | {v.get('db')} | {v.get('status')} | {v.get('npci_resp_code') or ''} | {v.get('amount')} "
                  f"| {v.get('created_on')} | {v.get('participants')} |" for k, v in found.items()]
    asked = (state.get("entities") or {}).get("txn_ids") or []
    unverified = [t for t in asked if t not in found]
    if unverified:
        lines += ["", f"> ⚠️ **Not verified against the database:** no `txn_info` row for "
                      f"{', '.join(f'`{t}`' for t in unverified)} (older than ~7 days, or the wrong system)."]
    calls = [r for r in state.get("tool_log") or [] if r.get("turn") == state.get("turn")]
    if calls:
        lines += ["", "**Tool calls behind this answer**", ""]
        lines += [f"- `{r['name']}` {r.get('input', '')[:160]} → {'error' if r.get('is_error') else f'{r.get('chars', 0)} chars'}"
                  for r in calls]
    return "\n".join(lines)


async def report(state: DebugState) -> dict[str, Any]:
    """Last node. Glue findings + txn table + NPCI table + reviewer verdict into the markdown the user sees."""
    if state.get("intent") == "npci_lookup":
        body = "## NPCI codes\n\n" + (state.get("npci_md") or "No matching NPCI code found in the code map.")
        return {"report": body, "messages": [_msg("assistant", body, "report")]}
    # Build the report as a list of markdown chunks, then join them with blank lines.
    parts = [state.get("findings", "").strip() or "_The investigator returned no text._"]
    parts.append(_proof_from_state(state))
    if state.get("npci_md"):
        parts.append("## NPCI code map\n\n" + state["npci_md"])
    rv = state.get("review")
    if rv:
        gaps = "".join(f"\n- {g}" for g in rv.get("gaps") or [])
        score = f" · score {rv['score']}/10" if rv.get("score") is not None else ""
        parts.append(f"> **Reviewer:** {rv.get('verdict')}{score} — {rv.get('summary', '')}{gaps}")
    body = "\n\n".join(parts)
    return {"report": body, "messages": [_msg("assistant", body, "report")]}


def _servers(state: DebugState) -> list[mcp_config.ServerInfo]:
    """MCP servers for this run: the detected system's + shared, optionally narrowed by the UI."""
    only = (state.get("options") or {}).get("servers")
    return mcp_config.servers_for(state.get("system"), only=only)


# --------------------------------------------------------------------------------------------
# wiring
# --------------------------------------------------------------------------------------------

# Only used to draw the UI diagram (graph_spec); the real wiring is build_graph() below.
NODES = ["triage", "clarify", "npci", "plan", "investigate", "compact", "agent", "tools", "ask_user",
         "npci_enrich", "review", "report"]
LLM_NODES = {"plan", "compact", "agent", "review"}  # a set: fast "is this in it?" checks


def build_graph(belt: ToolBelt | None = None) -> StateGraph:
    """Assemble the pipeline. Callers `.compile(checkpointer=...)` it before running.

    `belt` holds the tools (native + MCP). Without one, only the native tools are available,
    which is what `ai-debugger graph` uses.

    `add_edge(a, b)` = always go a → b. `add_conditional_edges(a, fn, [...])` = after a, call
    `fn(state)` and go to the node name it returns (the list declares the possible targets).

    Read the lines below top to bottom and you are reading the flowchart in the module docstring.
    """
    belt = belt or ToolBelt()
    # Tell LangGraph what the state looks like (this is how it learns about the reducers).
    g = StateGraph(DebugState)
    # Register each box: add_node("name used in edges", the Python function to run).
    # Note we pass the function itself (`triage`), not a call (`triage()`): LangGraph calls it later.
    g.add_node("triage", triage)
    g.add_node("clarify", clarify)
    g.add_node("npci", npci_node)
    g.add_node("plan", make_plan_node(belt))
    g.add_node("investigate", investigate)
    g.add_node("compact", compact)
    g.add_node("agent", make_agent_node(belt))
    # ToolNode must know every tool it may be asked to run; the agent only *offers* the model the
    # tools for the current system. messages_key: our messages live in `agent_messages`.
    # handle_tool_errors=True: an exception in a tool becomes an error ToolMessage the model can
    # read and react to (fix the SQL, try another tool) instead of crashing the run.
    g.add_node("tools", ToolNode(belt.all(), messages_key="agent_messages", handle_tool_errors=True,
                                 awrap_tool_call=make_tool_guard(belt)))
    g.add_node("ask_user", ask_user)
    g.add_node("npci_enrich", npci_enrich)
    g.add_node("review", review)
    g.add_node("report", report)
    # Now the arrows.
    g.add_edge(START, "triage")
    g.add_conditional_edges("triage", route_after_triage, ["clarify", "npci"])
    g.add_edge("clarify", END)
    g.add_conditional_edges("npci", route_after_npci, ["report", "plan", "investigate"])
    g.add_edge("plan", "investigate")
    g.add_conditional_edges("investigate", route_before_agent, ["compact", "agent"])
    g.add_edge("compact", "agent")
    g.add_conditional_edges("agent", route_after_agent, ["tools", "ask_user", "npci_enrich", "agent"])
    g.add_edge("tools", "agent")  # the loop: tool results go back to the model
    g.add_edge("ask_user", END)
    g.add_conditional_edges("npci_enrich", route_after_enrich, ["review", "report"])
    g.add_conditional_edges("review", route_after_review, ["investigate", "report"])
    g.add_edge("report", END)
    # Not runnable yet: the caller does `build_graph(belt).compile(checkpointer=saver)`.
    return g


def graph_spec() -> dict[str, Any]:
    """Nodes + edges for the UI's pipeline view. Keep in step with `build_graph()` by hand."""
    return {
        "nodes": [{"id": n, "llm": n in LLM_NODES} for n in NODES],
        "edges": [["triage", "clarify"], ["triage", "npci"], ["npci", "plan"], ["npci", "investigate"],
                  ["npci", "report"], ["plan", "investigate"], ["investigate", "agent"], ["investigate", "compact"],
                  ["compact", "agent"], ["agent", "tools"],
                  ["tools", "agent"], ["agent", "ask_user"], ["agent", "npci_enrich"],
                  ["npci_enrich", "review"], ["npci_enrich", "report"], ["review", "investigate"],
                  ["review", "report"]],
    }
