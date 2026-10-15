#!/usr/bin/env python3
"""Check in-page links (#anchor) against heading slugs (GitHub/MarkView style).

usage: python3 tools/md-polish/anchors.py <doc.md>
Prints every broken [text](#anchor) link with its line number. Exit code 1 if any.
"""
import re, sys

def slugger():
    seen = {}
    def slug(text):
        # github-slugger (used by MarkView/GitHub) drops punctuation/emoji but keeps U+FE0F
        s = re.sub(r'[^\w\- \ufe0f]', '', text.strip().lower(), flags=re.U).replace(' ', '-')
        n = seen.get(s, 0); seen[s] = n + 1
        return s if n == 0 else f'{s}-{n}'
    return slug

def headings(lines):
    slug, fence, out = slugger(), False, []
    for i, l in enumerate(lines):
        if l.strip().startswith('```'): fence = not fence
        m = None if fence else re.match(r'^(#{1,6})\s+(.*?)\s*#*\s*$', l)
        if m: out.append((i + 1, len(m.group(1)), m.group(2), slug(m.group(2))))
    return out

def main():
    lines = open(sys.argv[1], encoding='utf-8').read().replace('\r', '').split('\n')
    slugs = {h[3] for h in headings(lines)}
    bad, fence = 0, False
    for i, l in enumerate(lines):
        if l.strip().startswith('```'): fence = not fence
        if fence: continue
        for a in re.findall(r'\]\(#([^)\s]+)\)', l):
            if a not in slugs:
                bad += 1; print(f'{i + 1}: #{a}')
    print(f'{bad} broken anchor link(s)')
    sys.exit(1 if bad else 0)

if __name__ == '__main__': main()
