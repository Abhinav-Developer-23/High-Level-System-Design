#!/usr/bin/env python3
"""Quiz mode: collapse the content under every heading into <details> toggles.

usage: python3 tools/md-polish/toggles.py <doc.md> [--flat] [--write]   add toggles (dry run without --write)
       python3 tools/md-polish/toggles.py <doc.md> --remove [--write]   take them all out again

Default is NESTED: a heading's toggle holds its intro text AND all its sub-headings (each with
their own toggle), so a fully collapsed document shows only the top-level headings.
  - toggles that contain sub-headings are labelled "Open section"
  - innermost toggles are labelled "Show answer"
--flat wraps only the text directly under each heading (every heading stays visible).

Headings stay real markdown headings, so the TOC and anchors keep working (browsers open the
enclosing toggles when you follow a link or Ctrl+F into them). The Table of Contents and `---`
separators stay outside toggles. Run --remove before switching modes. Line endings are preserved.
"""
import re, sys, pathlib

SECTION, ANSWER = 'Open section', 'Show answer'
SUMMARY = re.compile(r'^<summary>(Open section|Show answer)</summary>$')

def scan(lines):
    """[(index, level)] of headings outside code fences."""
    fence, out = False, []
    for i, l in enumerate(lines):
        if l.strip().startswith('```'): fence = not fence
        elif not fence:
            m = re.match(r'^(#{1,6})\s+\S', l)
            if m: out.append((i, len(m.group(1))))
    return out

def has_text(lines):
    return any(l.strip() not in ('', '---') for l in lines)

def pop_tail(out):
    tail = []
    while out and out[-1].strip() in ('', '---'): tail.insert(0, out.pop())
    return tail

def add(lines, flat=False):
    hs = scan(lines)
    if not hs: return lines, 0
    if any(SUMMARY.match(l.strip()) for l in lines): sys.exit('already has toggles: run --remove first')
    out, stack, n = lines[:hs[0][0]], [], 0
    for k, (h, lvl) in enumerate(hs):
        nxt = hs[k + 1][0] if k + 1 < len(hs) else len(lines)
        # where this heading's toggle ends: next heading of same/higher level (nested) or next heading (flat)
        sec_end = nxt
        if not flat:
            sec_end = next((i for i, l2 in hs[k + 1:] if l2 <= lvl), len(lines))
        # close toggles that this heading ends
        tail = pop_tail(out)
        while stack and (flat or stack[-1] >= lvl):
            out += ['', '</details>']; stack.pop()
        out += (tail or [''])
        out.append(lines[h])
        body = lines[h + 1:nxt]
        is_toc = 'Table of Contents' in lines[h]
        if is_toc or not has_text(lines[h + 1:sec_end]):
            out += body
            continue
        has_children = not flat and sec_end > nxt
        out += ['', '<details>', f'<summary>{SECTION if has_children else ANSWER}</summary>', '']
        a = 0
        while a < len(body) and not body[a].strip(): a += 1
        out += body[a:]
        stack.append(lvl); n += 1
    tail = pop_tail(out)
    while stack: out += ['', '</details>']; stack.pop()
    out += tail or ['']
    return out, n

def remove(lines):
    out, n, i = [], 0, 0
    while i < len(lines):
        s = lines[i].strip()
        if s == '<details>' and i + 1 < len(lines) and SUMMARY.match(lines[i + 1].strip()):
            i += 2; n += 1; continue
        if s == '</details>':
            i += 1; continue
        out.append(lines[i]); i += 1
    text = '\n'.join(out)
    text = re.sub(r'\n{3,}', '\n\n', text)          # collapse blank lines left behind
    return text.split('\n'), n

def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    p = pathlib.Path(sys.argv[1])
    raw = p.read_bytes().decode('utf-8'); crlf = '\r\n' in raw
    lines = raw.replace('\r\n', '\n').split('\n')
    if '--remove' in sys.argv:
        out, n = remove(lines); print(f'{n} toggles removed')
    else:
        out, n = add(lines, flat='--flat' in sys.argv); print(f'{n} toggles added ({"flat" if "--flat" in sys.argv else "nested"})')
    if '--write' in sys.argv:
        s = '\n'.join(out)
        p.write_bytes((s.replace('\n', '\r\n') if crlf else s).encode('utf-8')); print('written', p)

if __name__ == '__main__':
    main()
