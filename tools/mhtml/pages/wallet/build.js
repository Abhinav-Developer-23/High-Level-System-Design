// Build HLD_Questions/Wallet_System.mhtml (AlgoMaster-style, same theme as the Airline page).
// usage: node tools/mhtml/pages/wallet/build.js
const path = require('path');
const { shell, writeMhtml, esc, SEQ_CSS } = require('../../lib');
const p1 = require('./part1'), p2 = require('./part2'), p3 = require('./part3');

const TITLE = 'Design a Digital Wallet System';
let body = [p1.hero, p1.questions, p1.requirements, p1.scale, p1.api, p1.model, p2.hld, p2.detailed, p3.deepDives, p3.failures, p3.revision].join('\n');

// counts in the hero come from the page itself
const count = re => (body.match(re) || []).length;
body = body.replace(/🔌 \d+ APIs/, `🔌 ${count(/<div class="endpoint">/g)} APIs`)
  .replace(/🗄 \d+ tables/, `🗄 ${count(/<div class="tbl-title">/g)} tables`)
  .replace(/🧭 \d+ diagrams/, `🧭 ${count(/<figure class="diagram/g)} diagrams`)
  .replace(/🔍 \d+ deep dives/, `🔍 ${count(/class="dd"/g)} deep dives`);

// fallback sidebar (the real one is CSS scroll markers built from data-toc)
const nav = []; let cur = null;
for (const m of body.matchAll(/<(h2|h3)\b[^>]*\bid="([^"]+)"[^>]*\bdata-toc="([^"]+)"/g)) {
  if (m[1] === 'h2') { cur = { id: m[2], label: m[3], kids: [] }; nav.push(cur); }
  else if (cur) cur.kids.push({ id: m[2], label: m[3] });
}
const navHtml = nav.map(t => `<li><a href="#${t.id}" class="l2">${t.label}</a>${t.kids.length ? `<ol>${t.kids.map(k => `<li><a href="#${k.id}">${k.label}</a></li>`).join('')}</ol>` : ''}</li>`).join('');

const css = SEQ_CSS + `
.meta .tag-red{color:#f87171;border-color:rgba(248,113,113,.35);background:rgba(248,113,113,.10);font-weight:700}
.meta .tag-amber{color:#fbbf24;border-color:rgba(251,191,36,.35);background:rgba(251,191,36,.08);font-weight:700}
.app:has(.theme-dt[open]) .meta .tag-red{color:#dc2626}.app:has(.theme-dt[open]) .meta .tag-amber{color:#b45309}
.whatis{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:26px;align-items:center;border:1px solid var(--pri-bd);border-radius:14px;padding:22px 24px;background:linear-gradient(135deg,var(--pri-bg),transparent 70%)}
.whatis h4{margin:0 0 8px;font-size:19px;color:var(--pri2)}
.wi-text p{margin:0 0 10px}
@media (max-width:860px){.whatis{grid-template-columns:1fr}}
.wmock{border:1px solid var(--bd);border-radius:16px;background:var(--card);padding:14px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.wcard{border-radius:12px;padding:16px 18px;background:linear-gradient(135deg,#14532d,#166534 55%,#15803d);color:#ecfdf5}
.wl{font-size:12px;letter-spacing:.06em;text-transform:uppercase;opacity:.8;font-weight:700}
.wb{font-size:30px;font-weight:800;letter-spacing:-.02em;line-height:1.2;margin-top:2px}.wb small{font-size:16px;opacity:.8}
.wsub{font-size:12.5px;opacity:.85;margin-bottom:12px}
.wbtns{display:flex;gap:8px}.wbtns span{flex:1;text-align:center;font-size:12.5px;font-weight:700;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);border-radius:8px;padding:5px 0}
.wtx{margin-top:10px}
.wtx>div{display:flex;align-items:center;gap:10px;padding:8px 4px;border-bottom:1px solid var(--bd);font-size:13.5px}
.wtx>div:last-child{border-bottom:0}
.wtx .ic{flex:none;width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;background:var(--card2);border:1px solid var(--bd)}
.wtx .ic.up{color:var(--pri2)}.wtx .ic.hold{color:var(--warn)}
.wtx .d{flex:1;min-width:0;color:var(--tx2);line-height:1.3}.wtx .d small{display:block;color:var(--mu);font-size:11.5px}
.wtx b{font-weight:700;color:var(--tx);white-space:nowrap}.wtx b.cr{color:var(--pri2)}.wtx b.hd{color:var(--warn)}
.diagram .arch{min-width:900px}
.callout:not(.tip):not(.interview) .ct{color:var(--pri2)}
`;

const html = shell({ title: TITLE, brand: 'HLD Notes', css, nav: navHtml, body,
  foot: `Built by <code>tools/mhtml/pages/wallet/build.js</code> · ${new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}` });
const out = path.join(__dirname, '../../../../HLD_Questions/Wallet_System.mhtml');
const size = writeMhtml(out, html, `${TITLE} | System Design Interview`);
console.log(`wrote ${path.relative(process.cwd(), out)} (${(size / 1e6).toFixed(2)} MB), sections: ${nav.length}, sidebar entries: ${nav.reduce((a, t) => a + 1 + t.kids.length, 0)}`);
