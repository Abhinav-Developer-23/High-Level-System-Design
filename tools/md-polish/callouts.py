#!/usr/bin/env python3
"""Turn plain `>` blockquotes into GitHub/MarkView alerts based on their leading label.

usage: python3 tools/md-polish/callouts.py <doc.md> [--write]
Dry run prints each blockquote with the alert type it would get. Already-converted alerts
are skipped, so it is safe to re-run. Line endings are preserved.
"""
import re, sys, pathlib, collections

RULES = [  # first match wins; tested against the first line, lowercased
    ('SKIP',      r'deeper .* topics|roadmap|^🔗|^👉|^🟢|for the api-side pattern'),
    ('CAUTION',   r'^⛔|^\**never\b'),
    ('WARNING',   r'^⚠️|^⚠|gotcha|danger|warning|misconception|limitation|caution|^\**problem\b|^\**without rollback'),
    ('TIP',       r'interview|^\**tip\b|best practice|best for|rule of thumb|in practice|practical consequence'),
    ('IMPORTANT', r'key (idea|takeaway|point|insight|distinction|design choice|trade-off)|the key (insight|trade-off|point|idea)|golden rule|the write-ahead|may never be written|^\**rule\b|'
                  r'one rule|bottom line|the guarantee|important|punchline|critical detail|in one line|why (it|does this|this) matter'),
]

def classify(first):
    t = first.lstrip('> ').strip().lower()
    for kind, pat in RULES:
        if re.search(pat, t): return kind
    return 'NOTE'

def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    doc = pathlib.Path(sys.argv[1]); raw = doc.read_bytes().decode('utf-8'); crlf = '\r\n' in raw
    L = raw.replace('\r\n', '\n').split('\n'); out = []; i = 0; fence = False; tally = collections.Counter()
    while i < len(L):
        l = L[i]
        if l.strip().startswith('```'): fence = not fence
        if fence or not l.startswith('>'):
            out.append(l); i += 1; continue
        j = i
        while j < len(L) and L[j].startswith('>'): j += 1
        block = L[i:j]
        if re.match(r'^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', block[0]):
            kind = 'ALREADY'
        else:
            kind = classify(block[0])
        tally[kind] += 1
        if '--write' not in sys.argv: print(f'{i + 1:6d} {kind:9s} {block[0][:110]}')
        if kind in ('SKIP', 'ALREADY'):
            out += block
        else:
            first = re.sub(r'^>\s*(⚠️|⚠|⛔)\s*', '> ', block[0])  # the alert icon replaces these
            out += [f'> [!{kind}]', first] + block[1:]
        i = j
    print(dict(tally))
    if '--write' in sys.argv:
        s = '\n'.join(out); doc.write_bytes((s.replace('\n', '\r\n') if crlf else s).encode('utf-8')); print('written', doc)

main()
