"""Thread index for the sidebar, and per-user daily usage. The conversation itself lives in the
LangGraph checkpointer.

Two SQLite files under `var/`, easy to confuse:
  * `checkpoints.sqlite` — owned by LangGraph (`AsyncSqliteSaver`): the full `DebugState` after
    every node of every thread. This is the source of truth for messages, findings, etc.
  * `threads.sqlite`     — this module: one small row per thread (title, status, total cost)
    so the sidebar can list threads without loading every checkpoint.

`status` goes idle → running → done | needs_input | error | cancelled (| interrupted).

The `usage` table holds one row per (user, day): questions asked and money spent. `take_question`
enforces the daily limit (AGENT_DAILY_QUESTIONS_PER_USER) with a single SQL statement, so two
requests arriving at the same moment can't both slip past the last free slot.

Background for beginners
------------------------
* **SQLite** is a database stored in a single file — no server to install. You talk to it with
  SQL (`SELECT`, `INSERT`, `UPDATE`, `DELETE`).
* **aiosqlite** is the async version of Python's sqlite3, so database calls are `await`ed and
  don't freeze the web server while they run.
* `?` in SQL is a placeholder. The values go separately as a tuple: `("...WHERE id=?", (tid,))`.
  The database inserts them safely, so text like `'; DROP TABLE` can't break the query
  (that attack is called SQL injection). `(tid,)` with the trailing comma is a 1-item tuple.
* After changing data you must `commit()`, otherwise the change is not saved.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import aiosqlite

# The table layout. "IF NOT EXISTS" makes it safe to run on every start.
# TEXT = string, REAL = decimal number, INTEGER = whole number; times are Unix seconds (time.time()).
_SCHEMA = """
CREATE TABLE IF NOT EXISTS threads (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  system TEXT,
  intent TEXT,
  status TEXT NOT NULL DEFAULT 'idle',
  cost_usd REAL NOT NULL DEFAULT 0,
  turns INTEGER NOT NULL DEFAULT 0,
  created REAL NOT NULL,
  updated REAL NOT NULL
)
"""

_USAGE_SCHEMA = """
CREATE TABLE IF NOT EXISTS usage (
  user TEXT NOT NULL,
  day TEXT NOT NULL,              -- YYYY-MM-DD in IST
  questions INTEGER NOT NULL DEFAULT 0,
  cost_usd REAL NOT NULL DEFAULT 0,
  PRIMARY KEY (user, day)
)
"""

_COLS = ("id", "title", "system", "intent", "status", "cost_usd", "turns", "created", "updated")


class ThreadStore:
    """Usage (see server.py lifespan): store = ThreadStore(path); await store.open(); ...; await store.close()."""

    # __init__ runs when you write ThreadStore(path). `self` is the new object being set up.
    # A leading underscore (`_db`) is a convention meaning "internal, don't touch from outside".
    def __init__(self, path: Path) -> None:
        self.path = path
        self._db: aiosqlite.Connection | None = None  # no connection until open() is called

    async def open(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(self.path)
        await self._db.execute(_SCHEMA)
        await self._db.execute(_USAGE_SCHEMA)
        # a server restart leaves no run alive
        await self._db.execute("UPDATE threads SET status='interrupted' WHERE status='running'")
        await self._db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    # `self.db` (no brackets) returns the open connection, or crashes with a clear message if
    # someone forgot to call open() first.
    @property
    def db(self) -> aiosqlite.Connection:
        assert self._db is not None, "store not opened"
        return self._db

    async def upsert(self, tid: str, title: str) -> None:
        """Create the row on a thread's first message; later messages only bump `updated`."""
        now = time.time()
        # "Upsert" = insert, or update if the row already exists (ON CONFLICT on the primary key).
        # `excluded.updated` = the value we tried to insert. title[:140] = first 140 characters.
        await self.db.execute(
            "INSERT INTO threads(id,title,created,updated) VALUES(?,?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET updated=excluded.updated", (tid, title[:140], now, now))
        await self.db.commit()

    async def update(self, tid: str, **fields: Any) -> None:
        """Set some columns. Unknown keys are dropped, which is what makes the f-string SQL safe.

        `**fields` collects keyword arguments into a dict:
            update(tid, status="done", system="tsp")  →  fields = {"status": "done", "system": "tsp"}
        which becomes:  UPDATE threads SET status=?,system=?,updated=? WHERE id=?
        Column names can't be `?` placeholders, so they go into the f-string — only names from
        _COLS are allowed through. `(*fields.values(), tid)` unpacks the values into a tuple.
        """
        fields = {k: v for k, v in fields.items() if k in _COLS and k != "id"}
        if not fields:
            return
        fields["updated"] = time.time()
        sets = ",".join(f"{k}=?" for k in fields)
        await self.db.execute(f"UPDATE threads SET {sets} WHERE id=?", (*fields.values(), tid))
        await self.db.commit()

    async def add_cost(self, tid: str, cost: float) -> None:
        """Called once per finished turn: add its cost and count the turn."""
        await self.db.execute("UPDATE threads SET cost_usd=cost_usd+?, turns=turns+1, updated=? WHERE id=?",
                              (cost, time.time(), tid))
        await self.db.commit()

    async def list(self, limit: int = 100) -> list[dict[str, Any]]:
        """Newest threads first, each as a dict.

        A row comes back as a tuple ("abc", "title", ...). zip(_COLS, row) pairs each column name
        with its value, and dict(...) turns those pairs into {"id": "abc", "title": "title", ...}.
        """
        cur = await self.db.execute(f"SELECT {','.join(_COLS)} FROM threads ORDER BY updated DESC LIMIT ?", (limit,))
        return [dict(zip(_COLS, row, strict=True)) for row in await cur.fetchall()]

    async def get(self, tid: str) -> dict[str, Any] | None:
        """One thread's row as a dict, or None if there is no such thread."""
        cur = await self.db.execute(f"SELECT {','.join(_COLS)} FROM threads WHERE id=?", (tid,))
        row = await cur.fetchone()
        return dict(zip(_COLS, row, strict=True)) if row else None

    async def take_question(self, user: str, day: str, limit: int) -> tuple[bool, int]:
        """Count one question for `user` today, unless they already hit `limit`.

        Returns (allowed, questions used today). "Upsert" with a condition: insert the first
        question of the day, or add one *only while* questions < limit. If the WHERE fails, no row
        changes (rowcount 0) and the question is refused. limit 0 = unlimited.
        """
        cur = await self.db.execute(
            "INSERT INTO usage(user, day, questions) VALUES(?, ?, 1) "
            "ON CONFLICT(user, day) DO UPDATE SET questions = questions + 1 "
            "WHERE ? = 0 OR questions < ?", (user, day, limit, limit))
        await self.db.commit()
        allowed = cur.rowcount > 0
        return allowed, (await self.usage(user, day))["questions"]

    async def add_user_cost(self, user: str, day: str, cost: float) -> None:
        await self.db.execute("UPDATE usage SET cost_usd = cost_usd + ? WHERE user = ? AND day = ?",
                              (cost, user, day))
        await self.db.commit()

    async def month_cost(self, user: str, month: str) -> float:
        """Money a user spent in a calendar month (`month` = "YYYY-MM"): the sum of their daily rows."""
        cur = await self.db.execute("SELECT COALESCE(SUM(cost_usd), 0) FROM usage WHERE user = ? AND day LIKE ?",
                                    (user, f"{month}-%"))
        row = await cur.fetchone()
        return float(row[0]) if row else 0.0

    async def usage(self, user: str, day: str) -> dict[str, Any]:
        """Today's row for a user: {"questions": n, "cost_usd": x} (zeros if they haven't asked yet)."""
        cur = await self.db.execute("SELECT questions, cost_usd FROM usage WHERE user = ? AND day = ?", (user, day))
        row = await cur.fetchone()
        return {"questions": row[0], "cost_usd": row[1]} if row else {"questions": 0, "cost_usd": 0.0}

    async def delete(self, tid: str) -> None:
        await self.db.execute("DELETE FROM threads WHERE id=?", (tid,))
        await self.db.commit()
