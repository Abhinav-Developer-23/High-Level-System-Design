# LangGraph AI Debugger

A production debugger for the TPAP and TSP UPI systems. You ask a question ("tsp: why is txn
PTM… DEEMED?"). A LangGraph pipeline decides what kind of question it is, then an agent node
(Claude through the Anthropic API, via LangChain's `ChatAnthropic`) investigates with **LangGraph
tools**: native DB tools on Redash plus the read-only MCP servers for logs, metrics, alerts and code.
You use it from a web UI or the terminal.

## Where to start reading

**New to Python or LangGraph?** Start with the long comment at the top of `src/ai_debugger/graph.py`. It explains LangGraph in plain words (state, nodes, edges, tools, checkpoints) and the Python syntax you'll keep seeing. Every other file opens with a "Background for beginners" section. `static/app.js` opens with a short JavaScript crash course.

Read the code in this order:

| # | File | What you learn |
|---|---|---|
| 1 | `src/ai_debugger/graph.py` | **Start here.** The pipeline diagram is at the top. `DebugState` is the data, the `async def` functions are the nodes, `route_after_*` choose the next node, `agent` ⇄ `tools` is the tool loop, and `build_graph()` at the bottom wires it all together. |
| 2 | `src/ai_debugger/tools/db.py` | The DB tools, each built a different way: `@tool`, async `@tool`, a `BaseTool` subclass, `StructuredTool.from_function` in a loop, and a tool that returns `Command`. `InjectedState` gives them the system (tpap/tsp). |
| 3 | `src/ai_debugger/tools/__init__.py` | The `ToolBelt`: every tool, and which ones a TPAP or TSP run may use. Then `tools/mcp.py` (MCP servers → tools), `tools/files.py`, `tools/control.py` (`AskUser`). |
| 4 | `src/ai_debugger/llm.py` | `ChatAnthropic`: how one LLM call is made and streamed, and the token/cost record. |
| 5 | `src/ai_debugger/prompts.py` | What each LLM node is asked, and how `skills/*.md` become the system prompt. |
| 6 | `src/ai_debugger/server.py` | The web API. `POST /api/chat` runs the graph in the background and streams its events to the browser as Server-Sent Events. |
| 7 | `src/ai_debugger/static/app.js` | The browser side. Start at `boot()` (bottom), then `send()` and `handle(ev)`. |

The rest is small and self-contained:

- `config.py`: settings from env / `.env`, and the project paths.
- `tools/redash.py`: the async Redash client and the SQL guard rails (read-only, one statement, auto `LIMIT`, 20 s timeout).
- `mcp_config.py`: the MCP server catalogue, which system each server belongs to, secrets filled from `.env`.
- `npci.py`: NPCI error-code lookup (ZM, U30…). Plain dictionary, no LLM.
- `store.py`: the sidebar's thread list. The conversation itself lives in LangGraph's checkpoint DB.
- `mcp_probe.py`: health check that starts an MCP server and lists its tools.
- `evals.py`: scoring the agent: code checks, Claude Opus 5.5 as LLM-as-a-judge, optional RAGAS metrics.
- `cli.py`: the `ai-debugger` command (`serve`, `ask`, `tools`, `eval`, `npci`, `mcp-check`, `graph`).

## What happens when you ask a question

```
question
   │
   ▼
triage        regex only: system (tpap/tsp), intent, txn ids / RRNs / incidents / NPCI codes
   │  system unknown? ──▶ clarify: ask "tpap or tsp?", stop, resume on the reply
   ▼
npci          translate NPCI codes found in the question
   │  pure "what is ZM?" ──▶ report
   ▼
plan          LLM, no tools: a numbered investigation plan             (skipped on follow-ups)
   ▼
investigate   adds the task as a message to the agent's conversation
   │  last prompt ≥ AGENT_COMPACT_TRIGGER_TOKENS? ──▶ compact: a cheaper model summarizes old turns
   ▼
agent ⇄ tools the tool loop: the LLM asks for tools, ToolNode runs them, results go back
   │  model called AskUser? ──▶ ask_user: show its question, stop, continue on the reply
   ▼
npci_enrich   translate NPCI codes the agent found in logs / DB
   ▼
review        LLM, no tools: grade the answer, JSON verdict
   │  gaps and loop budget left? ──▶ back to investigate (same conversation, told the gaps)
   ▼
report        findings + txn table + NPCI table + reviewer verdict → the markdown you see
```

Only `plan`, `agent` and `review` call the model; the rest is plain Python. Set `AGENT_PLAN=0`
or `AGENT_REVIEW=0` in `.env` to skip those steps. The agent gets at most `AGENT_MAX_TOOL_CALLS`
tool calls per turn; after that it must answer.

State is saved after every node in `var/checkpoints.sqlite`, keyed by thread id. Because the tool
loop runs inside the graph, every tool round is its own checkpoint: a follow-up question continues
the same conversation (earlier tool results included), and after a crash the run continues from
the last finished tool call instead of starting over.

Long threads stay affordable two ways. **Prompt caching**: the tools, the skills and the
conversation so far are marked with `cache_control`, so Anthropic re-reads them at a fraction of
the input price (`llm.system_message`, `llm.with_cache`; each run records `cache_read_tokens`).
**Compaction**: once a prompt passes `AGENT_COMPACT_TRIGGER_TOKENS` (120k), the `compact` node
summarizes everything but the last `AGENT_COMPACT_KEEP_TURNS` turns with `AGENT_SUMMARY_MODEL`.

## The tools

| Tool | Where | What it does |
|---|---|---|
| `get_txn` | `tools/db.py` | txn_info + txn_participants for one txn (every TSP shard); writes a summary into the state |
| `find_txn_by_rrn`, `txn_status_counts`, `recent_failures` | `tools/db.py` | Canned queries with validated parameters |
| `run_sql`, `explain_sql`, `get_table_schema` | `tools/db.py` | Generic read-only SQL, query plans, schema docs |
| `read_resource`, `search_resources` | `tools/files.py` | Read / search `resources/` and `skills/` |
| `<server>_<tool>` | `tools/mcp.py` | Every tool of the MCP servers in `config/mcp_servers.json` (except Redash) |
| `AskUser` | `tools/control.py` | Schema-only: the model asks the user a question |

`uv run ai-debugger tools --system tsp` lists what a TSP run gets.

## The other folders

| Folder | What it is |
|---|---|
| `skills/` | Markdown rules given to the model as its system prompt (`00-agent.md` first). Edit these to change how the agent investigates. |
| `config/mcp_servers.json` | Template of every MCP server: launch command, `${ENV}` placeholders, and our `_meta` (system, label, blocked tools). |
| `mcp_servers/` | The read-only MCP servers, copied from Agent-debugger. |
| `resources/` | DB schemas, flow docs and Grafana dashboard JSON that the file tools can read. |
| `evals/` | `golden.jsonl`: questions with reference answers, required facts and expected tools, for `ai-debugger eval`. |
| `scripts/` | `mcp-stdio.sh` (runs an MCP server with stderr sent to `var/logs/mcp/`), `build_npci_map.py` (regenerates the NPCI JSON). |
| `var/` | Runtime data (gitignored): checkpoint DB, thread index, logs. |

## Running it

```bash
uv sync
cp .env.example .env        # then fill in ANTHROPIC_API_KEY, the Redash keys and the rest (chmod 600)
uv run ai-debugger serve    # UI on http://127.0.0.1:8077
uv run ai-debugger ask "tsp: is the C3 switch master MySQL healthy right now?"
uv run ai-debugger tools --system tsp
uv run ai-debugger eval --golden evals/golden.jsonl          # add --ragas after `uv sync --extra eval`
uv run ai-debugger npci ZM U30
uv run ai-debugger mcp-check --system tsp
```

Each user gets `AGENT_DAILY_QUESTIONS_PER_USER` questions per day (default 100, resets at midnight IST)
and at most `AGENT_MONTHLY_BUDGET_USD_PER_USER` dollars per calendar month (default $500; needs the
`AGENT_PRICE_*` settings, which `.env.example` sets for Claude Sonnet 5);
the app sits behind the company login, which passes the user's name in `AUTH_USER_HEADER`.
All settings are listed in `.env.example`. `MCP_LOAD=0` starts with only the native tools (no MCP
servers), which is handy when you only need the DB.
