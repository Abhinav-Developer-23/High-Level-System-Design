# ASCII → SVG diagram conversion: style guide

Paths (all relative to the repo root)
- Inputs: tools/svg-diagrams/work/<doc>/blocks/DNNN.txt. Each holds the ASCII diagram plus the surrounding markdown for context. They are made by extract.py.
- Output SVGs: svg/<topic>/dNNN-<short-kebab-slug>.svg, e.g. svg/dbms/d042-alter-inplace-timeline.svg.
- Result record: tools/svg-diagrams/work/<doc>/results/DNNN.json, containing {"id":"DNNN","action":"svg"|"keep","file":"dNNN-slug.svg","alt":"one-line description","note":"optional, e.g. why kept or what changed"}
- Reference example (match this look): svg/dbms/d150-wal-commit-happy-path.svg
- QA tool: python3 -I tools/svg-diagrams/svgcheck.py <svg files...>. It prints lint issues (text outside the canvas, text overflowing its enclosing rect, overlapping text) and writes tools/svg-diagrams/out/<name>.png. Open the PNG with the Read tool to look at it.

DO NOT edit the markdown file. Only create SVGs and result JSONs. The coordinator runs apply.py.

## When to keep it as ASCII (action "keep")
Only when the block is not really a diagram: MySQL console result sets (+----+---+ tables), a raw query/EXPLAIN output, or plain code. Everything else becomes an SVG: flows, timelines, T1/T2 schedules, trees, before/after, comparisons, step lists with arrows.

## Content fidelity (most important)
- Every label, value, number, annotation, ✅/❌ verdict and side-comment in the ASCII must appear in the SVG. Nothing may be dropped or invented.
- If the source itself is wrong (e.g. a schedule called serializable that has a cycle), draw it faithfully and say so in the result "note". The coordinator decides on the fix.
- You may restructure the layout for clarity: real boxes, lanes, columns, colored states, proper arrows. You may fix obvious typos.
- Use the context around the block to understand what the diagram is teaching, then make that point visually obvious with color (e.g. the failing path in red, the correct one in green).
- Keep SQL, function names, and code in monospace.

## Canvas
- Root: <svg xmlns="http://www.w3.org/2000/svg" width="W" height="H" viewBox="0 0 W H" font-family="Segoe UI, Inter, system-ui, -apple-system, sans-serif">
- width/height must equal the viewBox (integer px). W usually 600–900, never above 960. Height fits the content, with no big empty areas.
- Include <title> and <desc>.
- Put style="font-variant-ligatures:none" on the root <svg>. Otherwise Cascadia Code turns >= into ≥.
- Spaces inside <text> collapse when rendered. Indent code with &#160; or position each line with x=; xml:space / white-space:pre don't help.
- Escape & as &amp; and < as &lt; in text. The file must be well-formed XML, even though Chrome tolerates some mistakes.
- First element is the card: <rect x="0.5" y="0.5" width="W-1" height="H-1" rx="14" fill="#161b22" stroke="#30363d"/>
- Padding: 24px or more inside the card.
- No external resources, no <style> with @import, no scripts, no foreignObject, no web fonts, no filters (keep it crisp).

## Palette (dark only; matches MarkView dark / GitHub dark)
- Card bg #161b22 · node fill #1c2128 · border #30363d · subtle divider #21262d · dashed/async border #484f58
- Text: primary #e6edf3 · body #c9d1d9 · muted/labels #8b949e
- Code/mono text: #79c0ff (or #e6edf3 inside a code box)
- Semantic accents (stroke color, light text color, fill = accent at fill-opacity .10–.16):
  - blue (neutral emphasis / process)  stroke #58a6ff  text #79c0ff
  - green (success / correct / durable / committed)  #3fb950  text #56d364
  - red (failure / crash / wrong / conflict / lost)  #f85149  text #ff7b72
  - amber (warning / caution / waiting / partial)  #d29922  text #e3b341
  - purple (memory / RAM / transaction T1)  #bc8cff  text #d2a8ff
  - teal (disk / storage / transaction T2)  #39c5cf  text #56d4dd
  - orange (T3 / a third actor) #f0883e text #ffa657
- Use color to carry meaning consistently. Don't paint everything blue. Most boxes stay neutral (#1c2128 / #30363d), and accents mark what matters.

## Typography
- Sans stack (default, on root) for prose. Mono: font-family="Cascadia Code, JetBrains Mono, Consolas, monospace".
- Sizes: section header labels 12px bold, letter-spacing 1.5, muted, uppercase (like "CLIENT"); box titles 14–15px weight 600 #e6edf3; body 13px #c9d1d9; small notes 12px #8b949e. Nothing smaller than 11px.
- Width estimates when sizing boxes: sans 13px ≈ 7px per char (bold ≈ 7.6); mono 12px ≈ 7.3px per char; mono 13px ≈ 7.9. Leave 14px or more of inner padding. The lint tool is the final judge.
- Multi-line text: use separate <text> elements or <tspan x=.. y=..> lines with 18–20px line height.
- Emoji: avoid. Use ✓ ✗ ⚠ glyphs or small drawn shapes (circle with check, etc.) colored green/red/amber.

## Shapes & arrows
- Boxes rx 8–10. Pills/badges rx = height/2, height 22.
- Arrows: define <marker> in <defs> (see example) with unique ids per color; stroke-width 1.5–2; gray #8b949e by default, accent color when the arrow means something (green = ack/success, red = failure).
- Timelines: horizontal axis with tick labels; T1/T2 schedules become a two- or three-column lane table with a time column, lanes tinted purple/teal/orange, and events as rows; conflicts/dirty reads highlighted red with a note.
- Trees (B/B+ trees): node boxes with key cells separated by thin dividers, edges as lines, leaf-level linked arrows if the ASCII shows ↔.
- Before/after or ❌/✅ comparisons: side-by-side panels, with headers tinted red and green.

## QA loop (required for every SVG)
1. Write the SVG.
2. Run svgcheck.py on it and fix every lint issue. "OVERFLOWS BOX" means widen the box or wrap the text. If a text is intentionally outside a rect it overlaps (e.g. a label sitting on a line), put data-nocheck="1" on that <text>.
3. Open out/<name>.png with Read and look at it: alignment, spacing, nothing clipped, arrows touching the right boxes, readable.
4. Then write results/DNNN.json.
Batch: you may lint several SVGs per call, but you must view every PNG at least once after its final edit.
