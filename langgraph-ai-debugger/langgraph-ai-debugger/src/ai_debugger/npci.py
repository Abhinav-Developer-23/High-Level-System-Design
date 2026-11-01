"""NPCI UPI error / response code map.

`data/npci_error_codes.json` is generated from the NPCI spec by
`scripts/build_npci_map.py`. One code can mean different things per API section, so
every code maps to a list of meanings.

Used three ways: `extract_codes` finds candidate codes in free text, `resolve` / `lookup`
turn codes into meanings, and `as_markdown` renders them as the table that goes into the
prompts and the final report. No LLM involved — it is a dictionary lookup.

Background for beginners
------------------------
NPCI is the body that runs UPI. When a payment fails, NPCI returns a short code like `ZM`
("invalid MPIN") or `U30`. This file answers "what does ZM mean?".

The JSON file looks like this (a dict of code → list of meanings):

    {"codes": {"ZM": [{"section": "3.1 Pay / Collect", "meaning": "INVALID MPIN",
                       "remarks": "...", "decline_type": "Business"}, ...], ...}}

Try it from a terminal: `uv run ai-debugger npci ZM`.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import TypedDict

DATA = Path(__file__).with_name("data") / "npci_error_codes.json"

# Our own switch emits these alongside NPCI codes; they are not in the spec.
EXTRA: dict[str, str] = {
    "DEEMED": "Txn outcome unknown at NPCI (timeout); settled later by check-status / recon",
}


# TypedDict = "a normal dict, but with these exact keys and value types" (for type checking and
# for readers; at runtime it's just a dict).
class Meaning(TypedDict):
    section: str       # NPCI spec section the meaning comes from, e.g. "3.1 Pay / Collect"
    meaning: str
    remarks: str
    decline_type: str  # e.g. technical vs business decline, when the spec says


class Resolved(TypedDict):
    """A code together with all its meanings (best-ranked section first)."""
    code: str
    meanings: list[Meaning]


@lru_cache(maxsize=1)
def code_map() -> dict[str, list[Meaning]]:
    """The whole JSON file as a dict, loaded once (@lru_cache remembers the result)."""
    return json.loads(DATA.read_text(encoding="utf-8"))["codes"]


# Core payment-flow sections first; niche products (UPI Lite, mandates, ...) after.
_SECTION_RANK = ("3.1 ", "4.4 ", "4.3", "3.2 ", "3.3 ", "3.4 ", "3.5 ", "4.5 ", "4.6", "4.7 ", "4.1 ", "4.8 ")


def _rank(m: Meaning) -> int:
    """Sort key: position of the meaning's section in `_SECTION_RANK` (unknown sections last)."""
    sec = m["section"]
    # enumerate gives (index, item) pairs. The `( ... for ... if ...)` is a generator: it yields
    # the index of each matching prefix. next(gen, default) takes the first one, or the default
    # if there is none. So: "position of the first matching prefix, else put it last".
    return next((i for i, p in enumerate(_SECTION_RANK) if sec.startswith(p)), len(_SECTION_RANK))


def lookup(code: str) -> list[Meaning]:
    """All meanings of one code, most relevant section first; [] if unknown.

    sorted(items, key=f) sorts by f(item) instead of the item itself; here by section rank.
    """
    return sorted(code_map().get(code.strip().upper(), []), key=_rank)


def search(query: str, limit: int = 25) -> list[Resolved]:
    """Exact code first, then codes whose meaning contains every word of the query."""
    q = query.strip()
    if not q:
        return []
    out: list[Resolved] = []
    exact = lookup(q)
    if exact:
        out.append({"code": q.upper(), "meanings": exact})
    # Split the query on any whitespace: "invalid mpin" → ["INVALID", "MPIN"].
    words = [w for w in re.split(r"\s+", q.upper()) if w]
    for code, meanings in code_map().items():
        if len(out) >= limit:
            break  # leave the loop entirely — we have enough results
        if code == q.upper():
            continue
        text = " ".join(m["meaning"] for m in meanings).upper()
        # all(...) is True only if every word appears; `w in text` is a substring check.
        if all(w in text for w in words):
            out.append({"code": code, "meanings": meanings})
    return out


# Regex reminders for the patterns below:
#   \b      word boundary          (?:...)  group that is not captured
#   (...)   captured group → m.group(1)   (?i:...) case-insensitive just inside this group
#   [A-Z0-9]{2,4}  2 to 4 capital letters/digits     ?  previous thing is optional
#   (?<!...) / (?!...)  "not preceded by" / "not followed by" (lookarounds)
# The adjacent r"..." r"..." strings are glued together by Python into one pattern.

# `respCode="ZM"`, `errCode: U30`, `reason code RB`, `response code - BT` ...
_KV = re.compile(
    r"\b(?i:resp(?:onse)?[_ ]?code|err(?:or)?[_ ]?code|reason[_ ]?code|npci[_ ]?code|"
    r"result[_ ]?code|decline[_ ]?code|code)(?i:s)?\b[\"'\s]*[:=\-]?[\"'\s]*([A-Z0-9]{2,4})\b"
)
# lists right after "code(s)": "codes ZM, U30 and RB"
_LIST = re.compile(r"\b(?i:codes?)\b((?:[\s,/]*(?:and|or)?\s*[\"']?[A-Z0-9]{2,4}[\"']?){1,10})")
# XML attributes in NPCI exchange logs: errCode="U30" respCode="ZM"
_XML = re.compile(r"\b(?:errCode|respCode|reasonCode)=\"([A-Z0-9]{2,4})\"")
# mixed letter+digit tokens are distinctive enough on their own (U30, Z9, B3, XH is not)
_MIXED = re.compile(r"\b([A-Z]{1,2}[0-9]{1,2}|[A-Z][0-9][A-Z0-9])\b")
_STOP = {"IST", "UTC", "TPAP", "TSP", "DB", "OK", "ID", "API", "SQL", "ELK", "PMM", "KQL", "C2", "C3",
         "C6", "C1", "P0", "P1", "P2", "UPI", "NPCI", "AND", "OR", "THE", "TXN", "RRN", "VPA"}


# Any standalone 2–3 char all-caps token, e.g. the "ZM" in "what is ZM?" (used only when loose=True).
_CAPS = re.compile(r"(?<![A-Za-z0-9_\-])([A-Z0-9]{2,3})(?![A-Za-z0-9_\-])")


def extract_codes(text: str, loose: bool = False) -> list[str]:
    """Candidate NPCI codes in free text, kept only if the map knows them.

    `loose` also accepts any bare 2–3 char all-caps token — right for a user's question
    ("what is ZM?"), too noisy for long agent output.
    """
    found: list[str] = []

    # Every pattern below only proposes candidates; `add` keeps a token only if the code map
    # actually knows it, which is what keeps false positives like "THE" or "OK" out.
    def add(c: str) -> None:
        c = c.strip().strip("\"'").upper()
        if c and c not in _STOP and c not in found and (c in code_map() or c in EXTRA):
            found.append(c)

    # finditer yields one match object per hit; m.group(1) is the text of the first (...) group.
    # Example: _XML on 'errCode="U30"' → m.group(1) == "U30".
    for m in _XML.finditer(text):
        add(m.group(1))
    for m in _KV.finditer(text):
        add(m.group(1))
    for m in _LIST.finditer(text):
        for tok in re.findall(r"[A-Za-z0-9]{2,4}", m.group(1)):
            if tok.lower() not in {"and", "or"} and tok.upper() == tok:
                add(tok)
    for m in _MIXED.finditer(text):
        add(m.group(1))
    if loose:
        for m in _CAPS.finditer(text):
            tok = m.group(1)
            # skip bare numbers, and "AM"/"PM" right after a time like "10:30 AM"
            if tok.isdigit() or (tok in {"AM", "PM"} and re.search(r"\d\s*$", text[: m.start()])):
                continue
            add(tok)
    return found


def resolve(codes: list[str]) -> list[Resolved]:
    """Codes → meanings, dropping codes the map does not know. `EXTRA` codes are handled here too."""
    out: list[Resolved] = []
    for c in codes:
        if c in EXTRA:
            out.append({"code": c, "meanings": [
                {"section": "switch status", "meaning": EXTRA[c], "remarks": "", "decline_type": ""}]})
            continue
        meanings = lookup(c)
        if meanings:
            out.append({"code": c, "meanings": meanings})
    return out


def as_markdown(resolved: list[Resolved], max_meanings: int = 3) -> str:
    """Markdown table, one row per (code, section), at most `max_meanings` sections per code."""
    if not resolved:
        return ""
    # A Markdown table is plain text: a header row, a |---| separator row, then one row per line.
    rows = ["| Code | Meaning | Type | Section |", "|---|---|---|---|"]
    for r in resolved:
        # Group meanings by section. setdefault(key, []) returns the existing list for the key,
        # or stores and returns a new empty one — so .append always has a list to add to.
        by_section: dict[str, list[Meaning]] = {}
        for m in r["meanings"]:
            by_section.setdefault(m["section"], []).append(m)
        for section, ms in list(by_section.items())[:max_meanings]:
            m = ms[0]
            # A "|" inside a cell would break the table, so swap it for "/".
            meaning = m["meaning"].replace("|", "/")
            if m["remarks"]:
                meaning += f" — {m['remarks'].replace('|', '/')}"
            if len(ms) > 1:
                meaning += f" _(+{len(ms) - 1} more variants)_"
            rows.append(f"| `{r['code']}` | {meaning} | {m['decline_type'] or '-'} | {section} |")
    return "\n".join(rows)
