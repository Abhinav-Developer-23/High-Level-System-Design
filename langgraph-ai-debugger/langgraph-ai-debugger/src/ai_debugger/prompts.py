"""System prompts (skills) and the per-node user prompts.

Two kinds of prompt go into every LLM call:
  * the **system prompt** — the markdown files in `skills/` (operating rules, which index to
    search, SQL safety…), sent as a `SystemMessage` (`system_prompt`);
  * the **user prompt** — built here per node from the graph state (question, system,
    entities, NPCI table, plan, reviewer gaps), sent as a `HumanMessage`.

The tools themselves are not described here: `bind_tools` sends each tool's name, description
and argument schema with the request, so the model sees them directly.

To change how the agent behaves, edit `skills/*.md`; to change what each node is asked, edit
the `*_prompt` functions below.

Background for beginners
------------------------
A "prompt" is just a long string of text sent to the AI model. Everything in this file builds
strings. The tool used most is the **f-string**:

    name = "tsp"
    f"System: {name}"        → "System: tsp"       (anything in {} is evaluated and inserted)
    f\"\"\"line 1
    line 2 {name}\"\"\"        → a multi-line f-string (triple quotes allow line breaks)
    f"{{literal}}"           → "{literal}"         (doubled braces = a real brace, not a slot)

That last rule is why the JSON example in `review_prompt` is written with `{{ }}`.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from .config import SKILLS_DIR

# Skills the planner / reviewer need. The investigator gets every skill.
_PLAN_SKILLS = ("00-agent", "systems", "debugging", "db", "elasticsearch", "grafana", "metrics", "alerts",
                "paging-alerts", "percona")
_REVIEW_SKILLS = ("00-agent", "debugging", "db", "elasticsearch")


# @lru_cache is a decorator that remembers the return value: the first call reads the files,
# every later call returns the saved result instantly without touching the disk.
@lru_cache(maxsize=1)
def skill_files() -> dict[str, str]:
    """skills/<name>.md → text, read once per process (restart the server after editing).

    `p.stem` is the file name without folder and extension: skills/db.md → "db".
    """
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted(SKILLS_DIR.glob("*.md"))}


def skills_text(names: tuple[str, ...] | None = None) -> str:
    """Selected skills (all when `names` is None), each wrapped in a <skill> tag."""
    files = skill_files()
    # Looping over a dict gives its keys (the skill names).
    picked = [n for n in files if names is None or n in names]
    # "\n\n".join([...]) glues the pieces together with a blank line between each.
    # The `\"` inside the f-string is an escaped quote character.
    return "\n\n".join(f"<skill name=\"{n}\">\n{files[n].strip()}\n</skill>" for n in picked)


# The skills were written for Claude Code, where tools are called `mcp__<server>__<tool>`. This
# note maps those names to the LangGraph tool names, so the skills don't need rewriting.
_TOOL_NAMES_NOTE = """<tool-names>
In these skills an MCP tool is written `mcp__<server>__<tool>`. Here the same tool is named
`<server>_<tool>` (one underscore), e.g. `mcp__tsp_elk__search` → `tsp_elk_search`.
DB rows: the Redash MCP servers are replaced by native tools. Use `get_txn` for one txn (it runs
txn_info + txn_participants, on every TSP shard), `find_txn_by_rrn`, `txn_status_counts`,
`recent_failures`, `get_table_schema`, `explain_sql`, and `run_sql` for anything else.
Docs under resources/ and skills/: `read_resource`, `search_resources`. There is no shell.
If you cannot go on without information only the user has, call `AskUser`.
</tool-names>"""


@lru_cache(maxsize=4)
def system_prompt(role: str) -> str:
    """The system prompt for a node: its skills, each in a <skill> tag.

    Any role other than plan/review (i.e. "investigate") gets every skill plus the tool-name note.
    Cached per role: the skill files are read once per process.
    """
    names = {"plan": _PLAN_SKILLS, "review": _REVIEW_SKILLS}.get(role)  # None for "investigate"
    text = skills_text(names)
    return text if names else f"{text}\n\n{_TOOL_NAMES_NOTE}"


def _tools_block(tools: list[Any]) -> str:
    """One line per tool: name and the first sentence of its description."""
    return "\n".join(f"- `{t.name}`: {(t.description or '').split(chr(10))[0][:140]}" for t in tools) or "- (none)"


# The question is fenced in <<< >>> so the model can tell user text apart from our instructions.

def plan_prompt(state: dict[str, Any], tools: list[Any]) -> str:
    """Planner: list the tools it will have and ask for ≤ 8 concrete steps, no tool calls."""
    return f"""You are the PLANNER node. Do not call tools. Produce an investigation plan only.

System: **{state.get('system') or 'unknown'}**
Intent: {state.get('intent')}
Entities: {json.dumps(state.get('entities', {}), ensure_ascii=False)}

Tools the investigator will have:
{_tools_block(tools)}

{_npci_block(state)}

User question:
<<<
{state['question']}
>>>

Return a numbered plan of at most 8 steps. Each step: the tool(s) by the names above,
the exact query/arguments (index, SQL, PromQL, time window), and what the result decides.
Mark steps that can run in parallel with `[parallel]`. Keep it under 300 words."""


def investigate_prompt(state: dict[str, Any], follow_up: bool) -> str:
    """Investigator. Three variants, checked in this order:

    1. review sent us back → short prompt listing the gaps (the agent's messages are kept, so
       the model still sees the question and its earlier tool results);
    2. follow-up in the same thread → short prompt with just the new question (same reason);
    3. fresh question → full prompt with system, entities, NPCI table and the plan.
    """
    # `(x or {}).get(...)` — if there is no review yet, use an empty dict so .get() still works.
    gaps = (state.get("review") or {}).get("gaps") or []
    if gaps and state.get("findings"):
        # chr(10) is the newline character. It's used because a backslash ("\n") isn't allowed
        # inside the {} of an f-string on older Python versions.
        return f"""The REVIEWER found gaps in your previous answer. Close them with more tool calls,
then write the complete final answer again in the required format (all sections).

Gaps:
{chr(10).join(f'- {g}' for g in gaps)}"""
    if follow_up:
        return f"""Follow-up question from the user on the same investigation (system: {state.get('system')}).
Use the earlier context, run any further tool calls needed, and answer in the required format.

{_npci_block(state)}

<<<
{state['question']}
>>>"""
    plan = state.get("plan") or "(no plan — work it out yourself)"
    return f"""You are the INVESTIGATOR node. Investigate with tools and answer.

System: **{state.get('system')}**. Your tools are already scoped to this system.

Detected entities: {json.dumps(state.get('entities', {}), ensure_ascii=False)}
Current time (IST): {state.get('now_ist')}

{_npci_block(state)}

Plan from the planner (adapt freely if evidence points elsewhere):
{plan}

User question:
<<<
{state['question']}
>>>

Answer in the required Markdown format (Finding, Evidence, Timeline, NPCI codes, Queries used, Next steps, Proof).
The Proof section is mandatory: every claim with the tool and the exact value it returned; for a txn,
the txn_info data from get_txn. Anything you could not fetch is "not verified", never a guess."""


def review_prompt(state: dict[str, Any]) -> str:
    """Reviewer: grade the answer against the debugging rules and reply with JSON only
    (parsed by `graph.parse_review`)."""
    return f"""You are the REVIEWER node. Do not call tools. Judge the investigator's answer.

User question:
<<<
{state['question']}
>>>

System: {state.get('system')}. Entities: {json.dumps(state.get('entities', {}), ensure_ascii=False)}

Investigator's answer:
<<<
{state.get('findings', '')}
>>>

Check: does the Finding answer the question with evidence (not a guess)? For a txn: were BOTH DB
(txn + participants) and logs checked, and is the `Total time:` line present? Are NPCI codes
translated? Are queries listed? Did it stay inside one system and stay read-only?

Reply with ONLY a JSON object, no prose, no code fence:
{{"verdict": "pass" | "gaps", "score": 0-10, "gaps": ["specific missing check", ...], "summary": "one line"}}
Use "gaps" only for missing evidence that more tool calls could realistically get."""


def _npci_block(state: dict[str, Any]) -> str:
    """The NPCI table built by the npci / npci_enrich nodes, or "" when no codes were seen."""
    table = state.get("npci_md")
    # Conditional expression: `A if condition else B`.
    return f"NPCI code table (from the code map):\n{table}" if table else ""
