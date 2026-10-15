#!/usr/bin/env python3
"""Step 1: find ASCII diagram code blocks in a markdown file and write one input file per block.

usage: python3 tools/svg-diagrams/extract.py <doc.md> [--extra LINE ...] [--chunks N]
  --extra LINE  also include the untagged block whose opening fence is on LINE (1-based),
                for diagrams the auto-detector misses (e.g. trees drawn with / | \\)
  --chunks N    print an N-way split of the block ids (for parallel agents)

Writes work/<doc-stem>/blocks/DNNN.txt, work/<doc-stem>/manifest.json and an empty results/ dir.
"""
import argparse, json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
DIAGRAM = re.compile(r'[─│┌┐└┘├┤▶◀▼▲→←↓↑═║╔╗┬┴┼]|-->|==>|\+--')

ap = argparse.ArgumentParser()
ap.add_argument('doc'); ap.add_argument('--extra', type=int, nargs='*', default=[]); ap.add_argument('--chunks', type=int, default=0)
a = ap.parse_args()
doc = pathlib.Path(a.doc).resolve()
work = HERE / 'work' / doc.stem
(work / 'blocks').mkdir(parents=True, exist_ok=True); (work / 'results').mkdir(exist_ok=True)

lines = doc.read_text(encoding='utf-8').split('\n')
lines = [l.rstrip('\r') for l in lines]
blocks, inb = [], False
for i, l in enumerate(lines):
    if l.strip().startswith('```'):
        if not inb: inb, start, lang = True, i, l.strip()[3:].strip()
        else: inb = False; blocks.append((start, i, lang, lines[start + 1:i]))

sel = [b for b in blocks if b[2] in ('', 'text', 'plaintext')
       and (any(DIAGRAM.search(l) for l in b[3]) or b[0] + 1 in a.extra)]
manifest = []
for n, (s, e, _, body) in enumerate(sel, 1):
    bid = f'D{n:03d}'
    heads = [l for l in lines[:s] if l.startswith('#')]
    (work / 'blocks' / f'{bid}.txt').write_text(
        f"ID: {bid}\nSOURCE: {doc.name} lines {s + 1}-{e + 1}\nNEAREST HEADING: {heads[-1] if heads else ''}\n\n"
        f"=== CONTEXT BEFORE ===\n" + '\n'.join(lines[max(0, s - 8):s]) +
        "\n\n=== ASCII DIAGRAM (convert this) ===\n" + '\n'.join(body) +
        "\n=== END DIAGRAM ===\n\n=== CONTEXT AFTER ===\n" + '\n'.join(lines[e + 1:e + 5]) + '\n', encoding='utf-8')
    manifest.append({'id': bid, 'start': s + 1, 'end': e + 1, 'body': '\n'.join(body)})
(work / 'manifest.json').write_text(json.dumps({'doc': str(doc), 'blocks': manifest}, ensure_ascii=False), encoding='utf-8')
print(f'{len(manifest)} diagram blocks -> {work}')
if a.chunks:
    w = [len(m['body'].split('\n')) + 6 for m in manifest]; per = sum(w) / a.chunks; out, acc = [[]], 0
    for m, x in zip(manifest, w):
        if acc >= per * len(out) and len(out) < a.chunks: out.append([])
        out[-1].append(m['id']); acc += x
    for c in out: print(f'  {c[0]}-{c[-1]} ({len(c)})')
