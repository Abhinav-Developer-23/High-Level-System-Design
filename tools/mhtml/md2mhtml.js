// Turn a notes .md into a single-file, AlgoMaster-style .mhtml page (dark by default, light toggle).
// usage: node tools/mhtml/md2mhtml.js <doc.md> <out.mhtml> [--title "..."] [--sub "..."] [--crumbs "A/B/C"] [--link "label|url"]
//
// - Quiz toggles (<details>/<summary> from md-polish/toggles.py) and the doc's <style> block are dropped: just content.
// - The doc's own "Table of Contents" H1 is dropped; the sidebar replaces it.
// - Heading levels shift down one (# topic -> numbered h2, ## -> h3 ...). h2/h3 feed the sidebar.
// - Local images (the dark SVG diagrams) are embedded as data: URIs, so the file is self-contained.
// - No JavaScript: Chrome opens .mhtml sandboxed (no scripts, no #links). The sidebar uses CSS scroll
//   markers and the theme toggle is a <details> element, same as HLD_Questions/Airline_Booking_System.mhtml.
// Needs: npm install in tools/svg-diagrams (markdown-it, highlight.js, markdown-it-github-alerts).
const fs = require('fs'), path = require('path');
const NM = path.join(__dirname, '../svg-diagrams/node_modules');
const MarkdownIt = require(path.join(NM, 'markdown-it'));
const hljs = require(path.join(NM, 'highlight.js'));
const alertsMod = require(path.join(NM, 'markdown-it-github-alerts'));
const alerts = alertsMod.default || alertsMod;

const argv = process.argv.slice(2);
const opt = k => { const i = argv.indexOf(k); return i >= 0 ? argv.splice(i, 2)[1] : undefined; };
const title = opt('--title'), subIn = opt('--sub'), crumbsIn = opt('--crumbs'), linkIn = opt('--link');
const [mdPath, outPath] = argv;
if (!mdPath || !outPath) { console.log('usage: node md2mhtml.js <doc.md> <out.mhtml> [--title ..] [--sub ..] [--crumbs A/B] [--link "label|url"]'); process.exit(1); }
const mdDir = path.dirname(path.resolve(mdPath));

// ---------- 1. clean the markdown ----------
let src = fs.readFileSync(mdPath, 'utf8').replace(/\r\n/g, '\n');
src = src.replace(/^<style>[\s\S]*?^<\/style>\s*/m, '');
{
  const L = src.split('\n'), out = []; let fence = false;
  for (let i = 0; i < L.length; i++) {
    const s = L[i].trim();
    if (s.startsWith('```')) fence = !fence;
    if (!fence) {
      if (s === '<details>' && /^<summary>(Open section|Show answer)<\/summary>$/.test((L[i + 1] || '').trim())) { i++; continue; }
      if (s === '</details>') continue;
    }
    out.push(L[i]);
  }
  src = out.join('\n').replace(/\n{3,}/g, '\n\n');
}
// drop a "Table of Contents" H1 section (up to the next H1 outside code)
{
  const L = src.split('\n'); let fence = false, start = -1, end = -1;
  for (let i = 0; i < L.length; i++) {
    if (L[i].trim().startsWith('```')) { fence = !fence; continue; }
    if (fence || !/^# /.test(L[i])) continue;
    if (start < 0 && /table of contents/i.test(L[i])) start = i;
    else if (start >= 0) { end = i; break; }
  }
  if (start >= 0 && end > start) L.splice(start, end - start);
  src = L.join('\n');
}

// ---------- 2. render ----------
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const md = new MarkdownIt({ html: true, linkify: true, typographer: false }).use(alerts);

const slugs = new Map();
const slug = t => {
  let s = t.toLowerCase().replace(/[^\p{L}\p{M}\p{N}\p{Pc}\- ]/gu, '').replace(/ /g, '-');
  const base = s; let n = slugs.get(base);
  if (n !== undefined) { do { n++; s = `${base}-${n}`; } while (slugs.has(s)); slugs.set(base, n); }
  slugs.set(s, 0); return s;
};
const plain = inline => (inline.children || []).filter(c => c.type === 'text' || c.type === 'code_inline').map(c => c.content).join('');
const clip = (s, n = 52) => s.length > n ? s.slice(0, n - 1).replace(/\s+\S*$/, '') + ' …' : s;

let topicN = 0; const toc = []; const stats = { topics: 0, sections: 0, diagrams: 0, code: 0, tables: 0 };
md.renderer.rules.heading_open = (tokens, i) => {
  const t = tokens[i], lvl = Math.min(6, +t.tag.slice(1) + 1), text = plain(tokens[i + 1]).trim(), id = slug(text);
  t.meta = { lvl };
  let label = text.replace(/^❓\s*/, '');
  if (lvl === 2) { topicN++; stats.topics++; label = `${topicN}. ${label}`; toc.push({ lvl, id, label, kids: [] }); }
  else if (lvl === 3) { stats.sections++; toc.length && toc[toc.length - 1].kids.push({ id, label }); }
  const dt = lvl <= 3 ? ` data-toc="${esc(clip(label))}"` : '';
  const num = lvl === 2 ? `<span class="sec-n">${topicN}.</span> ` : '';
  return `${lvl === 2 ? '</section><section class="sec">' : ''}<h${lvl} id="${id}"${dt}>${num}`;
};
md.renderer.rules.heading_close = (tokens, i) => {
  // find matching open to get shifted level
  let j = i; while (j >= 0 && tokens[j].type !== 'heading_open') j--;
  return `</h${tokens[j].meta.lvl}>\n`;
};
const LANG = { '': 'text', sql: 'SQL', java: 'Java', bash: 'bash', ini: 'ini', json: 'JSON', diff: 'diff', python: 'Python', javascript: 'JavaScript', typescript: 'TypeScript', php: 'PHP', csharp: 'C#' };
md.renderer.rules.fence = (tokens, i) => {
  const t = tokens[i], lang = (t.info || '').trim().split(/\s+/)[0].toLowerCase(); stats.code++;
  const body = lang && hljs.getLanguage(lang) ? hljs.highlight(t.content, { language: lang, ignoreIllegals: true }).value : esc(t.content);
  return `<div class="code"><div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="lang">${esc(LANG[lang] || lang || 'text')}</span></div><pre><code class="hljs">${body.replace(/\n$/, '')}</code></pre></div>\n`;
};
md.renderer.rules.table_open = () => { stats.tables++; return '<div class="tbl"><table>\n'; };
md.renderer.rules.table_close = () => '</table></div>\n';
md.renderer.rules.image = (tokens, i) => {
  const t = tokens[i], srcAttr = t.attrGet('src') || '', alt = t.content || '';
  let url = srcAttr;
  if (!/^(https?:|data:)/.test(srcAttr)) {
    const p = path.resolve(mdDir, decodeURI(srcAttr));
    if (!fs.existsSync(p)) { console.warn('missing image', srcAttr); }
    else {
      const ext = path.extname(p).slice(1).toLowerCase();
      const mime = ext === 'svg' ? 'image/svg+xml' : ext === 'jpg' ? 'image/jpeg' : `image/${ext}`;
      url = `data:${mime};base64,${fs.readFileSync(p).toString('base64')}`; stats.diagrams++;
    }
  }
  return `<img class="fig" src="${url}" alt="${esc(alt)}" title="${esc(alt)}" loading="lazy">`;
};
// paragraphs that hold only an image become a figure
md.core.ruler.push('figures', state => {
  const T = state.tokens;
  for (let i = 0; i + 2 < T.length; i++) {
    if (T[i].type === 'paragraph_open' && T[i + 1].type === 'inline' && T[i + 2].type === 'paragraph_close') {
      const kids = T[i + 1].children.filter(c => !(c.type === 'text' && !c.content.trim()) && c.type !== 'softbreak');
      if (kids.length && kids.every(c => c.type === 'image')) { T[i].tag = T[i + 2].tag = 'figure'; T[i].attrSet('class', 'diagram'); }
    }
  }
});
// links: open external ones in a new tab
const defLink = md.renderer.rules.link_open || ((t, i, o, e, s) => s.renderToken(t, i, o));
md.renderer.rules.link_open = (t, i, o, e, s) => { if (/^https?:/.test(t[i].attrGet('href') || '')) { t[i].attrSet('target', '_blank'); t[i].attrSet('rel', 'noopener'); } return defLink(t, i, o, e, s); };

let body = md.render(src);
// every topic heading closes the previous <section>; the first one closes this opener (empty sections are harmless)
body = '<section class="sec">' + body + '</section>';

// ---------- 3. page ----------
const docTitle = title || path.basename(mdPath, '.md');
const crumbs = (crumbsIn || `Notes/${path.basename(mdDir)}/${path.basename(mdPath, '.md')}`).split('/').map(esc).join('<span>›</span>');
const sub = subIn ? `<p class="sub">${esc(subIn)}</p>` : '';
const [linkLabel, linkUrl] = (linkIn || '').split('|');
const navHtml = toc.map(t => `<li><a href="#${t.id}" class="l2">${esc(t.label)}</a>${t.kids.length ? `<ol>${t.kids.map(k => `<li><a href="#${k.id}">${esc(clip(k.label))}</a></li>`).join('')}</ol>` : ''}</li>`).join('');
const topicChips = toc.map(t => `<span>${esc(clip(t.label.replace(/^\d+\.\s*/, ''), 34))}</span>`).join('');
const today = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
const css = fs.readFileSync(path.join(__dirname, 'theme.css'), 'utf8');

const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(docTitle)}</title>
<style>${css}</style></head>
<body>
<div class="app">
<div class="progress"></div>
<div class="topbar"><div class="brand"><span class="logo">◆</span> Interview Notes</div>
<div class="tb-mid">${esc(docTitle)}</div>
<details class="theme-dt"><summary class="theme-btn" title="Toggle light / dark"><span class="sun">☀ Light</span><span class="moon">☾ Dark</span></summary></details></div>
<div class="layout">
<nav class="side"><div class="side-h">On this page</div><ol>${navHtml}</ol></nav>
<main class="content"><div class="inner md">
<header class="hero">
<div class="crumbs">${crumbs}</div>
<h1>${esc(docTitle)}</h1>
${sub}
<div class="meta"><span>${stats.topics} topics</span><span>${stats.sections} sections</span><span>${stats.diagrams} diagrams</span><span>${stats.code} code blocks</span><span>${stats.tables} tables</span></div>
<div class="intro"><h4>What's inside</h4><div class="chips">${topicChips}</div>${linkUrl ? `<p class="intro-link">🗺️ <a href="${esc(linkUrl)}" target="_blank" rel="noopener">${esc(linkLabel)}</a></p>` : ''}</div>
</header>
${body}
<footer class="foot">Generated from <code>${esc(path.relative(process.cwd(), path.resolve(mdPath)).replace(/\\/g, '/'))}</code> · ${today}</footer>
</div></main>
</div></div>
</body></html>
`;

// ---------- 4. wrap as MHTML ----------
const size = require('./lib').writeMhtml(outPath, html, docTitle);
console.log(`wrote ${outPath} (${(size / 1e6).toFixed(2)} MB):`, stats);
