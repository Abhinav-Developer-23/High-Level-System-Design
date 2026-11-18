// Small page-structure helpers (numbered sections, cards, deep-dive headings) for AlgoMaster-style pages.
const { esc } = require('../../lib');
const used = new Map();
const slug = t => {
  let s = t.toLowerCase().replace(/<[^>]+>/g, '').replace(/&[a-z]+;/g, '').replace(/[^\p{L}\p{N}\- ]/gu, '').trim().replace(/\s+/g, '-');
  const n = used.get(s) || 0; used.set(s, n + 1); return n ? `${s}-${n}` : s;
};
const plain = h => h.replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
const clip = (s, n = 50) => s.length > n ? s.slice(0, n - 1).replace(/\s+\S*$/, '') + ' …' : s;
let sec = 0;
const H2 = (title, toc) => { sec++; return `<h2 id="${slug(title)}" data-toc="${esc(`${sec}. ${toc || plain(title)}`)}"><span class="sec-n">${sec}.</span> ${title}</h2>`; };
const H3 = (title, toc) => `<h3 id="${slug(plain(title))}" data-toc="${esc(clip(toc || plain(title)))}">${title}</h3>`;
const card = (n, title, html) => `<div class="card"><h3 id="${slug(plain(title))}"><span class="qn">${n}</span>${title}</h3><p>${html}</p></div>`;
const qcard = (n, q, why, ans) => `<div class="card"><h3 id="${slug(plain(q))}" data-toc="${esc(clip(`${n}. ${plain(q)}`))}"><span class="qn">Q${n}</span>${q}</h3><div class="qa why"><span class="qa-l">Why ask</span><p>${why}</p></div><div class="qa ans"><span class="qa-l">Interviewer answer</span><p>${ans}</p></div></div>`;
const DD = (n, q, toc) => `<h3 id="${slug(`deep dive ${n} ${plain(q)}`)}" class="dd" data-toc="${esc(clip(`Deep Dive ${n}: ${toc || plain(q)}`))}"><span class="dd-n">Deep Dive ${n}</span><span class="dd-q">${q}</span></h3>`;
const approach = (n, title, src) => `<h4 class="approach"><span class="ap-tag">${typeof n === 'number' ? `Approach ${n}` : n}</span>${title}${src ? ` <span class="ap-src">${src}</span>` : ''}</h4>`;
module.exports = { slug, H2, H3, card, qcard, DD, approach };
