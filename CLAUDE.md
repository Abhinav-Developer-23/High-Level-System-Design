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

### New diagrams: Mermaid or SVG?

- **Mermaid** (a ```` ```mermaid ```` block, which MarkView renders and themes dark automatically) for simple diagrams that will change: flowcharts, sequence diagrams, ER diagrams, state machines. They stay editable as text. Don't add a theme `%%{init}%%`; MarkView picks the theme itself.
- **Hand-made SVG** (via the steps above) when layout carries the meaning, e.g. T1/T2 schedule lanes, timelines with crash points, B+ trees, before/after panels.

## Dark styling and callouts

- `tools/svg-diagrams/markview-style.html` is a `<style>` block for MarkView's dark theme: headings, tables, code, blockquotes, callouts and diagram images. It targets `html.markview-dark #markview-container`. Paste it at the top of a doc only when the user asks for it. `DBMS/DBMS1.md` has it; when the file changes, update that copy too. MarkView renders raw HTML without sanitizing, so `<style>` works there; GitHub strips it.
- `python3 tools/md-polish/callouts.py <doc.md> [--write]` turns `>` blockquotes into alerts (`> [!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`, `[!NOTE]`) from their leading label (e.g. "Interview tip:" → TIP, "Key takeaway:" → IMPORTANT, "⚠️" → WARNING). Navigation and link blockquotes stay plain. Dry-run first and review the list.
- `python3 tools/md-polish/anchors.py <doc.md>` lists broken in-page `(#anchor)` links. It uses github-slugger rules, the same as MarkView. Run it after renaming or merging headings.
- `python3 tools/md-polish/toc.py <doc.md> --before <old copy> --write` rebuilds the numbered TOC. Sections whose H2s didn't change keep their hand-picked bullets, and changed sections list all their H2s.
- `python3 tools/md-polish/toggles.py <doc.md> [--flat] [--remove] --write` gives quiz mode: content under each heading goes into collapsed `<details>` toggles. The default is nested: a heading's toggle also holds its sub-headings ("Open section"), and the innermost ones say "Show answer". `--flat` wraps only the text directly under each heading. Headings stay real, so the TOC and anchors keep working. `DBMS/DBMS1.md` uses nested mode: to add a section, run `--remove`, edit, then run it again. Obsidian doesn't render markdown inside `<details>`; MarkView and GitHub do.

## Repo notes

- Many files have CRLF line endings. Preserve them when rewriting a file.
- Git has no user identity configured in WSL. Pass it with `git -c user.name=… -c user.email=…`, matching earlier commits.
