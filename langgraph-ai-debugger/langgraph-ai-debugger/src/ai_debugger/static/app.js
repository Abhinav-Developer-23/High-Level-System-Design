// AI Debugger UI: streams the LangGraph run (SSE) and paints every node, tool call and token.
//
// No framework, no build step: plain DOM calls via the tiny `h()` helper below.
// Reading order:
//   1. `boot()` at the very bottom — loads /api/config, threads, MCP list.
//   2. `send()` — POSTs /api/chat and reads the SSE stream chunk by chunk.
//   3. `handle(ev)` — one `case` per event type; this is where every server event lands.
//   4. The panels it updates: graph view (renderGraph/paintGraph), trace, tools, MCP, NPCI, run.
// Event types come from server.py (thread, node_start, node_end, final, error, done) and from
// llm.py / graph.py via the "custom" stream (triage, agent_start, text_delta, tool_use, tool_result, …).
//
// JavaScript crash course for this file (if you only know a little Python):
//   const x = 1 / let y = 2   — variables; `const` can't be reassigned, `let` can (Python: x = 1)
//   (a, b) => a + b           — an arrow function (Python: lambda a, b: a + b)
//   `hi ${name}`              — template string (Python f-string: f"hi {name}")
//   {a: 1, b: 2}              — object, used like a Python dict; read with obj.a or obj["a"]
//   [...list]                 — copy/spread a list (Python: [*list]); {...obj} spreads an object
//   a ?? b                    — b only if a is null/undefined (Python's `a or b`, but 0/"" are kept)
//   x?.y                      — x.y, or undefined if x is null (no crash)
//   === / !==                 — strict equal / not equal (always use these, not == / !=)
//   async/await               — same idea as in Python
//   document / DOM            — the page's elements as JS objects; changing them changes the page
//   el.addEventListener("click", fn) — run fn when the element is clicked
//   fetch(url, opts)          — make an HTTP request to our FastAPI server (server.py)

// $ / $$ = querySelector shorthands; h(tag, attrs, ...children) builds a DOM element.
//   $("#input")  → the element with id="input" (CSS selector syntax: # = id, . = class)
//   h("div", {class: "card", text: "hello"})  → <div class="card">hello</div>
//   h("button", {onclick: fn}, "Go")           → a button that calls fn when clicked
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const h = (tag, attrs = {}, ...kids) => {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") el.className = v;
    else if (k === "text") el.textContent = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v !== undefined && v !== null && v !== false) el.setAttribute(k, v);
  }
  for (const kid of kids.flat()) if (kid != null) el.append(kid.nodeType ? kid : document.createTextNode(kid));
  return el;
};

const ICONS = { triage: "🧭", clarify: "❓", npci: "🔣", plan: "🗺️", investigate: "🔬", compact: "🗜️", agent: "🤖", tools: "🛠️", ask_user: "🙋", npci_enrich: "🧬", review: "⚖️", report: "📜" };
const QUICK = [
  ["🔎 Debug a TSP txn", "tsp: debug txn PTM… — why is it DEEMED?"],
  ["🚨 Latest Zenduty incidents", "tsp: what fired on Zenduty for tsp-txn in the last 6h and why?"],
  ["📈 TPAP SR right now", "tpap: what is the UPI success rate per payer PSP in the last 1h, and is anything dipping?"],
  ["🐬 DB health", "tsp: is the C3 switch master MySQL healthy right now? connections, lag, slow queries"],
  ["🔣 What is ZM?", "what does NPCI code ZM mean?"],
  ["📮 PaytmCaller pages", "tpap: which PaytmCaller alerts fired today? check the mail first"],
];

// All page state lives here.
//   thread   — id of the open thread (null = new conversation)
//   running  — a /api/chat stream is open; blocks a second send
//   graph    — {nodes, edges} from /api/config, drawn by renderGraph()
//   tools    — tool_use id → its card in the Tools tab, so tool_result can fill it in
//   mcp      — rows for the MCP tab; selected = Set of server names ticked (null = defaults)
//   liveMsg  — the "typing" bubble shown while a run streams; replaced by the final report
const S = {
  thread: null, running: false, abort: null, graph: null, tools: new Map(),
  cost: 0, toolCount: 0, mcp: [], liveMsg: null, selected: null,
};

// ───────────────────────── markdown (escape first, then format) ─────────────────────────
// A small hand-rolled renderer for the agent's reports: headings, lists, tables, code, quotes,
// links. Everything is HTML-escaped before formatting, so model output can't inject markup.
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
function inline(s) {
  const codes = [];
  s = s.replace(/`([^`]+)`/g, (_, c) => { codes.push(c); return `\u0000${codes.length - 1}\u0000`; });
  s = esc(s)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>")
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${esc(codes[+i])}</code>`);
}
function md(src) {
  const lines = String(src || "").replace(/\r/g, "").split("\n");
  const out = [];
  let i = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (/^```/.test(l)) {
      const buf = []; i++;
      while (i < lines.length && !/^```/.test(lines[i])) buf.push(lines[i++]);
      i++; out.push(`<pre><code>${esc(buf.join("\n"))}</code></pre>`); continue;
    }
    if (/^\s*\|.*\|\s*$/.test(l) && i + 1 < lines.length && /^\s*\|?\s*:?-{2,}/.test(lines[i + 1])) {
      const row = (r) => r.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      const head = row(l); i += 2; const body = [];
      while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) body.push(row(lines[i++]));
      out.push(`<table><thead><tr>${head.map((c) => `<th>${inline(c)}</th>`).join("")}</tr></thead><tbody>${body.map((r) => `<tr>${r.map((c) => `<td>${inline(c)}</td>`).join("")}</tr>`).join("")}</tbody></table>`);
      continue;
    }
    let m;
    if ((m = l.match(/^(#{1,4})\s+(.*)$/))) { out.push(`<h${Math.min(m[1].length + 1, 4)}>${inline(m[2])}</h${Math.min(m[1].length + 1, 4)}>`); i++; continue; }
    if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(l)) { out.push("<hr>"); i++; continue; }
    if (/^>\s?/.test(l)) {
      const buf = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) buf.push(lines[i++].replace(/^>\s?/, ""));
      out.push(`<blockquote>${md(buf.join("\n"))}</blockquote>`); continue;
    }
    if (/^\s*([-*+]|\d+[.)])\s+/.test(l)) {
      const ordered = /^\s*\d/.test(l); const items = [];
      while (i < lines.length && /^\s*([-*+]|\d+[.)])\s+/.test(lines[i])) {
        let item = lines[i++].replace(/^\s*([-*+]|\d+[.)])\s+/, "");
        while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !/^\s*([-*+]|\d+[.)])\s+/.test(lines[i])) item += " " + lines[i++].trim();
        items.push(`<li>${inline(item)}</li>`);
      }
      out.push(`<${ordered ? "ol" : "ul"}>${items.join("")}</${ordered ? "ol" : "ul"}>`); continue;
    }
    if (!l.trim()) { i++; continue; }
    const buf = [l]; i++;
    while (i < lines.length && lines[i].trim() && !/^(#{1,4}\s|```|>|\s*([-*+]|\d+[.)])\s+|\s*\|)/.test(lines[i])) buf.push(lines[i++]);
    out.push(`<p>${inline(buf.join(" "))}</p>`);
  }
  return out.join("\n");
}

// ───────────────────────── api ─────────────────────────
// Call one of server.py's JSON endpoints, e.g. `await api("/api/threads")` → {threads: [...]}.
// Throws an error for any non-2xx HTTP status so callers can catch it.
const api = async (path, opts = {}) => {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
};

// ───────────────────────── live LangGraph view + trace route ─────────────────────────
// The SVG pipeline diagram. Node positions are hard-coded in POS; edges come from the server.
// G.turns holds one entry per user message: the list of nodes visited, with status and timing.
// paintGraph() colours the diagram for the selected turn (G.view, null = latest).
const START = "__start__", END = "__end__";
// [x, y] centre of each node box in the SVG
const POS = {
  __start__: [200, 22], triage: [200, 80], clarify: [72, 148], npci: [200, 148], plan: [322, 214],
  investigate: [200, 280], compact: [334, 280], agent: [200, 346], tools: [334, 346], ask_user: [330, 412],
  npci_enrich: [200, 412], review: [322, 478], report: [200, 544], __end__: [200, 610],
};
// edges that would cut through other nodes are bent out to this x
const VIA = { "npci>report": 96, "clarify>__end__": 30, "ask_user>__end__": 396 };
// box sizes: normal node (NW×NH) and the small __start__/__end__ pills (TW×TH)
const NW = 116, NH = 36, TW = 84, TH = 24;
const G = { edges: [], cond: new Set(), turns: [], view: null, timer: null };
const SVGNS = "http://www.w3.org/2000/svg";
const sv = (tag, attrs = {}, text) => {
  const el = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  if (text != null) el.textContent = text;
  return el;
};
const dims = (id) => (id.startsWith("__") ? [TW, TH] : [NW, NH]);
function fmtMs(ms) {
  if (ms == null) return "";
  if (ms < 1000) return `${Math.round(ms)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.floor(ms / 60000)}m ${Math.round((ms % 60000) / 1000)}s`;
}
// SVG path for edge a→b: a curve down to the next node, a loop out to the right when the
// edge goes back up (review → investigate), or two parallel lines for a side-by-side pair
// (agent ⇄ tools: the call goes along the top, the result comes back along the bottom).
function edgePath(a, b) {
  const [ax, ay] = POS[a], [bx, by] = POS[b], [aw, ah] = dims(a), [bw, bh] = dims(b);
  if (by === ay) {
    const dir = bx > ax ? 1 : -1, dy = dir > 0 ? -7 : 7;
    return `M${ax + dir * aw / 2},${ay + dy} L${bx - dir * bw / 2},${by + dy}`;
  }
  if (by < ay) {
    const sx = ax + aw / 2, ex = bx + bw / 2, cx = Math.min(396, Math.max(sx, ex) + 16);
    return `M${sx},${ay} C${cx},${ay} ${cx},${by} ${ex},${by}`;
  }
  const sy = ay + ah / 2, ey = by - bh / 2, via = VIA[`${a}>${b}`];
  if (via != null) return `M${ax},${sy} C${via},${sy + 70} ${via},${ey - 70} ${bx},${ey}`;
  const k = Math.max(16, (ey - sy) * 0.45);
  return `M${ax},${sy} C${ax},${sy + k} ${bx},${ey - k} ${bx},${ey}`;
}
function renderGraph() {
  const svg = $("#graphSvg"); svg.innerHTML = "";
  const edges = [[START, "triage"], ...(S.graph?.edges || []), ["clarify", END], ["ask_user", END], ["report", END]].filter(([a, b]) => POS[a] && POS[b]);
  const out = {}; for (const [a] of edges) out[a] = (out[a] || 0) + 1;
  G.edges = edges; G.cond = new Set(Object.keys(out).filter((k) => out[k] > 1));
  const defs = sv("defs");
  for (const v of ["idle", "route", "flow"]) {
    const m = sv("marker", { id: `ah-${v}`, viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" });
    m.append(sv("path", { d: "M0,0 L10,5 L0,10 z", class: `ah ${v}` })); defs.append(m);
  }
  svg.append(defs);
  for (const [a, b] of edges) svg.append(sv("path", { d: edgePath(a, b), class: `edge${G.cond.has(a) ? " cond" : ""}`, "data-e": `${a}>${b}`, "marker-end": "url(#ah-idle)" }));
  const llm = new Set((S.graph?.nodes || []).filter((n) => n.llm).map((n) => n.id));
  for (const id of Object.keys(POS)) {
    const [x, y] = POS[id], [w, hh] = dims(id), term = id.startsWith("__");
    const g = sv("g", { class: `gnode${term ? " term" : ""}`, "data-n": id, transform: `translate(${x},${y})` });
    g.append(sv("title", {}, term ? id : `${id}${llm.has(id) ? " — Claude via the Anthropic API" : id === "tools" ? " — ToolNode: runs the model's tool calls" : " — pure Python"}`));
    g.append(sv("rect", { x: -w / 2, y: -hh / 2, width: w, height: hh, rx: term ? hh / 2 : 8 }));
    g.append(sv("text", { y: term ? 0 : -6 }, term ? id.replace(/__/g, "") : id));
    if (!term) g.append(sv("text", { class: "sub", y: 9 }, ""));
    if (llm.has(id)) {
      g.append(sv("rect", { class: "opus", x: w / 2 - 32, y: -hh / 2 - 7, width: 30, height: 12, rx: 3 }));
      g.append(sv("text", { class: "opus-t", x: w / 2 - 17, y: -hh / 2 - 1 }, "LLM"));
    }
    svg.append(g);
  }
  paintGraph();
}
const curTurn = () => G.turns[G.view ?? G.turns.length - 1];
const liveTurn = () => { const t = G.turns[G.turns.length - 1]; return t?.live ? t : null; };
// The node sequence a turn took, with __start__ (and __end__ once finished) added.
function routeOf(t) {
  if (!t?.steps.length) return [];
  const seq = [START, ...t.steps.map((s) => s.node)];
  const last = t.steps[t.steps.length - 1];
  if (!t.live && last.status === "done" && (last.node === "report" || last.node === "clarify" || last.node === "ask_user")) seq.push(END);
  return seq;
}
const elapsed = (st) => (st.t0 ? performance.now() - st.t0 : null);
function paintGraph() {
  const t = curTurn(), steps = t?.steps || [], seq = routeOf(t);
  const route = new Set(); for (let i = 1; i < seq.length; i++) route.add(`${seq[i - 1]}>${seq[i]}`);
  const last = steps[steps.length - 1];
  const flowE = t?.live && last?.status === "active" && seq.length > 1 ? `${seq[seq.length - 2]}>${seq[seq.length - 1]}` : null;
  $$("#graphSvg .edge").forEach((e) => {
    const k = e.dataset.e, f = k === flowE, r = !f && route.has(k);
    e.classList.toggle("flow", f); e.classList.toggle("route", r);
    e.setAttribute("marker-end", `url(#ah-${f ? "flow" : r ? "route" : "idle"})`);
  });
  const finished = t && !t.live && steps.length;
  $$("#graphSvg .gnode").forEach((g) => {
    const id = g.dataset.n, mine = steps.filter((s) => s.node === id), ls = mine[mine.length - 1];
    const visited = mine.length > 0 || (id === START && steps.length > 0) || (id === END && seq.includes(END));
    g.classList.toggle("active", ls?.status === "active");
    g.classList.toggle("error", ls?.status === "error");
    g.classList.toggle("done", visited && ls?.status !== "active" && ls?.status !== "error");
    g.classList.toggle("skipped", Boolean(finished) && !visited);
    const sub = $(".sub", g);
    if (sub) {
      const total = mine.reduce((a, s) => a + (s.status === "active" ? elapsed(s) || 0 : s.ms || 0), 0);
      sub.textContent = !mine.length ? "" : ls.status === "active" ? `running ${fmtMs(total)}` : fmtMs(total);
    }
    $$(".vb", g).forEach((b) => b.remove());
    if (mine.length > 1) {
      const [w, hh] = dims(id);
      g.append(sv("circle", { class: "visits vb", cx: -w / 2 + 2, cy: -hh / 2 + 1, r: 9 }));
      g.append(sv("text", { class: "visits-t vb", x: -w / 2 + 2, y: -hh / 2 + 1 }, `×${mine.length}`));
    }
  });
  const lt = liveTurn(), act = lt?.steps.filter((s) => s.status === "active").pop();
  const chip = $("#statNode"); chip.textContent = act ? `${act.node} · ${fmtMs(elapsed(act))}` : "idle"; chip.classList.toggle("live", Boolean(act));
}
function renderTrace() {
  const box = $("#trace"); box.innerHTML = "";
  if (!G.turns.length) { box.append(h("div", { class: "empty", text: "The route through the graph shows up here, step by step." })); $("#traceNote").textContent = ""; return; }
  const view = G.view ?? G.turns.length - 1;
  G.turns.forEach((t, i) => {
    const total = t.steps.reduce((a, s) => a + (s.status === "active" ? elapsed(s) || 0 : s.ms || 0), 0);
    box.append(h("div", { class: `turn-h${i === view ? " on" : ""}`, title: "show this turn's route on the graph", onclick: () => { G.view = i === G.turns.length - 1 ? null : i; paintGraph(); renderTrace(); } },
      h("span", { text: `Turn ${t.turn}${t.live ? " · live" : ""}` }), h("span", { text: `${t.steps.length} steps · ${fmtMs(total)}` })));
    if (i !== view) return;
    t.steps.forEach((st, j) => box.append(h("div", { class: `step ${st.status}` },
      h("span", { class: "n", text: String(j + 1) }),
      h("span", { class: "nm" }, st.node, st.note ? h("small", { text: st.note }) : null),
      h("span", { class: "ms", text: st.status === "active" ? `${fmtMs(elapsed(st))}…` : fmtMs(st.ms) }))));
    const seq = routeOf(t);
    if (seq.length > 1) box.append(h("div", { class: "route-line", text: seq.map((n) => n.replace(/__/g, "")).join(" → ") }));
  });
  $("#traceNote").textContent = G.turns.length > 1 ? "click a turn to replay its route" : "";
}
function paintAll() { paintGraph(); renderTrace(); }
// Live trace updates, driven by node_start / node_end events. The 1s timer keeps the
// "running 12.3s" counters ticking while a node is busy.
function traceStartTurn() {
  G.turns.push({ turn: (G.turns[G.turns.length - 1]?.turn || 0) + 1, steps: [], live: true });
  G.view = null; clearInterval(G.timer); G.timer = setInterval(paintAll, 1000); paintAll();
}
function traceNodeStart(node) {
  const t = liveTurn(); if (!t) return;
  t.steps.push({ node, status: "active", t0: performance.now() }); paintAll();
}
function runNote(r) { return r ? `${r.tool_calls || 0} tools · $${(r.cost_usd || 0).toFixed(2)}` : ""; }
function traceNodeEnd(ev) {
  const t = liveTurn(); if (!t) return;
  const st = [...t.steps].reverse().find((s) => s.node === ev.node && s.status === "active"); if (!st) return;
  st.status = ev.error ? "error" : "done"; st.ms = elapsed(st); st.t0 = null;
  if (ev.node === "triage") st.note = `${ev.system || "system?"} · ${ev.intent || ""}`;
  else if (ev.node === "review" && ev.review) st.note = `${ev.review.verdict}${ev.review.score != null ? ` ${ev.review.score}/10` : ""} · ${runNote(ev.run)}`;
  else if (ev.run) st.note = runNote(ev.run);
  paintAll();
}
function traceEnd(failed) {
  const t = liveTurn(); clearInterval(G.timer); G.timer = null;
  if (!t) return;
  for (const s of t.steps) if (s.status === "active") { s.status = failed ? "error" : "done"; s.ms = elapsed(s); s.t0 = null; }
  t.live = false; paintAll();
}
function traceReset() { clearInterval(G.timer); G.timer = null; G.turns = []; G.view = null; paintAll(); }
// Rebuild the trace of a saved thread from /api/threads/<id>/trace (checkpoint history),
// matching each LLM step to its entry in state.runs to show tools/cost.
async function traceLoad(id, v) {
  try {
    const { steps } = await api(`/api/threads/${id}/trace`);
    const queue = [...(v.runs || [])], turns = new Map();
    for (const s of steps) {
      if (!turns.has(s.turn)) turns.set(s.turn, { turn: s.turn, steps: [], live: false });
      const st = { node: s.node, ms: s.ms, status: s.done ? "done" : "error" };
      if (queue[0]?.node === s.node) {
        const r = queue.shift();
        const rv = v.review;
        st.note = s.node === "review" && rv && !queue.some((q) => q.node === "review")
          ? `${rv.verdict}${rv.score != null ? ` ${rv.score}/10` : ""} · ${runNote(r)}` : runNote(r);
      }
      turns.get(s.turn).steps.push(st);
    }
    G.turns = [...turns.values()].filter((t) => t.steps.length); G.view = null;
  } catch (e) { console.error(e); G.turns = []; }
  paintAll();
}

// ───────────────────────── chat rendering ─────────────────────────
function hideHero() { $("#hero")?.classList.add("hidden"); }
function scrollChat() { const c = $("#chat"); c.scrollTop = c.scrollHeight; }
function addUser(text) {
  hideHero();
  $("#chat").append(h("div", { class: "msg user" }, h("div", { class: "bubble", text })));
  scrollChat();
}
function addBot(html, meta = {}) {
  hideHero();
  const body = h("div", { class: "md" }); body.innerHTML = html;
  const bubble = h("div", { class: "bubble" }, body);
  if (meta.pills?.length) {
    const foot = h("div", { class: "bot-foot" }, meta.pills.map(([t, c]) => h("span", { class: `pill ${c || ""}`, text: t })));
    foot.append(h("button", { class: "copy-btn", text: "copy", onclick: (e) => { navigator.clipboard.writeText(meta.raw || body.innerText); e.target.textContent = "copied ✓"; } }));
    bubble.append(foot);
  }
  const m = h("div", { class: "msg bot" }, h("div", { class: "avatar", text: "◭" }), bubble);
  $("#chat").append(m); scrollChat(); return m;
}
// The temporary bubble shown during a run: status line, collapsible thinking, streamed text.
function startLive() {
  hideHero();
  const status = h("div", { class: "status-line" }, h("span", { class: "spark" }), h("span", { class: "st-text", text: "Starting the graph…" }));
  const think = h("details", { class: "thinkbox hidden" }, h("summary", { text: "thinking" }), h("div", { class: "think" }));
  const text = h("div", { class: "live-text cursor" });
  const bubble = h("div", { class: "bubble" }, status, think, text);
  const m = h("div", { class: "msg bot live" }, h("div", { class: "avatar", text: "◭" }), bubble);
  $("#chat").append(m); scrollChat();
  S.liveMsg = { m, status: $(".st-text", status), think, thinkBody: $(".think", think), text };
}
function liveStatus(t) { if (S.liveMsg) S.liveMsg.status.textContent = t; }
function endLive() { if (S.liveMsg) { S.liveMsg.m.remove(); S.liveMsg = null; } }

// ───────────────────────── tools panel ─────────────────────────
// One card per tool call: created on tool_use, completed on tool_result (matched by id).
// "mcp__tsp_redash__run_sql" → server "tsp_redash", tool "run_sql", system "tsp".
function splitTool(name) {
  const m = name.match(/^mcp__(.+?)__(.+)$/);
  if (!m) return { server: "builtin", tool: name, sys: "builtin" };
  const sys = m[1].startsWith("tpap") ? "tpap" : m[1].startsWith("tsp") ? "tsp" : "shared";
  return { server: m[1], tool: m[2], sys };
}
function fmtInput(input) {
  if (input == null) return "";
  if (typeof input === "string") return input;
  if (input.command) return `$ ${input.command}`;
  for (const k of ["query", "sql", "expr", "promql", "kql", "q", "pattern"]) if (typeof input[k] === "string") return `${k}: ${input[k]}\n${JSON.stringify(Object.fromEntries(Object.entries(input).filter(([kk]) => kk !== k)))}`;
  return JSON.stringify(input, null, 1);
}
function addTool(ev) {
  $("#toolsEmpty").classList.add("hidden");
  const { server, tool, sys } = splitTool(ev.name || "?");
  const card = $("#tplTool").content.firstElementChild.cloneNode(true);
  card.classList.add(sys, "pending");
  $(".srv", card).textContent = server; $(".tname", card).textContent = tool;
  $(".tms", card).textContent = ev.node || "";
  $(".tin", card).textContent = fmtInput(ev.input);
  if (ev.parent) card.prepend(h("div", { class: "sub", text: "↳ subagent" }));
  card.addEventListener("click", () => card.classList.toggle("open"));
  $("#toolList").prepend(card);
  S.tools.set(ev.id, card);
  S.toolCount++; $("#toolCount").textContent = S.toolCount; $("#statTools").textContent = `${S.toolCount} tools`;
  liveStatus(`Calling ${tool} on ${server}…`);
}
function toolResult(ev) {
  const card = S.tools.get(ev.id); if (!card) return;
  card.classList.remove("pending"); if (ev.is_error) card.classList.add("err");
  $(".tms", card).textContent = ev.ms != null ? `${ev.ms}ms · ${ev.chars}ch` : `${ev.chars}ch`;
  const out = $(".tout", card); out.classList.remove("hidden"); out.textContent = ev.preview || "";
}
// Re-draw the tools panel from state.tool_log when an old thread is opened.
function loadToolLog(log = []) {
  $("#toolList").innerHTML = ""; S.tools.clear(); S.toolCount = 0;
  $("#toolsEmpty").classList.toggle("hidden", log.length > 0);
  for (const t of log) {
    const id = Math.random().toString(36).slice(2);
    let input; try { input = JSON.parse(t.input); } catch { input = t.input; }
    addTool({ id, name: t.name, input, node: t.node });
    toolResult({ id, is_error: t.is_error, ms: t.ms, chars: t.chars, preview: t.preview });
  }
}

// ───────────────────────── MCP panel ─────────────────────────
// Lists servers from /api/mcp. Ticking boxes sets S.selected, which send() passes as
// options.servers so the next run only gets those servers.
async function loadMcp() {
  const { servers } = await api("/api/mcp");
  S.mcp = servers; renderMcp();
}
function renderMcp() {
  const list = $("#mcpList"); list.innerHTML = "";
  const groups = { tpap: "TPAP", tsp: "TSP", shared: "Shared" };
  for (const [g, label] of Object.entries(groups)) {
    const rows = S.mcp.filter((s) => s.system === g); if (!rows.length) continue;
    list.append(h("div", { class: "mcp-group" }, h("span", { class: `sys-badge ${g}`, text: label }), ` ${rows.length} servers`));
    for (const s of rows) {
      const p = s.probe;
      const dotCls = s.probing ? "probing" : p ? (p.ok ? "ok" : "bad") : "";
      const enabled = !s.disabled && (S.selected ? S.selected.has(s.name) : !s.default_off);
      const cb = h("input", { type: "checkbox", title: "use in the next run", ...(enabled ? { checked: "" } : {}), ...(s.disabled ? { disabled: "" } : {}) });
      cb.addEventListener("change", () => toggleServer(s.name, cb.checked));
      const row = h("div", { class: `mcp${enabled ? "" : " off"}` },
        h("span", { class: `dot ${dotCls}` }), h("span", { class: "m-name", text: s.name }),
        h("span", { class: "m-tools" }, p?.ok ? `${p.tools.length} tools ` : "", cb),
        h("span", { class: "m-label", text: s.label + (s.deny.length ? ` · ${s.deny.length} write tools blocked` : "") }));
      if (s.missing_env?.length) row.append(h("span", { class: "m-err", text: `.env missing: ${s.missing_env.join(", ")}` }));
      if (p && !p.ok) row.append(h("span", { class: "m-err", text: p.error }));
      list.append(row);
    }
  }
  const ok = S.mcp.filter((s) => s.probe?.ok).length;
  $("#mcpCount").textContent = ok ? `${ok}/${S.mcp.length}` : S.mcp.length;
}
function toggleServer(name, on) {
  if (!S.selected) S.selected = new Set(S.mcp.filter((s) => !s.disabled && !s.default_off).map((s) => s.name));
  on ? S.selected.add(name) : S.selected.delete(name);
  renderMcp();
}
async function probeAll() {
  const btn = $("#probeBtn"); btn.disabled = true; $("#probeNote").textContent = "starting servers…";
  S.mcp.forEach((s) => (s.probing = true)); renderMcp();
  try {
    const { results } = await api("/api/mcp/probe", { method: "POST", body: JSON.stringify({}) });
    const by = Object.fromEntries(results.map((r) => [r.name, r]));
    S.mcp.forEach((s) => { s.probing = false; if (by[s.name]) s.probe = by[s.name]; });
    const ok = results.filter((r) => r.ok).length;
    const tools = results.reduce((a, r) => a + (r.tools?.length || 0), 0);
    $("#probeNote").textContent = `${ok}/${results.length} up · ${tools} tools`;
  } catch (e) { $("#probeNote").textContent = String(e); S.mcp.forEach((s) => (s.probing = false)); }
  renderMcp(); btn.disabled = false;
}

// ───────────────────────── NPCI panel ─────────────────────────
let npciTimer;
async function npciSearch() {
  const q = $("#npciQ").value;
  const r = await api(`/api/npci?q=${encodeURIComponent(q)}`);
  $("#npciCount").textContent = q ? `${r.results.length} match${r.results.length === 1 ? "" : "es"} in ${r.count} codes` : `${r.count} codes in the map`;
  const list = $("#npciList"); list.innerHTML = "";
  for (const c of r.results) {
    list.append(h("div", { class: "npci" }, h("span", { class: "code", text: c.code }),
      c.meanings.slice(0, 4).map((m) => h("div", {},
        h("div", { class: "mean" }, m.meaning, m.decline_type ? h("span", { class: "td", text: m.decline_type }) : null),
        m.remarks ? h("div", { class: "sec", text: m.remarks }) : null,
        h("div", { class: "sec", text: m.section })))));
  }
}

// ───────────────────────── run panel ─────────────────────────
function renderRun(v = {}, meta = {}) {
  const box = $("#runInfo"); box.innerHTML = "";
  const runs = v.runs || [];
  const cost = runs.reduce((a, r) => a + (r.cost_usd || 0), 0);
  box.append(h("div", { class: "run-card" }, h("h4", { text: "Thread" }), kvGrid([
    ["thread", S.thread || "-"], ["system", v.system || "-"], ["intent", v.intent || "-"],
    ["tool calls (this turn)", String(v.tool_calls ?? 0)], ["MCP servers", (v.servers || []).join(", ") || "-"],
    ["cost", `$${cost.toFixed(3)}`], ["LLM calls", String(runs.length)]])));
  if (v.entities) {
    const e = Object.entries(v.entities).filter(([, x]) => x && x.length);
    if (e.length) box.append(h("div", { class: "run-card" }, h("h4", { text: "Entities" }), kvGrid(e.map(([k, x]) => [k, x.join(", ")]))));
  }
  if (runs.length) box.append(h("div", { class: "run-card" }, h("h4", { text: "LLM calls" }),
    kvGrid(runs.map((r) => [r.node, `${(r.duration_ms / 1000).toFixed(1)}s · ${r.input_tokens ?? "?"}→${r.output_tokens ?? "?"} tokens (${r.cache_read_tokens ?? 0} cached) · ${r.tool_calls} tool calls · $${(r.cost_usd || 0).toFixed(3)}`]))));
  if (v.plan) box.append(h("div", { class: "run-card" }, h("h4", { text: "Plan" }), h("div", { class: "plan-box", text: v.plan })));
  if (v.review) box.append(h("div", { class: "run-card" }, h("h4", { text: "Review" }),
    kvGrid([["verdict", v.review.verdict], ["score", String(v.review.score ?? "-")], ["summary", v.review.summary || "-"], ...(v.review.gaps || []).map((g, i) => [`gap ${i + 1}`, g])])));
  S.cost = meta.cost_usd ?? cost;
  $("#statCost").textContent = `$${S.cost.toFixed(2)}`;
}
function kvGrid(rows) { return h("div", { class: "kv" }, rows.flatMap(([k, v]) => [h("div", { text: k }), h("div", { text: v })])); }

// ───────────────────────── threads ─────────────────────────
async function loadThreads() {
  const { threads } = await api("/api/threads");
  const box = $("#threads"); box.innerHTML = "";
  if (!threads.length) box.append(h("div", { class: "empty", text: "No investigations yet." }));
  for (const t of threads) {
    const status = t.running ? "running" : t.status;
    box.append(h("div", { class: `thread${t.id === S.thread ? " on" : ""}`, onclick: () => openThread(t.id) },
      h("div", { class: "t-title", text: t.title }),
      h("div", { class: "t-meta" }, h("span", { class: `dot ${status}`, title: status }),
        t.system ? h("span", { class: `sys-badge ${t.system}`, text: t.system }) : null,
        h("span", { text: t.intent || "" }), h("span", { text: `$${(t.cost_usd || 0).toFixed(2)}` })),
      h("button", { class: "t-del", title: "delete", text: "✕", onclick: async (e) => { e.stopPropagation(); if (confirm("Delete this investigation?")) { await api(`/api/threads/${t.id}`, { method: "DELETE" }); if (S.thread === t.id) newThread(); loadThreads(); } } })));
  }
}
async function openThread(id) {
  if (S.running) return;
  const d = await api(`/api/threads/${id}`);
  S.thread = id; const v = d.state || {};
  $("#chat").innerHTML = "";
  for (const m of v.messages || []) m.role === "user" ? addUser(m.content) : addBot(md(m.content), { raw: m.content });
  loadToolLog(v.tool_log || []); renderRun(v, d.meta || {});
  traceLoad(id, v);
  loadThreads();
}
function newThread() {
  if (S.running) return;
  S.thread = null; $("#chat").innerHTML = ""; $("#chat").append(heroEl);
  heroEl.classList.remove("hidden"); traceReset(); loadToolLog([]); renderRun({});
  S.cost = 0; $("#statCost").textContent = "$0.00"; $("#statTools").textContent = "0 tools"; loadThreads(); $("#input").focus();
}

// ───────────────────────── send + SSE ─────────────────────────
// fetch() + a stream reader instead of EventSource, because EventSource can only do GET and
// /api/chat is a POST with a JSON body. SSE frames are separated by a blank line ("\n\n").
async function send(text) {
  text = (text ?? $("#input").value).trim();
  if (!text || S.running) return;
  $("#input").value = ""; autosize();
  addUser(text); startLive(); traceStartTurn();
  if (!S.thread) { loadToolLog([]); }
  S.running = true; setRunning(true);
  const body = {
    message: text, thread_id: S.thread,
    options: { plan: $("#optPlan").checked, review: $("#optReview").checked,
      ...(S.selected ? { servers: [...S.selected] } : {}) },
  };
  // AbortController = a handle to cancel the fetch later (used by the Stop button).
  S.abort = new AbortController();
  try {
    // JSON.stringify turns the JS object into JSON text (Python: json.dumps).
    const r = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), signal: S.abort.signal });
    if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
    // Read the response body piece by piece as it arrives, instead of waiting for the end.
    // TextDecoder turns the raw bytes into text. `buf` holds text not yet processed.
    const reader = r.body.getReader(); const dec = new TextDecoder(); let buf = "";
    for (;;) {  // loop forever; `break` when the server closes the stream
      // `const { value, done } = ...` pulls two fields out of the returned object (destructuring).
      const { value, done } = await reader.read(); if (done) break;
      buf += dec.decode(value, { stream: true });
      let k;
      // A piece of network data can hold half an event or several events, so cut out every
      // complete one (ending in a blank line) and keep the rest in `buf` for next time.
      while ((k = buf.indexOf("\n\n")) >= 0) {
        const chunk = buf.slice(0, k); buf = buf.slice(k + 2);
        // Keep the `data: ` lines (drops `: ping` keep-alives), strip the prefix → JSON text.
        const data = chunk.split("\n").filter((l) => l.startsWith("data: ")).map((l) => l.slice(6)).join("\n");
        // JSON.parse = json.loads. Each event (e.g. {type: "tool_use", ...}) goes to handle().
        if (data) handle(JSON.parse(data));
      }
    }
  } catch (e) {
    if (e.name !== "AbortError") { endLive(); addBot(`<p>⚠️ ${esc(e.message)}</p>`, { pills: [["error", "bad"]] }); }
    traceEnd(true);
  } finally {
    S.running = false; setRunning(false); traceEnd(false); loadThreads(); loadUsage();
  }
}
// Every event from the server stream ends up here.
// `switch (x) { case "a": ...; break; }` is like Python's if/elif chain on one value
// (or `match`). `break` ends that case; without it the code would fall into the next case.
function handle(ev) {
  switch (ev.type) {
    case "thread": S.thread = ev.thread_id; loadThreads(); break;
    case "node_start": traceNodeStart(ev.node); liveStatus(`${ICONS[ev.node] || ""} ${ev.node}…`); break;
    case "node_end":
      traceNodeEnd(ev);
      if (ev.run) { S.cost += ev.run.cost_usd || 0; $("#statCost").textContent = `$${S.cost.toFixed(2)}`; }
      break;
    case "triage":
      liveStatus(`🧭 ${ev.system ? ev.system.toUpperCase() : "system unknown"} · ${ev.intent}`);
      break;
    case "agent_start": $("#engineOrb").classList.add("live"); liveStatus(`◭ ${ev.model} · ${ev.node} is thinking…`); if (S.liveMsg && ev.node !== "agent") S.liveMsg.text.textContent = ""; break;
    case "init": {
      const ok = (ev.mcp_servers || []).filter((s) => s.status === "connected").length;
      liveStatus(`◭ ${ev.node}: ${ev.model} · ${ok}/${(ev.mcp_servers || []).length} MCP servers connected · ${ev.tools} tools`);
      for (const s of ev.mcp_servers || []) { const row = S.mcp.find((x) => x.name === s.name); if (row && !row.probe) row.probe = { ok: s.status === "connected", tools: [], error: s.status }; }
      renderMcp(); break;
    }
    case "thinking_delta": if (S.liveMsg) { S.liveMsg.think.classList.remove("hidden"); S.liveMsg.thinkBody.textContent += ev.text; S.liveMsg.thinkBody.scrollTop = 1e9; } break;
    case "text_delta": if (S.liveMsg) { S.liveMsg.text.textContent += ev.text; scrollChat(); } break;
    case "tool_use": addTool(ev); break;
    case "tool_result": toolResult(ev); break;
    case "agent_end": $("#engineOrb").classList.remove("live"); break;
    case "warning": liveStatus(`⚠️ ${ev.text}`); break;
    case "review": liveStatus(`⚖️ review: ${ev.verdict}${ev.gaps?.length ? ` — ${ev.gaps.length} gaps, digging deeper` : ""}`); break;
    // the graph finished: swap the live bubble for the rendered report
    case "final": {
      endLive(); traceEnd(false); $("#engineOrb").classList.remove("live");
      const pills = [];
      if (ev.system) pills.push([ev.system.toUpperCase(), "good"]);
      if (ev.intent) pills.push([ev.intent]);
      if (ev.cost_usd) pills.push([`$${ev.cost_usd.toFixed(3)}`]);
      const tools = (ev.runs || []).reduce((a, r) => a + (r.tool_calls || 0), 0);
      if (tools) pills.push([`${tools} tool calls`]);
      if (ev.needs_input) pills.push(["needs your answer", "warn"]);
      addBot(md(ev.report), { pills, raw: ev.report });
      api(`/api/threads/${S.thread}`).then((d) => renderRun(d.state || {}, d.meta || {})).catch(() => {});
      break;
    }
    case "error": endLive(); addBot(`<p>⚠️ ${esc(ev.message)}</p>`, { pills: [["error", "bad"]] }); traceEnd(true); break;
    case "done": break;
  }
}
// The "12/100 today" chip: the caller's questions today vs the daily limit (GET /api/usage).
async function loadUsage() {
  try {
    const u = await api("/api/usage");
    const q = u.limit ? `${u.questions}/${u.limit} today` : `${u.questions} today`;
    const m = u.monthly_budget_usd ? ` · $${u.month_cost_usd.toFixed(0)}/$${u.monthly_budget_usd.toFixed(0)} month` : "";
    $("#statQuota").textContent = q + m;
    const near = (u.limit && u.questions >= u.limit * 0.8) || (u.monthly_budget_usd && u.month_cost_usd >= u.monthly_budget_usd * 0.8);
    $("#statQuota").style.color = near ? "var(--amber, #e3b341)" : "";
  } catch { /* the chip just stays as it was */ }
}
function setRunning(on) {
  $("#send").disabled = on; $("#cancelBtn").classList.toggle("hidden", !on);
  if (!on) $("#engineOrb").classList.remove("live");
}
async function cancelRun() {
  if (!S.thread) return;
  try { await api(`/api/threads/${S.thread}/cancel`, { method: "POST" }); } catch { /* the stream reports it */ }
}

// ───────────────────────── wiring ─────────────────────────
const heroEl = $("#hero");
function autosize() { const t = $("#input"); t.style.height = "auto"; t.style.height = `${Math.min(t.scrollHeight, 220)}px`; }
$("#input").addEventListener("input", autosize);
$("#input").addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
$("#send").addEventListener("click", () => send());
$("#cancelBtn").addEventListener("click", cancelRun);
$("#newThread").addEventListener("click", newThread);
$("#probeBtn").addEventListener("click", probeAll);
$("#npciQ").addEventListener("input", () => { clearTimeout(npciTimer); npciTimer = setTimeout(npciSearch, 180); });
$$("#tabs button").forEach((b) => b.addEventListener("click", () => {
  $$("#tabs button").forEach((x) => x.classList.toggle("on", x === b));
  $$(".tab").forEach((t) => t.classList.toggle("on", t.id === `tab-${b.dataset.tab}`));
}));
for (const [label, prompt] of QUICK) $("#quick").append(h("button", { class: "qchip", text: label, onclick: () => { $("#input").value = prompt; autosize(); $("#input").focus(); } }));

(async function boot() {
  try {
    const cfg = await api("/api/config");
    S.graph = cfg.graph;
    const pretty = cfg.model.replace(/^claude-/, "").replace(/-(\d+)-(\d+)$/, " $1.$2").replace(/^\w/, (c) => c.toUpperCase());
    $("#engineName").textContent = `Anthropic API · ${pretty}`;
    $("#engineSub").textContent = `≤ ${cfg.max_tool_calls} tool calls · ${cfg.npci_codes} NPCI codes mapped`;
    $("#optPlan").checked = cfg.plan; $("#optReview").checked = cfg.review;
  } catch (e) { console.error(e); }
  renderGraph(); renderTrace();
  await Promise.allSettled([loadThreads(), loadMcp(), npciSearch(), loadUsage()]);
  $("#input").focus();
})();
