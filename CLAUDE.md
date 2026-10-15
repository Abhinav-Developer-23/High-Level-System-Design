# CLAUDE.md

Personal interview-prep notes (system design, DBMS, Java, LLD, networking) as markdown. The user reads them in Chrome with the **MarkView** extension in **dark theme**, so check rendering against that.

## Diagrams: ASCII → SVG

Diagrams are dark-theme SVGs in `svg/<topic>/`, embedded with relative links (e.g. `![alt](../svg/dbms/d150-wal-commit-happy-path.svg)` from `DBMS/DBMS1.md`). Tooling is in `tools/svg-diagrams/` (Windows Chrome is driven from WSL):

1. `python3 tools/svg-diagrams/extract.py <doc.md> --chunks N` finds the ASCII diagram blocks and writes one input file per block to `work/<doc>/blocks/`. Use `--extra LINE` for blocks it misses (trees drawn with `/ | \`).
2. Convert each block to an SVG following `tools/svg-diagrams/STYLE.md` (palette, fonts, content-fidelity rules). For big docs, split the ids across parallel agents. Agents write SVGs + `results/DNNN.json` only, never the markdown.
3. QA every SVG: `python3 tools/svg-diagrams/svgcheck.py <files>`. It must report no issues, and look at the PNG it writes to `out/`.
4. `python3 tools/svg-diagrams/apply.py <doc.md> svg/<topic>` does a dry run; add `--write` to replace the blocks. It refuses if any block changed since step 1.
5. Optional: `node tools/svg-diagrams/preview.js <doc.md> [start end]` renders a MarkView-like dark preview to `out/preview.png` (run `npm install` in that folder once).

Keep MySQL console output / EXPLAIN result sets as code blocks. They're not diagrams.

## Table styling

`tools/svg-diagrams/markview-style.html` is a `<style>` block that styles tables and diagram images for MarkView's dark theme (it targets `html.markview-dark #markview-container`). Paste it at the top of a doc only when the user asks for it. `DBMS/DBMS1.md` already has it. MarkView renders raw HTML without sanitizing, so `<style>` works there; GitHub strips it.

## Repo notes

- Many files have CRLF line endings. Preserve them when rewriting a file.
- Git has no user identity configured in WSL. Pass it with `git -c user.name=… -c user.email=…`, matching earlier commits.
