"""Settings. App knobs come from the environment, falling back to `.env`.

Only the knobs below are read from `.env`. The other credentials in it (Grafana, Jira…) are
never loaded into this process's environment: each MCP server gets only its own values
(see `mcp_config.rendered_spec`). `ANTHROPIC_API_KEY` is read here and handed straight to the
chat model (`llm.py`); it is kept out of `repr()` so it never lands in a log line.

Background for beginners
------------------------
* A **`.env` file** is a plain text file of `NAME=value` lines (copy `.env.example` to start).
  It holds settings and secrets that must not go into git.
* **Environment variables** are name=value pairs every running program gets from whoever
  started it (your shell). In Python they are in the dict-like `os.environ`.
  `AGENT_MODEL=x uv run ai-debugger serve` sets one just for that command.
* A **knob** here = one setting you can turn without editing code.
* Values in .env and the environment are always text, so numbers go through `int("1800")`
  and yes/no switches through `_bool("true")`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values

# Project layout. ROOT = the repo root (src/ai_debugger/config.py → up two levels).
# Path(__file__) = this file; .resolve() = full absolute path; .parents[0] is src/ai_debugger,
# .parents[1] is src, .parents[2] is the project folder. `ROOT / ".env"` joins paths.
# ALL_CAPS names are a Python convention for constants: set once, never changed.
ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
# Runtime data: checkpoints.sqlite, threads.sqlite, logs/.
# AI_DEBUGGER_VAR points it elsewhere (e.g. a temp dir for a throwaway run).
VAR_DIR = Path(os.environ.get("AI_DEBUGGER_VAR") or ROOT / "var")
SKILLS_DIR = ROOT / "skills"                         # system-prompt markdown (see prompts.py)
RESOURCES_DIR = ROOT / "resources"                   # schemas, flows, docs the file tools may read
MCP_TEMPLATE = ROOT / "config" / "mcp_servers.json"  # MCP server template (see mcp_config.py)

def env_file_values() -> dict[str, str]:
    """Parse .env into a dict WITHOUT touching os.environ (unlike load_dotenv)."""
    if not ENV_FILE.exists():
        return {}
    # Keep only keys that have a value (a bare `NAME` line with no `=` gives None).
    return {k: v for k, v in dotenv_values(ENV_FILE).items() if v is not None}


def _knob(name: str, default: str, file_vals: dict[str, str]) -> str:
    """Precedence: real environment variable > .env > default.

    `a or b or c` returns the first one that isn't empty/None — a compact "try in order".
    """
    return os.environ.get(name) or file_vals.get(name) or default


def _bool(v: str) -> bool:
    """Text to True/False: ' True ' gives True, '0' gives False. strip() drops spaces, lower() lowercases."""
    return v.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """App knobs. Each field maps to one variable in `.env.example` (see `get_settings`).

    Each line is `name: type = default`. Use it as `get_settings().model`.
    """
    # repr=False: printing the Settings object (logs, debugger) never shows the key.
    anthropic_api_key: str = field(default="", repr=False)
    model: str = "claude-opus-5-5"
    max_tokens: int = 8192              # longest reply one LLM call may write
    llm_timeout_s: int = 300            # one HTTP call to the Anthropic API
    max_tool_calls: int = 30            # tool budget per turn; then the agent must answer
    tool_output_chars: int = 12000      # tool results are cut to this before the LLM sees them
    recursion_limit: int = 150          # LangGraph super-steps per turn (each tool round = 2)
    price_in_per_mtok: float = 0.0      # USD per million input tokens, for the cost display
    price_out_per_mtok: float = 0.0     # USD per million output tokens
    price_cache_read_per_mtok: float = 0.0  # USD per million tokens read from the prompt cache
    prompt_cache: bool = True           # mark the stable prefix + conversation for Anthropic's prompt cache
    cache_ttl: str = "5m"               # "5m" (write costs 1.25x input) or "1h" (write costs 2x)
    compact_trigger_tokens: int = 120_000  # high watermark: summarize old turns once a prompt is this big
    compact_keep_turns: int = 2         # low watermark: the last N turns stay word for word
    summary_model: str = "claude-haiku-5-5"  # cheaper model that writes the compaction summary
    max_review_loops: int = 1
    plan_enabled: bool = True
    review_enabled: bool = True
    host: str = "127.0.0.1"
    port: int = 8077
    daily_questions_per_user: int = 100  # questions per user per day (IST); 0 = no limit
    monthly_budget_usd_per_user: float = 500.0  # $ per user per calendar month; 0 = no cap (needs AGENT_PRICE_*)
    user_header: str = "X-Forwarded-User"  # header in which the login layer passes the user's name
    mcp_enabled: bool = True            # load MCP servers as LangGraph tools at startup
    mcp_load_timeout_s: int = 60        # per server, at startup
    disabled_servers: tuple[str, ...] = field(default_factory=tuple)
    allow_notion_writes: bool = False

    # @property makes a method look like a field: write `s.checkpoint_db`, not `s.checkpoint_db()`.
    @property
    def checkpoint_db(self) -> Path:
        return VAR_DIR / "checkpoints.sqlite"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Built once and cached; call `get_settings.cache_clear()` after changing env vars in-process."""
    fv = env_file_values()
    # Keyword arguments (name=value) fill the Settings fields by name.
    # disabled_servers: "a, b," → split on commas → strip spaces → drop empties → ("a", "b").
    return Settings(
        anthropic_api_key=_knob("ANTHROPIC_API_KEY", "", fv),
        model=_knob("AGENT_MODEL", "claude-opus-5-5", fv),
        max_tokens=int(_knob("AGENT_MAX_TOKENS", "8192", fv)),
        llm_timeout_s=int(_knob("AGENT_LLM_TIMEOUT_S", "300", fv)),
        max_tool_calls=int(_knob("AGENT_MAX_TOOL_CALLS", "30", fv)),
        tool_output_chars=int(_knob("AGENT_TOOL_OUTPUT_CHARS", "12000", fv)),
        recursion_limit=int(_knob("AGENT_RECURSION_LIMIT", "150", fv)),
        price_in_per_mtok=float(_knob("AGENT_PRICE_IN_PER_MTOK", "0", fv)),
        price_out_per_mtok=float(_knob("AGENT_PRICE_OUT_PER_MTOK", "0", fv)),
        price_cache_read_per_mtok=float(_knob("AGENT_PRICE_CACHE_READ_PER_MTOK", "0", fv)),
        prompt_cache=_bool(_knob("AGENT_PROMPT_CACHE", "1", fv)),
        cache_ttl=_knob("AGENT_CACHE_TTL", "5m", fv),
        compact_trigger_tokens=int(_knob("AGENT_COMPACT_TRIGGER_TOKENS", "120000", fv)),
        compact_keep_turns=int(_knob("AGENT_COMPACT_KEEP_TURNS", "2", fv)),
        summary_model=_knob("AGENT_SUMMARY_MODEL", "claude-haiku-5-5", fv),
        max_review_loops=int(_knob("AGENT_MAX_REVIEW_LOOPS", "1", fv)),
        plan_enabled=_bool(_knob("AGENT_PLAN", "1", fv)),
        review_enabled=_bool(_knob("AGENT_REVIEW", "1", fv)),
        host=_knob("APP_HOST", "127.0.0.1", fv),
        daily_questions_per_user=int(_knob("AGENT_DAILY_QUESTIONS_PER_USER", "100", fv)),
        monthly_budget_usd_per_user=float(_knob("AGENT_MONTHLY_BUDGET_USD_PER_USER", "500", fv)),
        user_header=_knob("AUTH_USER_HEADER", "X-Forwarded-User", fv),
        port=int(_knob("APP_PORT", "8077", fv)),
        mcp_enabled=_bool(_knob("MCP_LOAD", "1", fv)),
        mcp_load_timeout_s=int(_knob("MCP_LOAD_TIMEOUT_S", "60", fv)),
        disabled_servers=tuple(s.strip() for s in _knob("MCP_DISABLED", "", fv).split(",") if s.strip()),
        allow_notion_writes=_bool(_knob("ALLOW_NOTION_WRITES", "0", fv)),
    )
