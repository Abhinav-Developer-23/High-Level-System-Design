#!/usr/bin/env python3
"""Rebuild a numbered table of contents (H1s, with H2s as sub-bullets) in place.

usage: python3 tools/md-polish/toc.py <doc.md> [--before OLD_COPY.md] [--write]
The TOC is the list under the heading containing "Table of Contents", up to the next `---`.
With --before, H1s whose H2 list is unchanged since OLD_COPY keep their existing hand-picked
sub-bullets; changed or new H1s list all their H2s. Without it, every H1 lists all its H2s.
"""
import re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from anchors import headings

def parse(path):
    raw = pathlib.Path(path).read_bytes().decode('utf-8')
    return raw, raw.replace('\r\n', '\n').split('\n')

def structure(lines):
    """[(h1_text, h1_slug, [(h2_text, h2_slug), ...])] for H1s after the TOC."""
    out, seen_toc = [], False
    for n, lvl, text, slug in headings(lines):
        if lvl == 1 and 'Table of Contents' in text: seen_toc = True; continue
        if not seen_toc: continue
        if lvl == 1: out.append((text, slug, []))
        elif lvl == 2 and out: out[-1][2].append((text, slug))
    return out

def toc_bounds(lines):
    s = next(i for i, l in enumerate(lines) if l.startswith('#') and 'Table of Contents' in l)
    first = next(i for i in range(s + 1, len(lines)) if re.match(r'^\d+\. \[', lines[i]))
    end = next(i for i in range(first, len(lines)) if lines[i].strip() == '---')
    return first, end

def old_subs(lines):
    a, b = toc_bounds(lines); subs, cur = {}, None
    for l in lines[a:b]:
        m = re.match(r'^\d+\. \[.*\]\(#([^)]+)\)', l)
        if m: cur = m.group(1); subs[cur] = []; continue
        m = re.match(r'^\s+- (\[.*\]\(#([^)]+)\))', l)
        if m and cur: subs[cur].append((m.group(1), m.group(2)))
    return subs

clean = lambda t: re.sub(r'^\d+\.\s+', '', t.replace('**', '')).strip()

def main():
    doc = sys.argv[1]
    raw, L = parse(doc); crlf = '\r\n' in raw
    new = structure(L)
    old_struct, old_s = {}, {}
    if '--before' in sys.argv:
        _, OL = parse(sys.argv[sys.argv.index('--before') + 1])
        old_struct = {slug: [t for t, _ in h2] for _, slug, h2 in structure(OL)}
        old_s = old_subs(OL)
    valid = {h[3] for h in headings(L)}
    out = []
    for k, (text, slug, h2) in enumerate(new, 1):
        out.append(f'{k}. [{clean(text)}](#{slug})')
        keep = slug in old_struct and old_struct[slug] == [t for t, _ in h2] and slug in old_s
        subs = [(lbl, a) for lbl, a in old_s.get(slug, []) if a in valid] if keep else [(f'[{clean(t)}](#{s})', s) for t, s in h2]
        pad = ' ' * len(f'{k}. ')  # sub-list must start where the item text starts
        out += [f'{pad}- {lbl}' for lbl, _ in subs]
    a, b = toc_bounds(L)
    L[a:b] = out + ['']
    s = '\n'.join(L)
    print(f'{len(new)} H1 entries, {len(out)} TOC lines')
    if '--write' in sys.argv:
        pathlib.Path(doc).write_bytes((s.replace('\n', '\r\n') if crlf else s).encode('utf-8')); print('written')

if __name__ == '__main__': main()
