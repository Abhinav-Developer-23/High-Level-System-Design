// Shared helpers for the AlgoMaster-style .mhtml pages (see md2mhtml.js and pages/*.js).
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const NM = path.join(__dirname, '../svg-diagrams/node_modules');
const hljs = require(path.join(NM, 'highlight.js'));

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const theme = () => fs.readFileSync(path.join(__dirname, 'theme.css'), 'utf8');

// ---------- MHTML (quoted-printable, CRLF, like Chrome's "Save as MHTML") ----------
function qp(str) {
  const bytes = Buffer.from(str.replace(/\r\n/g, '\n'), 'utf8'), lines = [];
  let line = '';
  const push = tok => { if (line.length + tok.length > 75) { lines.push(line + '='); line = ''; } line += tok; };
  for (let i = 0; i < bytes.length; i++) {
    const b = bytes[i];
    if (b === 10) {
      if (/[ \t]$/.test(line)) { const c = line.slice(-1); line = line.slice(0, -1); push('=' + c.charCodeAt(0).toString(16).toUpperCase().padStart(2, '0')); }
      lines.push(line); line = ''; continue;
    }
    push((b >= 33 && b <= 126 && b !== 61) || b === 32 || b === 9 ? String.fromCharCode(b) : '=' + b.toString(16).toUpperCase().padStart(2, '0'));
  }
  if (line) lines.push(line);
  return lines.join('\r\n');
}
function writeMhtml(outPath, html, title) {
  const boundary = '----MultipartBoundary--' + crypto.randomBytes(16).toString('hex') + '----';
  const subj = /^[\x20-\x7e]*$/.test(title) ? title : `=?utf-8?B?${Buffer.from(title).toString('base64')}?=`;
  const mhtml = [
    'From: <Saved by Blink>', `Subject: ${subj}`, `Date: ${new Date().toUTCString()}`, 'MIME-Version: 1.0',
    'Content-Type: multipart/related;', '\ttype="text/html";', `\tboundary="${boundary}"`, '', '',
    `--${boundary}`, 'Content-Type: text/html; charset="utf-8"', 'Content-ID: <frame-main@mhtml.blink>',
    'Content-Transfer-Encoding: quoted-printable', '', qp(html), '', `--${boundary}--`, '',
  ].join('\r\n');
  fs.writeFileSync(outPath, mhtml);
  // plain HTML copy for previewing with scripts enabled (git-ignored)
  const o = path.join(__dirname, '../svg-diagrams/out'); fs.mkdirSync(o, { recursive: true });
  fs.writeFileSync(path.join(o, 'mhtml-last.html'), html);
  return mhtml.length;
}

// ---------- page shell (top bar, theme toggle, sidebar fallback, hero slot) ----------
function shell({ title, brand = 'Interview Notes', css = '', nav = '', body, foot = '' }) {
  return `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<style>${theme()}${css}</style></head>
<body>
<div class="app">
<div class="progress"></div>
<div class="topbar"><div class="brand"><span class="logo">◆</span> ${esc(brand)}</div>
<div class="tb-mid">${esc(title)}</div>
<details class="theme-dt"><summary class="theme-btn" title="Toggle light / dark"><span class="sun">☀ Light</span><span class="moon">☾ Dark</span></summary></details></div>
<div class="layout">
<nav class="side"><div class="side-h">On this page</div><ol>${nav}</ol></nav>
<main class="content"><div class="inner">
${body}
${foot ? `<footer class="foot">${foot}</footer>` : ''}
</div></main>
</div></div>
</body></html>
`;
}

// ---------- content helpers ----------
const LANG = { sql: 'SQL', json: 'JSON', java: 'Java', http: 'HTTP', text: 'Text', bash: 'bash', javascript: 'JavaScript', python: 'Python' };
function code(lang, src, label) {
  src = src.replace(/^\n/, '').replace(/\s+$/, '');
  const body = lang !== 'text' && hljs.getLanguage(lang) ? hljs.highlight(src, { language: lang, ignoreIllegals: true }).value : esc(src);
  return `<div class="code"><div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="lang">${esc(label || LANG[lang] || lang)}</span></div><pre><code class="hljs">${body}</code></pre></div>`;
}
// rows: arrays of cells (HTML allowed). hl: set of row indexes to highlight
function table(head, rows, { hl = [] } = {}) {
  return `<div class="tbl"><table><thead><tr>${head.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map((r, i) => `<tr${hl.includes(i) ? ' class="hl"' : ''}>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
// numbered list; item = html | {html, kind:'pro'|'con'}
function nl(items) {
  return `<ol class="nl">${items.map((it, i) => { const o = typeof it === 'string' ? { html: it } : it; return `<li${o.kind ? ` class="${o.kind}"` : ''}><span class="n">${i + 1}</span><div class="li-b"><p>${o.html}</p></div></li>`; }).join('')}</ol>`;
}
const bl = items => `<ul class="bl">${items.map(h => `<li><div class="li-b"><p>${h}</p></div></li>`).join('')}</ul>`;
const callout = (kind, title, html) => `<div class="callout ${kind}"><div class="ct">${title}</div><p>${html}</p></div>`;
const say = html => callout('interview', '💬 Interview line', html);
const endpoint = (m, p) => `<div class="endpoint"><span class="m m-${m.toLowerCase()}">${m}</span><code>${esc(p)}</code></div>`;

// ---------- sequence diagrams (theme-aware: colours come from the page's --sq-* variables) ----------
let seqN = 0;
const tw = s => [...String(s)].reduce((w, ch) => w + (ch === ' ' ? 3.8 : /[A-Z@#%]/.test(ch) ? 8.6 : /[ilj.,:;'|!()[\]{}]/.test(ch) ? 4.2 : /[─→←✓✗×≤≥…•·]/.test(ch) ? 9 : 7.1), 0);
// parts: [{n, s, c}]   steps: ['m', from, to, label, {dash}] | ['note', from, to, text] | ['alt', label] | ['else', label] | ['end']
function seq({ parts, steps, caption, fit = 1000 }) {
  const id = `sqah${++seqN}`, np = parts.length;
  // variable lifeline spacing: each gap gets only the room its own labels and notes need
  const boxW = parts.map(p => Math.max(130, tw(p.n) * 1.02 + 30, tw(p.s || '') * 0.8 + 24));
  const gap = Array.from({ length: np - 1 }, (_, i) => (boxW[i] + boxW[i + 1]) / 2 + 14);
  const ext = { l: boxW[0] / 2, r: boxW[np - 1] / 2 };
  const monoW = l => [...l].length * 7.3;   // action boxes use the 12px monospace font
  const noteW = st => st[0] === 'm' ? Math.max(...String(st[3]).split('\n').map(monoW)) + 52 : Math.max(...String(st[3]).split('\n').map(l => tw(l) * 0.93)) + 28;
  const need = (a, b, w) => {           // lifelines a < b must be at least w apart
    if (a === b) return; let have = 0; for (let i = a; i < b; i++) have += gap[i];
    if (have < w) for (let i = a; i < b; i++) gap[i] += (w - have) / (b - a);
  };
  const ms = steps.filter(st => st[0] === 'm' && st[1] !== st[2]).sort((p, q) => Math.abs(p[2] - p[1]) - Math.abs(q[2] - q[1]));
  for (const st of ms) need(Math.min(st[1], st[2]), Math.max(st[1], st[2]), tw(st[3]) + 56);
  for (const st of steps) {
    if (!(st[0] === 'note' || (st[0] === 'm' && st[1] === st[2]))) continue;
    const lo = Math.min(st[1], st[0] === 'note' ? (st[2] ?? st[1]) : st[1]), hi = Math.max(st[1], st[0] === 'note' ? (st[2] ?? st[1]) : st[1]);
    let span = 0; for (let i = lo; i < hi; i++) span += gap[i];
    const half = Math.max(0, (noteW(st) - span) / 2) + 12;   // how far the note sticks out past lo and hi
    if (lo === 0) ext.l = Math.max(ext.l, half); else need(lo - 1, lo, gap[lo - 1] < half * 2 ? half * 2 : 0);
    if (hi === np - 1) ext.r = Math.max(ext.r, half); else need(hi, hi + 1, gap[hi] < half * 2 ? half * 2 : 0);
  }
  const xs = [20 + ext.l]; gap.forEach(g => xs.push(xs[xs.length - 1] + g));
  const X = i => xs[i], W = Math.ceil(xs[np - 1] + ext.r + 20);
  if (W > fit) console.warn(`  seq: ${W}px wide (fits ${fit}): ${caption || ''}`.slice(0, 160));
  let y = 104, n = 0; const out = [], frames = [];
  for (const st of steps) {
    const k = st[0];
    if (k === 'm' && st[1] !== st[2]) {
      const [, a, b, label, o = {}] = st; n++;
      const dir = b > a ? 1 : -1, x1 = X(a) + dir * 4, x2 = X(b) - dir * 6, mid = (X(a) + X(b)) / 2, lw = tw(label);
      out.push(`<line x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" class="sq-arrow${o.dash ? ' sq-dash' : ''}" marker-end="url(#${id})"/>`);
      const cx = Math.max(Math.min(X(a), X(b)) + 14, mid - lw / 2 - 14);
      out.push(`<circle cx="${cx}" cy="${y - 13}" r="9" class="sq-num"/><text x="${cx}" y="${y - 9}" class="sq-numt" text-anchor="middle">${n}</text>`);
      out.push(`<text x="${mid + 6}" y="${y - 8.5}" class="sq-lbl" text-anchor="middle">${esc(label)}</text>`);
      y += 46;
    } else if (k === 'note' || (k === 'm' && st[1] === st[2])) {
      const self = k === 'm', a = st[1], b = self ? a : (st[2] ?? a), text = self ? st[3] : st[3];
      if (self) n++;
      const lines = String(text).split('\n'), h = 14 + lines.length * 17;
      const lo = Math.min(a, b), hi = Math.max(a, b);
      const wText = self ? Math.max(...lines.map(monoW)) + 30 : Math.max(...lines.map(l => tw(l) * 0.93)) + 28;
      const w = Math.max(wText + (self ? 22 : 0), 120), cxm = (X(lo) + X(hi)) / 2;
      const rx = cxm - w / 2, top = y - 18;
      out.push(`<rect x="${rx}" y="${top}" width="${w}" height="${h}" rx="8" class="${self ? 'sq-act' : 'sq-note'}"/>`);
      if (self) out.push(`<circle cx="${rx + 14}" cy="${top + h / 2}" r="9" class="sq-num"/><text x="${rx + 14}" y="${top + h / 2 + 4}" class="sq-numt" text-anchor="middle">${n}</text>`);
      lines.forEach((l, i) => out.push(`<text x="${self ? rx + 30 : cxm}" y="${top + 21 + i * 17}" class="${self ? 'sq-actt' : 'sq-notet'}" text-anchor="${self ? 'start' : 'middle'}">${esc(l)}</text>`));
      y += h + 22;
    } else if (k === 'alt') {
      frames.push({ top: y - 22, label: st[1], elses: [] }); y += 30;
    } else if (k === 'else') {
      frames[frames.length - 1].elses.push({ y: y - 16, label: st[1] }); y += 32;
    } else if (k === 'end') {
      const f = frames.pop(), d = frames.length * 6, x0 = 12 + d, w = W - 24 - 2 * d, bottom = y - 10;
      const lw = tw(f.label) * 0.86 + 22;
      out.unshift(`<rect x="${x0}" y="${f.top}" width="${w}" height="${bottom - f.top}" rx="6" class="sq-frame"/>` +
        `<path d="M${x0} ${f.top + 6} q0 -6 6 -6 h${lw - 6} v14 l-8 8 h-${lw - 2} z" class="sq-altbox"/><text x="${x0 + 9}" y="${f.top + 15}" class="sq-altt">${esc(f.label)}</text>` +
        f.elses.map(e => `<line x1="${x0}" y1="${e.y}" x2="${x0 + w}" y2="${e.y}" class="sq-alt"/><text x="${x0 + 10}" y="${e.y + 15}" class="sq-altt">[${esc(e.label)}]</text>`).join(''));
      y += 8;
    }
  }
  const H = y + 4;
  const head = parts.map((p, i) => `<line x1="${X(i)}" y1="70" x2="${X(i)}" y2="${H - 8}" class="sq-life"/><rect x="${X(i) - boxW[i] / 2}" y="14" width="${boxW[i]}" height="54" rx="10" fill="${p.c}" class="sq-part"/><text x="${X(i)}" y="${p.s ? 37 : 46}" class="sq-pt" text-anchor="middle">${esc(p.n)}</text>${p.s ? `<text x="${X(i)}" y="56" class="sq-ps" text-anchor="middle">${esc(p.s)}</text>` : ''}`).join('');
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" class="seq" role="img"><defs><marker id="${id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="sq-head"/></marker></defs>${head}${out.join('')}</svg>`;
  return `<figure class="diagram seqfig"><div class="fig-scroll">${svg}</div>${caption ? `<figcaption>${caption}</figcaption>` : ''}</figure>`;
}
const SEQ_CSS = `
.seq .sq-life{stroke:var(--sq-life);stroke-width:1.2;stroke-dasharray:4 5}
.seq .sq-arrow{stroke:var(--sq-line);stroke-width:1.7}
.seq .sq-dash{stroke-dasharray:6 4}
.seq .sq-head{fill:var(--sq-line)}
.seq .sq-lbl{font:500 13px var(--font-sans);fill:var(--sq-text)}
.seq .sq-num{fill:var(--sq-numbg)}
.seq .sq-numt{font:700 10.5px var(--font-sans);fill:#0a0a0a}
.seq .sq-part{stroke:rgba(0,0,0,.18);stroke-width:1}
.seq .sq-pt{font:700 13.5px var(--font-sans);fill:#0a0a0a}
.seq .sq-ps{font:500 10.5px var(--font-sans);fill:#1f1f1f}
.seq .sq-note{fill:var(--sq-notebg);stroke:var(--sq-notebd);stroke-width:1}
.seq .sq-notet{font:500 12px var(--font-sans);fill:var(--sq-notet)}
.seq .sq-act{fill:var(--card2);stroke:var(--pri-bd);stroke-width:1.2}
.seq .sq-actt{font:500 12px var(--font-mono);fill:var(--tx)}
.seq .sq-alt{stroke:var(--sq-altline);stroke-width:1;stroke-dasharray:3 4}
.seq .sq-frame{fill:none;stroke:var(--sq-altline);stroke-width:1}
.seq .sq-altbox{fill:var(--sq-altbg);stroke:var(--sq-altline);stroke-width:1}
.seq .sq-altt{font:600 11.5px var(--font-sans);fill:var(--sq-text)}
`;
const C = { blue: '#74c0fc', teal: '#38d9a9', orange: '#ffa94d', purple: '#b197fc', red: '#ff8787', yellow: '#ffd43b', green: '#8ce99a', pink: '#f783ac', gray: '#ced4da' };

module.exports = { esc, qp, writeMhtml, shell, code, table, nl, bl, callout, say, endpoint, seq, SEQ_CSS, C, theme };
