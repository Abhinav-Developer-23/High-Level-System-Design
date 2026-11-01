"""Turn the NPCI "UPI Error and Response Codes" text dump into a code -> meanings map.

    uv run python scripts/build_npci_map.py

Reads  resources/Docs/NPCI error codes.txt   (pdftotext output of UPI spec v2.9)
Writes src/ai_debugger/data/npci_error_codes.json

The dump is one cell per line. A row is: code, description lines, optional remark
lines (after a blank cell), then the decline-type cell (TD / BD / -). The same code
can mean different things in different sections (e.g. RespPay vs ReqPay), so every
code maps to a list of {section, meaning, remarks, decline_type}.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "resources" / "Docs" / "NPCI error codes.txt"
OUT = ROOT / "src" / "ai_debugger" / "data" / "npci_error_codes.json"

CODE_RE = re.compile(r"^(?:[A-Z0-9]{2,5}|[A-Z0-9]{2,5}\s*-\s*[A-Z0-9]{2,5})$")
SECTION_RE = re.compile(r"^(\d(?:\.\d+){1,2})\s+(.+?)\s*$")
TYPE_MARKERS = {"TD", "BD", "-", "TD/BD"}
NOISE_RE = re.compile(r"^(UPI Error and Response Codes|Page \d+ of \d+.*|Public - UPI.*)$")
# The body starts after the table of contents; the TOC lines end in "..... <page>".
TOC_RE = re.compile(r"\.{5,}\s*\d+\s*$")
HEADER_CELLS = {"Response code", "Description", "Remarks", "TD/BD", "Error Code", "Error code",
                "Response Code", "Code", "Element", "Attribute", "Reason", "Error Description"}


def _clean(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def parse(text: str) -> dict[str, list[dict[str, str]]]:
    lines = [_clean(raw) for raw in text.splitlines()]
    section = ""
    out: dict[str, list[dict[str, str]]] = {}
    cur: dict[str, object] | None = None

    def flush() -> None:
        nonlocal cur
        if not cur:
            return
        desc: list[str] = cur["desc"]  # type: ignore[assignment]
        rem: list[str] = cur["remarks"]  # type: ignore[assignment]
        meaning = " ".join(desc).strip(" -")
        if meaning and re.search(r"[A-Za-z]{3}", meaning):
            for code in _expand(str(cur["code"])):
                out.setdefault(code, []).append({
                    "section": section,
                    "meaning": meaning,
                    "remarks": " ".join(rem).strip(),
                    "decline_type": str(cur.get("type", "")),
                })
        cur = None

    started = False
    for line in lines:
        if not started:
            # first real body heading after the TOC
            if line.startswith("3. Codes to be populated") and not TOC_RE.search(line):
                started = True
            continue
        if not line or NOISE_RE.match(line):
            if cur is not None and cur["desc"]:
                cur["gap"] = True
            continue
        m = SECTION_RE.match(line)
        if m and not CODE_RE.match(line) and len(line) > 6 and re.search(r"[a-z]", line):
            flush()
            section = f"{m.group(1)} {m.group(2)}".rstrip(" :")
            continue
        if section.endswith(("&", ",")) and cur is None:
            section = f"{section} {line}".rstrip(" :")
            continue
        if line in HEADER_CELLS:
            continue
        if cur is not None and line in TYPE_MARKERS and cur["desc"]:
            cur["type"] = line if line != "-" else ""
            flush()
            continue
        if CODE_RE.match(line) and line not in TYPE_MARKERS:
            flush()
            cur = {"code": line, "desc": [], "remarks": [], "gap": False}
            continue
        if cur is None:
            continue
        if cur["gap"]:
            cur["remarks"].append(line)  # type: ignore[union-attr]
        else:
            cur["desc"].append(line)  # type: ignore[union-attr]
    flush()
    return out


def _expand(code: str) -> list[str]:
    """`D04 - D11` -> D04..D11; anything else is returned as-is."""
    m = re.match(r"^([A-Z]*)(\d+)\s*-\s*([A-Z]*)(\d+)$", code)
    if not m or m.group(1) != m.group(3):
        return [code.replace(" ", "")]
    prefix, a, b = m.group(1), m.group(2), m.group(4)
    if int(b) - int(a) > 50 or int(b) < int(a):
        return [code.replace(" ", "")]
    return [f"{prefix}{n:0{len(a)}d}" for n in range(int(a), int(b) + 1)]


def main() -> int:
    data = parse(SRC.read_text(encoding="utf-8", errors="replace"))
    # dedupe identical rows that the PDF repeats across pages
    for code, rows in data.items():
        seen, uniq = set(), []
        for r in rows:
            key = (r["section"], r["meaning"])
            if key not in seen:
                seen.add(key)
                uniq.append(r)
        data[code] = uniq
    payload = {
        "source": "NPCI UPI Error and Response Codes v2.9 (resources/Docs/NPCI error codes.txt)",
        "count": len(data),
        "codes": dict(sorted(data.items())),
    }
    text = json.dumps(payload, indent=1, ensure_ascii=False) + "\n"
    if "--check" in sys.argv[1:]:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print(f"{OUT.relative_to(ROOT)} is stale; run scripts/build_npci_map.py", file=sys.stderr)
            return 1
        print(f"{OUT.relative_to(ROOT)} up to date: {len(data)} codes")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(data)} codes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
