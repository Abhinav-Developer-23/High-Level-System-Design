"""`ai-debugger` command line: serve the UI, ask from the terminal, look up NPCI codes, check MCP.

    ai-debugger serve                       # web UI on APP_HOST:APP_PORT (server.py)
    ai-debugger ask "tsp: debug txn ..."    # one investigation, progress on stderr, report on stdout
    ai-debugger npci ZM U30                 # NPCI code lookup, no LLM
    ai-debugger mcp-check [--system tsp]    # start every MCP server and list its tools
    ai-debugger tools [--system tsp]        # the LangGraph tools a run would get
    ai-debugger eval --golden evals/golden.jsonl [--ragas] [--baseline …]   # score the agent
    ai-debugger graph                       # print the LangGraph as mermaid

`ask` runs the same graph as the web UI and shares its checkpoint DB, so `--thread <id>`
continues a conversation started in either place.

Background for beginners
------------------------
* The `ai-debugger` command exists because `pyproject.toml` (section `[project.scripts]`) maps
  it to `main()` in this file. `uv run ai-debugger ...` runs it inside the project's virtualenv.
* **argparse** (standard library) turns the words you type into a Python object: for
  `ai-debugger ask "hi" --system tsp`, it gives `args.question == "hi"`, `args.system == "tsp"`.
  Each subcommand (serve/ask/npci/…) is a "subparser" with its own options.
* Each `cmd_*` function returns an *exit code*: 0 = success, anything else = failure. Shell
  scripts and CI check this number.
* **stdout vs stderr**: `print(x)` goes to stdout (the result); `print(x, file=sys.stderr)` goes
  to stderr (progress/noise). So `ai-debugger ask "..." > report.md` saves just the report.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid
from pathlib import Path
from typing import Any, cast

from langchain_core.runnables import RunnableConfig

from . import mcp_config, mcp_probe, npci
from .config import VAR_DIR, get_settings

# ANSI escape codes: special character sequences a terminal reads as "switch colour".
# "\033[0m" ("off") resets back to normal.
_C = {"dim": "\033[2m", "pink": "\033[38;5;199m", "cyan": "\033[38;5;51m", "lime": "\033[38;5;154m",
      "red": "\033[38;5;203m", "amber": "\033[38;5;214m", "off": "\033[0m"}


def _c(color: str, text: str) -> str:
    """Colour text for the terminal; plain text when stderr is piped to a file."""
    return f"{_C[color]}{text}{_C['off']}" if sys.stderr.isatty() else text


def cmd_serve(args: argparse.Namespace) -> int:
    """Start the web server. Blocks until you press Ctrl+C."""
    # Imported inside the function so other commands (npci, graph) start fast without loading it.
    import uvicorn

    s = get_settings()
    # Two assignments in one line. `--port` from the command line wins over .env.
    host, port = args.host or s.host, args.port or s.port
    print(_c("pink", f"AI Debugger → http://{host}:{port}"), file=sys.stderr)
    uvicorn.run("ai_debugger.server:app", host=host, port=port, log_level="warning", reload=args.reload)
    return 0


async def _ask(args: argparse.Namespace) -> int:
    """Terminal version of `server._run`: same graph, same stream modes, printed instead of SSE."""
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    from .graph import build_graph
    from .tools import load_belt

    VAR_DIR.mkdir(parents=True, exist_ok=True)
    tid = args.thread or f"cli-{uuid.uuid4().hex[:10]}"
    opts: dict[str, Any] = {"system": args.system}
    if args.no_plan:
        opts["plan"] = False
    if args.no_review:
        opts["review"] = False
    # The LangGraph lifecycle in five lines — the same steps server.py does:
    #   1. open the checkpointer (save-file)   2. build + compile the graph with it (and the tools)
    #   3. config = which thread (+ a safety cap on steps)
    #   4. astream(input, config) runs the graph and yields events as nodes start/finish
    #   5. aget_state(config) reads the final saved state (the report is in there)
    belt = await load_belt()
    for name, err in belt.mcp_errors.items():
        print(_c("amber", f"  MCP {name} not loaded: {err[:120]}"), file=sys.stderr)
    async with AsyncSqliteSaver.from_conn_string(str(get_settings().checkpoint_db)) as saver:
        graph = build_graph(belt).compile(checkpointer=saver)
        cfg: RunnableConfig = {"configurable": {"thread_id": tid}, "recursion_limit": get_settings().recursion_limit}
        print(_c("dim", f"thread {tid}"), file=sys.stderr)
        # The input dict is merged into the thread's state; then the graph runs from START.
        async for mode, chunk in graph.astream({"question": args.question, "options": opts}, cfg,
                                               stream_mode=["tasks", "custom"]):
            # cast() only tells the type checker "trust me, this is a dict"; it does nothing at runtime.
            chunk = cast(dict[str, Any], chunk)
            if mode == "tasks":
                if "input" in chunk:
                    print(_c("pink", f"▶ {chunk['name']}"), file=sys.stderr)
                elif chunk.get("error"):
                    print(_c("red", f"✖ {chunk['name']}: {chunk['error']}"), file=sys.stderr)
            elif isinstance(chunk, dict):
                _print_event(chunk, args.verbose)
        snap = await graph.aget_state(cfg)
        v = snap.values
        cost = sum(r.get("cost_usd", 0) for r in v.get("runs", []))
        print(v.get("report", ""))  # the only thing on stdout
        # `{cost:.3f}` = format the number with 3 decimal places.
        print(_c("dim", f"\nthread {tid} · system {v.get('system')} · intent {v.get('intent')} · ${cost:.3f}"),
              file=sys.stderr)
    return 0


def _print_event(ev: dict[str, Any], verbose: bool) -> None:
    """One line on stderr per interesting live event (llm.py and graph.make_tool_guard send them)."""
    t = ev.get("type")
    if t == "triage":
        print(_c("dim", f"  system={ev['system']} intent={ev['intent']}"), file=sys.stderr)
    elif t == "tool_use":
        print(_c("amber", f"  ⚙ {ev['name']} {json.dumps(ev.get('input'), ensure_ascii=False)[:160]}"), file=sys.stderr)
    elif t == "tool_result" and (verbose or ev.get("is_error")):
        print(_c("red" if ev.get("is_error") else "dim", f"    ↳ {ev.get('preview', '')[:200]}"), file=sys.stderr)
    elif t == "agent_end":
        print(_c("lime", f"  ✔ {ev['node']} · {ev['duration_ms'] / 1000:.1f}s · {ev['input_tokens']}→"
                         f"{ev['output_tokens']} tokens ({ev.get('cache_read_tokens', 0)} from cache) · "
                         f"{ev['tool_calls']} tool calls · ${ev['cost_usd']:.3f}"),
              file=sys.stderr)
    elif t == "warning":
        print(_c("red", f"  ! {ev.get('error') or ev.get('text')}"), file=sys.stderr)
    elif t == "review":
        print(_c("dim", f"  review: {ev['verdict']} {ev.get('gaps') or ''}"), file=sys.stderr)


def cmd_npci(args: argparse.Namespace) -> int:
    """`ai-debugger npci ZM U30` or `ai-debugger npci invalid mpin`."""
    q = " ".join(args.query)  # nargs="+" gives a list of words; join them back into one string
    # Try three strategies in order; `or` moves to the next one when a result list is empty.
    res = npci.resolve(npci.extract_codes(q, loose=True)) or npci.resolve([q.upper()]) or npci.search(q)
    if args.json:
        print(json.dumps(res, indent=1, ensure_ascii=False))
    else:
        # `{q!r}` prints the value with quotes around it, e.g. 'XYZ'.
        print(npci.as_markdown(res, max_meanings=6) or f"no NPCI code matches {q!r}")
    return 0 if res else 1


def cmd_mcp_check(args: argparse.Namespace) -> int:
    """Health-check every MCP server (or one system's), print one line each."""
    names = [s.name for s in mcp_config.catalogue()
             if args.system in (None, s.system) or s.system == "shared"]
    # asyncio.run() is the bridge from normal code into async code: it runs one coroutine to the end.
    results = asyncio.run(mcp_probe.probe_many(names))
    bad = 0
    for r in results:
        if r.get("ok"):
            # Format specs: `:<36` = pad to 36 chars, left-aligned; `:>3` = 3 chars, right-aligned.
            print(f"{_c('lime', '●')} {r['name']:<36} {len(r['tools']):>3} tools  {r['ms']:>6}ms")
        else:
            bad += 1
            print(f"{_c('red', '●')} {r['name']:<36} {r.get('error', '')[:120]}")
        if r.get("missing_env"):
            print(_c("amber", f"    .env missing: {', '.join(r['missing_env'])}"))
    print(f"\n{len(results) - bad}/{len(results)} servers up · {sum(len(r.get('tools', [])) for r in results)} tools")
    return 1 if bad else 0


def cmd_tools(args: argparse.Namespace) -> int:
    """List the tools a run for `--system` would be given (native + loaded MCP tools)."""
    from .tools import load_belt

    belt = asyncio.run(load_belt())
    tools = belt.for_state({"system": args.system})
    for t in tools:
        print(f"{_c('lime', t.name):<48} {(t.description or '').splitlines()[0][:90]}")
    for name, err in belt.mcp_errors.items():
        print(_c("amber", f"  MCP {name} not loaded: {err[:120]}"))
    print(f"\n{len(tools)} tools for {args.system}")
    return 0


async def _eval_samples(args: argparse.Namespace) -> tuple[list[Any], list[dict[str, Any]]]:
    """Get the samples (live run of the golden cases, or saved threads) and score them."""
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    from . import evals
    from .graph import build_graph
    from .tools import load_belt

    samples = []
    if args.golden:
        graph = build_graph(await load_belt()).compile(checkpointer=InMemorySaver())
        for case in evals.load_golden(Path(args.golden)):
            print(_c("pink", f"▶ {case.id}: {case.question[:80]}"), file=sys.stderr)
            samples.append(await evals.run_case(graph, case))
    else:
        async with AsyncSqliteSaver.from_conn_string(str(get_settings().checkpoint_db)) as saver:
            graph = build_graph().compile(checkpointer=saver)
            for tid in args.threads.split(","):
                st = (await graph.aget_state({"configurable": {"thread_id": tid.strip()}})).values
                case = evals.GoldenCase(id=tid.strip(), question=st.get("question", ""), system=st.get("system"))
                samples.append(evals.sample_from_state(case, st))
    print(_c("dim", f"judging {len(samples)} answers with {evals.JUDGE_MODEL}…"), file=sys.stderr)
    return samples, await evals.evaluate_samples(samples)


def cmd_eval(args: argparse.Namespace) -> int:
    """Score the agent: code checks + Opus 5.5 judge (+ RAGAS). Exit 1 on a regression vs --baseline."""
    from . import evals

    if not args.golden and not args.threads:
        print("give --golden FILE or --threads ID,ID", file=sys.stderr)
        return 2
    samples, rows = asyncio.run(_eval_samples(args))
    if args.ragas:
        evals.add_ragas(rows, samples)  # outside asyncio: RAGAS runs its own event loop
    summary = evals.summarize(rows)
    path = evals.write_report(rows, summary)
    for k, v in summary.items():
        print(f"{k:<28} {v}")
    print(_c("dim", f"\nreport: {path} (and .md next to it)"), file=sys.stderr)
    if args.baseline:
        drops = evals.regressions(summary, json.loads(Path(args.baseline).read_text())["summary"])
        if drops:
            print(_c("red", "regressions:\n  " + "\n  ".join(drops)), file=sys.stderr)
            return 1
    return 0


def cmd_graph(_: argparse.Namespace) -> int:
    from .graph import build_graph

    print(build_graph().compile().get_graph().draw_mermaid())
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ai-debugger", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    # Pattern for each subcommand: create it, declare its options, then set_defaults(fn=...) says
    # which function handles it. At the bottom we just call args.fn(args).
    #   "--host"              optional option with a value (args.host, None if not given)
    #   type=int              convert the value to a number
    #   action="store_true"   a flag: True if present, False if not
    #   "question"            no dashes = required positional argument
    sp = sub.add_parser("serve", help="run the web UI")
    sp.add_argument("--host")
    sp.add_argument("--port", type=int)
    sp.add_argument("--reload", action="store_true")
    sp.set_defaults(fn=cmd_serve)

    sp = sub.add_parser("ask", help="run one investigation in the terminal")
    sp.add_argument("question")
    sp.add_argument("--system", choices=["tpap", "tsp"])
    sp.add_argument("--thread", help="continue an existing thread")
    sp.add_argument("--no-plan", action="store_true")
    sp.add_argument("--no-review", action="store_true")
    sp.add_argument("-v", "--verbose", action="store_true")
    # `lambda a: ...` is a tiny unnamed function; needed because _ask is async and needs asyncio.run.
    sp.set_defaults(fn=lambda a: asyncio.run(_ask(a)))

    sp = sub.add_parser("npci", help="look up NPCI error codes")
    sp.add_argument("query", nargs="+")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_npci)

    sp = sub.add_parser("mcp-check", help="start every MCP server and list its tools")
    sp.add_argument("--system", choices=["tpap", "tsp"])
    sp.set_defaults(fn=cmd_mcp_check)

    sp = sub.add_parser("tools", help="list the LangGraph tools a run would get")
    sp.add_argument("--system", choices=["tpap", "tsp"], default="tsp")
    sp.set_defaults(fn=cmd_tools)

    sp = sub.add_parser("eval", help="score the agent: code checks + Opus 5.5 as judge (+ RAGAS)")
    sp.add_argument("--golden", help="JSONL of golden cases: run the graph on each")
    sp.add_argument("--threads", help="comma-separated thread ids: score saved conversations instead")
    sp.add_argument("--ragas", action="store_true", help="add RAGAS Faithfulness / FactualCorrectness")
    sp.add_argument("--baseline", help="an earlier report .json; exit 1 if any average dropped >5%%")
    sp.set_defaults(fn=cmd_eval)

    sp = sub.add_parser("graph", help="print the LangGraph as mermaid")
    sp.set_defaults(fn=cmd_graph)

    args = p.parse_args(argv)  # argv=None means "read the real command line" (sys.argv)
    return int(args.fn(args) or 0)


# True only when this file is run directly (`python -m ai_debugger.cli`), not when imported.
if __name__ == "__main__":
    raise SystemExit(main())
