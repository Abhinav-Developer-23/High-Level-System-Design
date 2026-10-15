#!/usr/bin/env python3
"""Step 3: replace each converted ASCII block in the markdown with an image link.

usage: python3 tools/svg-diagrams/apply.py <doc.md> <svg-dir> [--write]
  e.g. apply.py DBMS/DBMS1.md svg/dbms --write
Dry run by default. A block is replaced only if its text still matches what extract.py saw,
and nothing is written while any result is missing or any SVG file is absent.
Line endings (CRLF/LF) of the doc are preserved.
"""
import json, os, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
if len(sys.argv) < 3: sys.exit(__doc__)
doc, svgdir = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
work = HERE / 'work' / doc.stem
man = {m['id']: m for m in json.loads((work / 'manifest.json').read_text(encoding='utf-8'))['blocks']}
raw = doc.read_bytes().decode('utf-8'); crlf = '\r\n' in raw
lines = raw.replace('\r\n', '\n').split('\n')
rel = pathlib.Path(os.path.relpath(svgdir, doc.parent)).as_posix()

res = {r['id']: r for r in (json.loads(f.read_text(encoding='utf-8')) for f in (work / 'results').glob('D*.json'))}
missing = [i for i in man if i not in res]
problems = [f"{i}: missing {r['file']}" for i, r in res.items() if r['action'] == 'svg' and not (svgdir / r['file']).exists()]
todo = sorted((r for r in res.values() if r['action'] == 'svg'), key=lambda r: -man[r['id']]['start'])
for r in todo:
    m = man[r['id']]; s, e = m['start'] - 1, m['end'] - 1
    if not lines[s].strip().startswith('```') or lines[e].strip() != '```' or '\n'.join(lines[s + 1:e]) != m['body']:
        problems.append(f"{r['id']}: block moved or changed since extract, skipped"); continue
    alt = re.sub(r'[\[\]\n]', ' ', r.get('alt', 'diagram')).strip()
    lines[s:e + 1] = [f'![{alt}]({rel}/{r["file"]})']

print(f"results {len(res)} | svg {len(todo)} | keep {sum(r['action'] == 'keep' for r in res.values())} | missing {missing}")
print('problems:', problems or 'none')
if '--write' in sys.argv:
    if problems or missing: sys.exit('not written: fix the problems above first')
    out = '\n'.join(lines)
    doc.write_bytes((out.replace('\n', '\r\n') if crlf else out).encode('utf-8')); print('written:', doc)
