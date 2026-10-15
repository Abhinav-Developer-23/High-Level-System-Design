// Preview a markdown file roughly as MarkView (dark) renders it, as a PNG.
// usage: node tools/svg-diagrams/preview.js <doc.md> [startLine endLine]
//   -> out/preview.html + out/preview.png  (keeps the doc's <style> block when previewing a line range)
// Needs: npm install (in this folder), Windows Chrome, and MarkView installed in Chrome (its content.css is reused).
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const MarkdownIt = require('markdown-it');
const hljs = require('highlight.js');
const alerts = require('markdown-it-github-alerts').default || require('markdown-it-github-alerts');
const [, , mdPath, a, b] = process.argv;
if (!mdPath) { console.log('usage: node preview.js <doc.md> [startLine endLine]'); process.exit(1); }
const OUT = path.join(__dirname, 'out'); fs.mkdirSync(OUT, { recursive: true });
const CHROME = '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe';
const toWin = p => 'C:\\' + path.resolve(p).replace(/^\/mnt\/c\//, '').replace(/\//g, '\\');
const toUrl = p => 'file:///' + toWin(p).replace(/\\/g, '/');

// MarkView's own stylesheet from the installed extension (any version / profile)
const extRoot = '/mnt/c/Users';
let css = '';
for (const user of fs.readdirSync(extRoot)) {
  const base = path.join(extRoot, user, 'AppData/Local/Google/Chrome/User Data');
  if (!fs.existsSync(base)) continue;
  for (const prof of fs.readdirSync(base)) {
    const ext = path.join(base, prof, 'Extensions/cfopbpknalachedpcddhgbgjoigklien');
    if (!fs.existsSync(ext)) continue;
    const v = fs.readdirSync(ext).sort().pop(); const c = path.join(ext, v, 'css/content.css');
    if (fs.existsSync(c)) css = c;
  }
}
if (!css) console.warn('MarkView CSS not found; preview will be unstyled');

let src = fs.readFileSync(mdPath, 'utf8');
if (a) { const L = src.split('\n'); const st = src.match(/<style>[\s\S]*?<\/style>/); src = (st ? st[0] + '\n\n' : '') + L.slice(+a - 1, +b).join('\n'); }
const html = new MarkdownIt({ html: true, linkify: true, typographer: true, highlight: (code, lang) => (lang && hljs.getLanguage(lang)) ? `<pre><code class="hljs language-${lang}">${hljs.highlight(code, { language: lang }).value}</code></pre>` : '' }).use(alerts).render(src);
const page = path.join(OUT, 'preview.html');
fs.writeFileSync(page, `<!doctype html><html class="markview-active markview-dark"><head><meta charset="utf-8">
<base href="${toUrl(path.dirname(mdPath))}/">${css ? `<link rel="stylesheet" href="${toUrl(css)}">` : ''}</head>
<body><div id="markview-container" class="markview-dark">${html}</div></body></html>`);
const lines = src.split('\n').length, height = Math.min(16000, Math.max(800, lines * 26));
execFileSync(CHROME, ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
  '--virtual-time-budget=5000', `--window-size=1000,${height}`, `--screenshot=${toWin(path.join(OUT, 'preview.png'))}`, toUrl(page)], { stdio: 'ignore' });
console.log('wrote', path.join(OUT, 'preview.png'));
