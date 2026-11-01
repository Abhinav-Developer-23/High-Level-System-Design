"""Native LangGraph DB tools: rows from txn_info / txn_participants through Redash.

Each tool here is built a different way on purpose, so this file doubles as a reference:

| Tool                    | Built with                                   | Why that way                                  |
|-------------------------|----------------------------------------------|-----------------------------------------------|
| `get_table_schema`      | `@tool(parse_docstring=True)`                | simplest: function + docstring = tool          |
| `explain_sql`           | `@tool` on an `async def`                    | async I/O inside a tool                        |
| `run_sql`               | subclass of `BaseTool` (`RunSqlTool`)        | full control, Pydantic limits, state on object |
| `txn_status_counts` …   | `StructuredTool.from_function` in a loop     | several tools generated from one table of data |
| `get_txn`               | `@tool` returning `Command`                  | writes rows into the graph state, not just text|

Every tool that touches a database reads the system (tpap / tsp) with
`Annotated[str, InjectedState("system")]`. `ToolNode` fills that argument from the graph state
and it is left out of the schema the model sees, so the model can't query the wrong estate.

`client_for` can be swapped for a fake for an offline run (no network).
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolCallId, StructuredTool, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from pydantic import BaseModel, Field

from ..config import RESOURCES_DIR
from .redash import DEFAULT_TIMEOUT_SEC, RedashClient


def client_for(system: str) -> RedashClient:
    """The Redash client for a system. A module-level function so it can be swapped for a fake."""
    return RedashClient.for_system(system)


def _dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)


# --------------------------------------------------------------------------------------------
# 1. @tool(parse_docstring=True): function name → tool name, docstring → description,
#    `Args:` section → one description per argument.
# --------------------------------------------------------------------------------------------

@tool(parse_docstring=True)
def get_table_schema(system: Annotated[str, InjectedState("system")], table: str = "") -> str:
    """Columns, types and indexes of a table, from the schema docs. Free and instant: use it before writing SQL.

    Args:
        system: Filled in by the graph (tpap or tsp); never set by the model.
        table: Table name such as "txn_info" or "switchv2.txn_participants". Empty lists every table.
    """
    path = RESOURCES_DIR / "db_schema" / f"{system}_schema.md"
    if not path.exists():
        return f"No schema doc for system {system!r}."
    lines = path.read_text(encoding="utf-8").splitlines()
    headings = [(i, ln[4:].strip()) for i, ln in enumerate(lines) if ln.startswith("### ")]
    if not table:
        return "Tables:\n" + "\n".join(f"- {name}" for _, name in headings)
    want = table.lower().split(".")[-1]
    for i, name in headings:
        if name.lower().split(".")[-1] == want:
            # The section runs until the next table heading (or the next database heading).
            end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith(("### ", "## "))), len(lines))
            return "\n".join(lines[i:end]).strip()
    return f"No table {table!r}. Known tables: {', '.join(name for _, name in headings)}"


# --------------------------------------------------------------------------------------------
# 2. @tool on an async function: LangGraph awaits it, so slow I/O doesn't block other tools.
# --------------------------------------------------------------------------------------------

@tool(parse_docstring=True)
async def explain_sql(sql: str, system: Annotated[str, InjectedState("system")], db_name: str = "") -> str:
    """Show MySQL's plan for a SELECT without running it, and flag full table scans. Use before any non-trivial query.

    Args:
        sql: The SELECT to check, without the EXPLAIN keyword.
        system: Filled in by the graph (tpap or tsp); never set by the model.
        db_name: Database or shard; empty means the default (first shard on TSP).
    """
    client = client_for(system)
    db = client.resolve(db_name or None)[0]
    res = await client.run(f"EXPLAIN {sql.strip().rstrip(';')}", db, max_rows=50)
    rows = res.get("rows", [])
    scans = [r.get("table") for r in rows if r.get("type") == "ALL" or not r.get("key")]
    verdict = (f"FULL SCAN on {', '.join(map(str, scans))}: add a WHERE on an indexed column "
               "(txn_id, rrn, created_on) before running this." if scans else "Uses an index; OK to run.")
    return _dumps({"verdict": verdict, "plan": rows, "db": db})


# --------------------------------------------------------------------------------------------
# 3. Subclass BaseTool: the most control. The Pydantic `args_schema` validates arguments
#    *before* our code runs (max_rows=5000 is rejected by `le=500`), and the tool object can
#    hold its own settings (`default_timeout_sec`, `client_factory`).
# --------------------------------------------------------------------------------------------

class RunSqlArgs(BaseModel):
    sql: str = Field(description="One read-only statement: SELECT / SHOW / EXPLAIN / DESCRIBE / WITH. "
                                 "Always filter on txn_id, rrn or a tight created_on range.")
    db_name: str = Field("", description="tpap: switchv2 | upi_config. tsp: switchv2_C1 | switchv2_C2 | "
                                         "switchv2_C3 | switchv2_C6 | Config_UPI_Jobs. Empty = default "
                                         "(tpap: switchv2; tsp: every shard, one after another).")
    max_rows: int = Field(100, ge=1, le=500, description="Rows to return (a LIMIT is added if missing).")
    timeout_sec: int = Field(DEFAULT_TIMEOUT_SEC, ge=1, le=120,
                             description="Leave at 20. Not found in 20s means rewrite the query, not wait longer.")
    # Injected by ToolNode from the graph state; not part of the schema the model sees.
    system: Annotated[str, InjectedState("system")]


class RunSqlTool(BaseTool):
    """Generic read-only SQL on the txn databases. The guard rails are in `redash.check_read_only`."""

    name: str = "run_sql"
    description: str = (
        "Run read-only SQL on the transaction DB through Redash (20s timeout). Prefer get_txn / "
        "find_txn_by_rrn / txn_status_counts when they fit. txn_info and txn_participants keep ~7 days.")
    args_schema: type[BaseModel] = RunSqlArgs
    # State on the tool object: a different client factory can be passed in here.
    client_factory: Callable[[str], RedashClient] | None = None

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("run_sql is async-only; the graph calls it with ainvoke")

    async def _arun(self, sql: str, system: str, db_name: str = "", max_rows: int = 100,
                    timeout_sec: int = DEFAULT_TIMEOUT_SEC) -> str:
        client = (self.client_factory or client_for)(system)
        results = [await client.run(sql, db, max_rows=max_rows, timeout_sec=timeout_sec)
                   for db in client.resolve(db_name or None)]
        return _dumps(results[0] if len(results) == 1 else results)


# --------------------------------------------------------------------------------------------
# 4. StructuredTool.from_function in a loop: one table of "canned" debug queries becomes
#    several tools. The SQL is fixed; the model only fills validated parameters (ints and
#    regex-checked codes), so it can't inject SQL through them.
# --------------------------------------------------------------------------------------------

class _WindowArgs(BaseModel):
    minutes: int = Field(60, ge=1, le=1440, description="Look back this many minutes.")
    system: Annotated[str, InjectedState("system")]


class _FailureArgs(_WindowArgs):
    npci_resp_code: str = Field("", pattern=r"^[A-Z0-9]{0,6}$", description="Only this NPCI code, e.g. U30.")
    limit: int = Field(50, ge=1, le=200)


class _RrnArgs(BaseModel):
    rrn: str = Field(pattern=r"^\d{12}$", description="12-digit RRN from NPCI.")
    system: Annotated[str, InjectedState("system")]


@dataclass(frozen=True)
class CannedQuery:
    name: str
    description: str
    args: type[BaseModel]
    sql: Callable[[Any], str]  # validated args → SQL text


CANNED_QUERIES = [
    CannedQuery(
        "txn_status_counts",
        "Count transactions by status and NPCI response code over the last N minutes. Use for spikes, "
        "success rate and 'how many failed' questions.",
        _WindowArgs,
        lambda a: ("SELECT status, npci_resp_code, COUNT(*) AS cnt FROM txn_info "
                   f"WHERE created_on >= NOW() - INTERVAL {a.minutes} MINUTE "
                   "GROUP BY status, npci_resp_code ORDER BY cnt DESC LIMIT 100")),
    CannedQuery(
        "recent_failures",
        "Latest failed transactions in the last N minutes, optionally for one NPCI response code.",
        _FailureArgs,
        lambda a: ("SELECT txn_id, status, npci_resp_code, amount, created_on FROM txn_info "
                   f"WHERE status = 'FAILURE' AND created_on >= NOW() - INTERVAL {a.minutes} MINUTE"
                   + (f" AND npci_resp_code = '{a.npci_resp_code}'" if a.npci_resp_code else "")
                   + f" ORDER BY created_on DESC LIMIT {a.limit}")),
    CannedQuery(
        "find_txn_by_rrn",
        "Find the txn_id(s) for an RRN. Then call get_txn with the txn_id.",
        _RrnArgs,
        lambda a: f"SELECT txn_id, status, npci_resp_code, amount, created_on FROM txn_info WHERE rrn = '{a.rrn}' LIMIT 10"),
]


def _canned_tool(q: CannedQuery) -> StructuredTool:
    async def run(**kwargs: Any) -> str:
        # StructuredTool passes only the arguments the model actually sent (plus the injected
        # `system`), so validate again here to get the defaults filled in.
        args = q.args.model_validate(kwargs)
        client = client_for(args.system)
        results = [await client.run(q.sql(args), db, max_rows=200) for db in client.resolve(None)]
        return _dumps(results[0] if len(results) == 1 else results)

    return StructuredTool.from_function(coroutine=run, name=q.name, description=q.description,
                                        args_schema=q.args)


# --------------------------------------------------------------------------------------------
# 5. A tool that returns Command: besides answering the model (the ToolMessage), it writes a
#    summary of the txn into the graph state (`txn_rows`), which the report node turns into a
#    table later. A plain tool can only return text to the model.
# --------------------------------------------------------------------------------------------

_TXN_ID = re.compile(r"^[A-Za-z0-9]{10,64}$")


@tool
async def get_txn(txn_id: str, system: Annotated[str, InjectedState("system")],
                  tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Fetch one UPI transaction by txn_id: its txn_info row and all txn_participants rows.

    On TSP every shard is checked until the txn is found. Rows are kept ~7 days; no rows for an
    older txn means it was purged, not that it never existed.
    """
    if not _TXN_ID.match(txn_id):
        raise ValueError("txn_id must be 10–64 letters and digits.")
    client = client_for(system)
    found: dict[str, Any] | None = None
    for db in client.resolve(None):
        info = await client.run(f"SELECT * FROM txn_info WHERE txn_id = '{txn_id}'", db, max_rows=5)
        if info.get("row_count"):
            parts = await client.run(f"SELECT * FROM txn_participants WHERE txn_id = '{txn_id}'", db, max_rows=50)
            found = {"db": db, "txn_info": info["rows"], "txn_participants": parts.get("rows", [])}
            break
    if found is None:
        content = (f"No txn_info row for {txn_id} on {system}. If the txn is older than ~7 days it was purged: "
                   "search the logs instead.")
        summary = {"found": False}
    else:
        row = found["txn_info"][0]
        content = _dumps(found)
        summary = {"found": True, "db": found["db"], "status": row.get("status"),
                   "npci_resp_code": row.get("npci_resp_code"), "amount": row.get("amount"),
                   "created_on": row.get("created_on"), "participants": len(found["txn_participants"])}
    return Command(update={
        "txn_rows": {txn_id: summary},                                   # → graph state
        "agent_messages": [ToolMessage(content, tool_call_id=tool_call_id, name="get_txn")],  # → the model
    })


DB_TOOLS: list[BaseTool] = [get_table_schema, explain_sql, RunSqlTool(), get_txn,
                            *(_canned_tool(q) for q in CANNED_QUERIES)]
