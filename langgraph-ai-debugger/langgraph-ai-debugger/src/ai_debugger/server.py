"""FastAPI app: the UI plus an SSE stream of every graph node, LLM token and tool call.

The interesting endpoint is `POST /api/chat`:

    browser ──POST /api/chat──▶ chat()  ── starts ──▶ _run() as a background asyncio task
       ▲                          │                      │ graph.astream(...) yields node + custom events
       └──── SSE "data: {...}" ◀──┴── stream() ◀─ queue ◀┘

`_run` and the HTTP response are decoupled by an `asyncio.Queue`, so the graph keeps running
even while the browser is slow to read. Everything else is small read endpoints for the
sidebar (threads), the MCP panel, the NPCI panel and the graph view.

Background for beginners
------------------------
* **FastAPI** is a web framework. You write a normal Python function and put a *decorator*
  above it, e.g. `@app.get("/api/threads")`. That line means: "when a browser sends an HTTP GET
  to /api/threads, call this function and send back whatever it returns". A returned dict is
  turned into JSON automatically.
* `{tid}` in a path (`/api/threads/{tid}`) is a placeholder: FastAPI pulls that part of the URL
  out and passes it as the function argument named `tid`.
* **pydantic** `BaseModel` classes describe the JSON a request must contain. FastAPI reads the
  request body, checks it against the class, and hands you a ready object (or answers 422
  "invalid request" by itself if the JSON is wrong).
* `HTTPException(404, "...")` — raising it makes FastAPI answer with that HTTP status code.
* **uvicorn** (started from `cli.py serve`) is the actual web server that runs this `app`.
* **SSE (Server-Sent Events)** — a normal HTTP response that is kept open; the server keeps
  writing `data: {...}\n\n` chunks to it and the browser reads them one by one. That is how the
  UI shows progress live without polling.
* An **asyncio Task** is a job running in the background inside the same program;
  `asyncio.create_task(f())` starts one. An **asyncio Queue** is a pipe between two jobs: one
  side `put`s items in, the other side `get`s them out (waiting if it's empty).
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from pydantic import BaseModel, Field

from . import __version__, mcp_config, mcp_probe, npci
from .config import VAR_DIR, get_settings
from .graph import build_graph, graph_spec
from .store import ThreadStore
from .tools import ToolBelt, load_belt

# Folder with index.html, app.js, style.css. `__file__` = path of this .py file.
STATIC = Path(__file__).with_name("static")
IST = timezone(timedelta(hours=5, minutes=30))  # the daily limit resets at midnight IST


def current_user(request: Request) -> str:
    """The logged-in user. The app sits behind the company login, which puts the user's name in
    the AUTH_USER_HEADER header (default `X-Forwarded-User`) of every request it forwards.

    The header is trustworthy because the login layer is the only way to reach the app and it
    overwrites whatever the browser sent. A request without it didn't come through login: 401.
    """
    name = request.headers.get(get_settings().user_header, "").strip()
    if not name:
        raise HTTPException(401, "not logged in")
    return name


def _today() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d")


# --- request bodies (pydantic validates them; FastAPI returns 422 on bad input) ---

# Example request body for POST /api/chat:
#   {"message": "tsp: is C3 healthy?", "thread_id": null,
#    "options": {"system": "tsp", "plan": true, "review": false, "servers": ["tsp_redash"]}}
class ChatOptions(BaseModel):
    """Per-message overrides. `None` means "use the .env setting"."""
    system: str | None = Field(default=None, description="tpap | tsp | null = auto-detect")
    plan: bool | None = None
    review: bool | None = None
    servers: list[str] | None = None


class ChatRequest(BaseModel):
    # Field(...) adds validation rules: empty or >20k-character messages are rejected with 422.
    message: str = Field(min_length=1, max_length=20000)
    thread_id: str | None = None  # None = start a new thread; an id = follow-up in that thread
    options: ChatOptions = ChatOptions()


class ProbeRequest(BaseModel):
    names: list[str] | None = None
    system: str | None = None


class App:
    """Process-wide singletons, filled in by `lifespan` at startup."""
    graph: Any = None                         # compiled LangGraph with the SQLite checkpointer
    belt: ToolBelt = ToolBelt()               # every tool the agent may call (native + MCP)
    store: ThreadStore                        # sidebar index (title, status, cost per thread)
    runs: dict[str, asyncio.Task[None]] = {}  # thread_id → the task running it right now


# One shared instance, imported by every endpoint below as `state.graph`, `state.store`, …
state = App()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown. The checkpointer connection stays open for the life of the server.

    FastAPI runs everything before `yield` when the server starts, and everything after it when
    the server stops. `async with X as y:` opens X and guarantees it gets closed at the end of
    the block (here: the SQLite connection), even if an error happens.
    """
    s = get_settings()
    VAR_DIR.mkdir(parents=True, exist_ok=True)  # create var/ if missing; no error if it exists
    # Start every MCP server once and turn its tools into LangGraph tools (MCP_LOAD=0 skips this).
    state.belt = await load_belt()
    # The checkpointer = LangGraph's save-file (var/checkpoints.sqlite). Giving it to compile()
    # makes the graph load/save state per thread_id automatically on every run.
    async with AsyncSqliteSaver.from_conn_string(str(s.checkpoint_db)) as saver:
        state.graph = build_graph(state.belt).compile(checkpointer=saver)
        state.store = ThreadStore(VAR_DIR / "threads.sqlite")
        await state.store.open()
        try:
            yield  # ← the server runs and serves requests while we are paused here
        finally:
            for t in state.runs.values():
                t.cancel()
            await state.store.close()


# The web application object. uvicorn is pointed at "ai_debugger.server:app" (see cli.py).
app = FastAPI(title="LangGraph AI Debugger", version=__version__, lifespan=lifespan)
# Serve files in static/ as-is: GET /static/app.js returns static/app.js.
app.mount("/static", StaticFiles(directory=STATIC), name="static")


# --------------------------------------------------------------------------------------------
# read endpoints used by the UI panels
# --------------------------------------------------------------------------------------------

@app.get("/")  # decorator: "GET / runs this function"
async def index() -> FileResponse:
    """The single HTML page. Everything else on the page is loaded by app.js via /api/*."""
    return FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-store"})


@app.get("/api/health")
async def health() -> dict[str, Any]:
    """Is the server up, is an API key set, how many tools loaded. Try it: curl :8077/api/health"""
    s = get_settings()
    return {"ok": True, "version": __version__, "api_key": bool(s.anthropic_api_key), "model": s.model,
            "tools": len(state.belt.all()), "mcp_errors": state.belt.mcp_errors,
            "graph": state.graph is not None, "running": sorted(state.runs)}


@app.get("/api/config")
async def config() -> dict[str, Any]:
    """Settings + graph shape, fetched once by app.js `boot()` when the page loads."""
    s = get_settings()
    return {"model": s.model, "plan": s.plan_enabled, "review": s.review_enabled,
            "max_review_loops": s.max_review_loops, "max_tool_calls": s.max_tool_calls, "graph": graph_spec(),
            "npci_codes": len(npci.code_map()), "version": __version__}


@app.get("/api/graph")
async def graph_view() -> dict[str, Any]:
    """The graph as Mermaid diagram text, generated by LangGraph from the compiled graph."""
    mermaid = state.graph.get_graph().draw_mermaid() if state.graph else ""
    return {**graph_spec(), "mermaid": mermaid}


@app.get("/api/mcp")
async def mcp_list() -> dict[str, Any]:
    """MCP panel: every server in config/mcp_servers.json, its blocked tools, missing .env keys,
    how many tools were loaded at startup (or why it failed), and the last probe result."""
    probes = mcp_probe.cached()
    # One dict per server, built with a list comprehension (the `for` is on the last line).
    return {"servers": [
        {"name": s.name, "system": s.system, "label": s.label, "kind": s.kind, "deny": list(s.deny),
         "default_off": s.default_off, "missing_env": mcp_config.missing_env(s.name),
         "disabled": s.name in get_settings().disabled_servers, "probe": probes.get(s.name),
         "tools_loaded": len(state.belt.mcp_tools.get(s.name, [])), "load_error": state.belt.mcp_errors.get(s.name)}
        for s in mcp_config.catalogue()]}


@app.post("/api/mcp/probe")
async def mcp_probe_run(req: ProbeRequest) -> dict[str, Any]:
    """Actually start the servers and list their tools (slow: up to 90s per server)."""
    cat = mcp_config.catalogue()
    names = req.names or [s.name for s in cat if req.system in (None, s.system, "shared") or s.system == "shared"]
    known = {s.name for s in cat}
    names = [n for n in names if n in known]
    return {"results": await mcp_probe.probe_many(names)}


@app.get("/api/npci")
async def npci_lookup(q: str = "", limit: int = 30) -> dict[str, Any]:
    """NPCI search box. Arguments not in the path come from the query string: /api/npci?q=ZM&limit=5."""
    q = q.strip()
    if not q:
        return {"results": [], "count": len(npci.code_map())}
    exact = npci.resolve(npci.extract_codes(q, loose=True)) or npci.resolve([q.upper()])
    return {"results": exact or npci.search(q, limit=limit), "count": len(npci.code_map())}


@app.get("/api/usage")
async def usage(request: Request) -> dict[str, Any]:
    """The caller's questions and cost today, cost this month, and both limits (0 = no limit)."""
    user, s = current_user(request), get_settings()
    return {"user": user, "day": _today(), "limit": s.daily_questions_per_user,
            **await state.store.usage(user, _today()),
            "month_cost_usd": round(await state.store.month_cost(user, _today()[:7]), 2),
            "monthly_budget_usd": s.monthly_budget_usd_per_user}


@app.get("/api/threads")
async def threads() -> dict[str, Any]:
    """Sidebar list, newest first."""
    rows = await state.store.list()
    for r in rows:
        r["running"] = r["id"] in state.runs
    return {"threads": rows}


@app.get("/api/threads/{tid}")
async def thread(tid: str) -> dict[str, Any]:
    """Re-open a thread: sidebar metadata + the latest checkpointed graph state."""
    meta = await state.store.get(tid)
    # aget_state = "load the latest saved state of this thread" from the checkpointer (no run).
    # snap.values is the DebugState dict; snap.next lists nodes still pending (empty when finished).
    snap = await state.graph.aget_state({"configurable": {"thread_id": tid}})
    if not meta and not snap.values:
        raise HTTPException(404, "no such thread")
    v = snap.values or {}
    keep = ("messages", "runs", "tool_log", "system", "intent", "entities", "npci", "plan", "review", "report",
            "needs_input", "tool_calls", "txn_rows", "servers", "question", "agent_summary", "context_tokens")
    return {"meta": meta, "running": tid in state.runs, "next": list(snap.next or []),
            "state": {k: v.get(k) for k in keep}}


@app.get("/api/threads/{tid}/trace")
async def thread_trace(tid: str) -> dict[str, Any]:
    """The route the graph actually took, rebuilt from checkpoint history (oldest first)."""
    # aget_state_history yields every saved checkpoint, newest first. `[x async for x in ...]`
    # collects an async stream into a list; .reverse() then puts it oldest first.
    snaps = [s async for s in state.graph.aget_state_history({"configurable": {"thread_id": tid}})]
    snaps.reverse()
    steps: list[dict[str, Any]] = []
    turn = 0
    # A checkpoint is saved before each step; `s.next` names the node(s) about to run. The time
    # between two consecutive checkpoints is therefore how long that node took.
    for i, s in enumerate(snaps):
        nxt = list(s.next or [])
        if "__start__" in nxt:  # a new user message begins a new turn
            turn += 1
            continue
        end = snaps[i + 1].created_at if i + 1 < len(snaps) else None
        for node in nxt:
            ms = None
            if end and s.created_at:
                ms = round((datetime.fromisoformat(end) - datetime.fromisoformat(s.created_at)).total_seconds() * 1000)
            steps.append({"node": node, "turn": turn, "at": s.created_at, "ms": ms, "done": end is not None})
    return {"thread_id": tid, "turns": turn, "steps": steps}


@app.delete("/api/threads/{tid}")
async def delete_thread(tid: str) -> dict[str, Any]:
    """Remove a thread everywhere: sidebar row and LangGraph checkpoints."""
    if tid in state.runs:
        raise HTTPException(409, "thread is running; cancel it first")
    await state.store.delete(tid)
    # contextlib.suppress(Exception) = "ignore any error inside this block" (a short try/except/pass).
    with contextlib.suppress(Exception):
        await state.graph.checkpointer.adelete_thread(tid)
    return {"deleted": tid}


@app.post("/api/threads/{tid}/cancel")
async def cancel(tid: str) -> dict[str, Any]:
    """Stop button: cancel the asyncio task running the graph.

    The task's current `await` (an API call, a tool) raises CancelledError, which `_run` catches.
    The last checkpoint stays, so the thread can be continued later.
    """
    task = state.runs.get(tid)
    if task:
        task.cancel()
    return {"cancelled": bool(task)}


# --------------------------------------------------------------------------------------------
# chat: run the graph in the background and stream its events as Server-Sent Events
# --------------------------------------------------------------------------------------------

def _sse(ev: dict[str, Any]) -> bytes:
    """One SSE frame: `data: <json>` followed by a blank line."""
    return f"data: {json.dumps(ev, ensure_ascii=False, default=str)}\n\n".encode()


def _node_summary(name: str, result: Any) -> dict[str, Any]:
    """The few fields of a node's output worth sending with its `node_end` event."""
    if not isinstance(result, dict):
        return {}
    pick = {"triage": ("system", "intent", "entities"), "plan": ("plan",), "review": ("review",),
            "npci": (), "npci_enrich": (), "investigate": (), "compact": (), "agent": ("tool_calls", "context_tokens"),
            "tools": (),
            "clarify": ("report",), "ask_user": ("report",), "report": ()}.get(name, ())
    # `{...}.get(name, ())` above looked up which keys to keep for this node; () if unknown.
    out = {k: result.get(k) for k in pick}
    if "runs" in result and result["runs"]:
        out["run"] = result["runs"][-1]
    return out


async def _run(tid: str, req: ChatRequest, q: asyncio.Queue[dict[str, Any] | None], user: str, day: str) -> None:
    """Run one turn of the graph for thread `tid`, pushing every event onto `q`.

    Puts `None` on the queue when finished (success, error or cancel) so `stream()` can close.
    """
    # thread_id makes the checkpointer load this thread's earlier state before running.
    # recursion_limit caps total node executions per turn (guards the tool and review loops).
    cfg = {"configurable": {"thread_id": tid}, "recursion_limit": get_settings().recursion_limit}
    opts = req.options.model_dump(exclude_none=True)
    # Only the new keys are passed in; LangGraph merges them into the saved state.
    inp = {"question": req.message, "options": opts}
    await state.store.update(tid, status="running")
    cost = 0.0
    try:
        # stream_mode "tasks"  → a chunk when each node starts (has "input") and ends (has "result")
        # stream_mode "custom" → whatever the nodes sent through get_stream_writer() (graph._emit)
        async for mode, chunk in state.graph.astream(inp, cfg, stream_mode=["tasks", "custom"]):
            # Each item is a pair (mode, chunk); `async for mode, chunk in ...` unpacks it.
            if mode == "tasks":
                if "input" in chunk:
                    await q.put({"type": "node_start", "node": chunk["name"]})
                else:
                    # chunk["result"] is the dict the node returned (its partial state update).
                    ev = {"type": "node_end", "node": chunk["name"], "error": chunk.get("error"),
                          **_node_summary(chunk["name"], chunk.get("result"))}
                    cost += float((ev.get("run") or {}).get("cost_usd") or 0)
                    await q.put(ev)
            else:
                await q.put(chunk if isinstance(chunk, dict) else {"type": "custom", "data": chunk})
        # Graph finished: read the final state from the checkpoint and send the report.
        snap = await state.graph.aget_state(cfg)
        v = snap.values
        status = "needs_input" if v.get("needs_input") else "done"
        await state.store.update(tid, status=status, system=v.get("system"), intent=v.get("intent"))
        await q.put({"type": "final", "report": v.get("report", ""), "system": v.get("system"),
                     "intent": v.get("intent"), "needs_input": bool(v.get("needs_input")), "cost_usd": round(cost, 4),
                     "runs": [r for r in v.get("runs", [])][-6:], "npci": v.get("npci", [])})
    except asyncio.CancelledError:
        await state.store.update(tid, status="cancelled")
        await q.put({"type": "error", "message": "Run cancelled."})
    except Exception as e:  # noqa: BLE001 — surface every failure to the UI
        await state.store.update(tid, status="error")
        await q.put({"type": "error", "message": f"{type(e).__name__}: {e}"[:2000]})
    finally:
        # Record the money in `finally`, so a cancelled or failed run is counted too: the LLM calls
        # it made before stopping were billed. This is what the monthly budget is checked against.
        # shield(): even while the task is being cancelled, these two writes still complete.
        with contextlib.suppress(Exception):
            await asyncio.shield(state.store.add_cost(tid, cost))
            await asyncio.shield(state.store.add_user_cost(user, day, cost))
        state.runs.pop(tid, None)  # this thread is no longer running
        await q.put(None)          # None = "no more events" signal for stream()


@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request) -> StreamingResponse:
    """Start a turn and return an SSE stream of its events (first event carries the thread id).

    Refused with 429 once the user has spent this month's AGENT_MONTHLY_BUDGET_USD_PER_USER or
    used today's AGENT_DAILY_QUESTIONS_PER_USER questions.
    """
    if req.options.system not in (None, "", "auto", "tpap", "tsp"):
        raise HTTPException(400, "system must be tpap, tsp or auto")
    if req.options.system in ("", "auto"):
        req.options.system = None
    # New conversation → make a random 16-character id. Existing one → keep it (that's what makes the
    # checkpointer load the earlier state, so this message becomes a follow-up).
    tid = req.thread_id or uuid.uuid4().hex[:16]
    if tid in state.runs:
        raise HTTPException(409, "this thread is already running")
    user, day, s = current_user(request), _today(), get_settings()
    # Per-user monthly $ cap, checked before anything costs money. The check is "spent < budget",
    # so the question that crosses the line still finishes: the cap can be overshot by at most
    # one question's cost.
    if s.monthly_budget_usd_per_user > 0:
        spent = await state.store.month_cost(user, day[:7])
        if spent >= s.monthly_budget_usd_per_user:
            raise HTTPException(429, f"Monthly budget reached: ${spent:.2f} of ${s.monthly_budget_usd_per_user:.0f} "
                                     f"this month for {user}. It resets on the 1st (IST).")
    # Per-user daily limit. Checked (and counted) before anything costs money.
    limit = s.daily_questions_per_user
    allowed, used = await state.store.take_question(user, day, limit)
    if not allowed:
        raise HTTPException(429, f"Daily limit reached: {used}/{limit} questions today for {user}. "
                                 "It resets at midnight IST.")
    # Sidebar title = first line of the first message.
    await state.store.upsert(tid, req.message.strip().splitlines()[0])
    q: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
    # Start the graph in the background. We do NOT await it here — we return the stream right away.
    state.runs[tid] = asyncio.create_task(_run(tid, req, q, user, day))

    # An *async generator*: a function with `yield` in it. Each `yield` sends one chunk to the
    # browser; FastAPI's StreamingResponse keeps calling it until it returns.
    async def stream() -> AsyncIterator[bytes]:
        yield _sse({"type": "thread", "thread_id": tid})
        while True:
            try:
                ev = await asyncio.wait_for(q.get(), timeout=15)
            except TimeoutError:
                # SSE comment line as keep-alive, so proxies don't drop a long quiet investigation
                yield b": ping\n\n"
                continue
            if ev is None:
                yield _sse({"type": "done", "thread_id": tid})
                return
            yield _sse(ev)

    # text/event-stream tells the browser this is SSE; no-cache / X-Accel-Buffering stop proxies from
    # holding chunks back.
    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
