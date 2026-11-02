"""
The NODES, in the order they run. Each one is a box in the graph (svg/n03-query-graph.svg).

[LangGraph] Every node has the same shape:

    def node_name(s: QAState) -> dict:
        ...read what it needs from s...
        return {"some_key": new_value}      # ONLY the keys it changes

LangGraph calls it with the current state and merges the returned dict into the state. A node never
edits `s` in place and never calls the next node; the edges in graph.py decide what runs next.
graph.py registers each function under its own name (fn.__name__), so the names below are the ones you
see in the diagram, in `--stream` output and in the checkpoint history.

    understand         read the question                        (LLM: fake_plan)
    retrieve           pinned rule clauses + keyword search
    rerank             best 12, then MMR down to 6
    latest_wins        current / history / upcoming per rule    (the ₹500 -> ₹1,000 logic)
    generate           write the cited answer                   (LLM: fake_answer)
    check_grounding    every number in the answer is in a cited source?
    cite_sources       end: answer + proof block
    clarify_or_refuse  end: "which product?" / off-topic
    not_found          end: grounding failed twice
"""
from __future__ import annotations

import re
from datetime import date

from .data import PRODUCTS
from .fake_llm import fake_answer, fake_plan
from .models import Chunk, Source
from .state import QAState
from .store import chunks, circulars, tokens

# [Python] `date.today()` runs once, when the module is first imported. Every question uses it as "now"
#          unless the question names a date ("on 10 Dec 2024").
TODAY = date.today()


# --------------------------------------------------------------------------------------------------
# 1. understand
# --------------------------------------------------------------------------------------------------

def understand(s: QAState) -> dict:
    """Work out what is being asked: intent, products, rule parameter, as-of date.
    [Real] one Claude call with structured output (QueryPlan)."""
    # Follow-ups: the checkpointer brought back last turn's products/parameter (same thread_id), so we
    # pass them in. A fresh thread has none, hence .get(..., default).
    plan = fake_plan(s["question"], {"products": s.get("products", []), "parameter": s.get("parameter")})
    # [LangGraph] Why reset every per-turn key here: with a checkpointer, a new question on the same
    # thread STARTS FROM LAST TURN'S STATE (only "question" is new). Without the reset, last turn's
    # answer, sources and retries would leak into this turn. Reducer-free state never clears itself;
    # the first node of a turn does it.
    return {
        "intent": plan.intent, "products": plan.products, "parameter": plan.parameter,
        "as_of": plan.as_of or TODAY, "pinned": [], "candidates": [], "sources": [],
        "answer": "", "citations": [], "found": False, "grounded": False, "retries": 0, "final": "",
    }


# --------------------------------------------------------------------------------------------------
# 2. retrieve
# --------------------------------------------------------------------------------------------------

def retrieve(s: QAState) -> dict:
    """Collect candidate clauses, from two places:
    - rule questions: EVERY clause with that rule_key, by metadata filter ("pinned"). The newest clause
      can't be missed by similarity search, so "latest wins" can't silently fall back to the old ₹500.
    - everything: hybrid search (BM25 + vector in Weaviate), filtered by product.
    [LangGraph] This node also runs a SECOND time when check_grounding sends the run back here (the retry
    loop). It tells the two apart by reading the state: retries > 0 means "this is the retry"."""
    pinned = []
    if s["parameter"]:
        # [Python] A nested comprehension: for each product, for each clause of that product's rule.
        pinned = [c for p in s["products"] for c in chunks.by_rule(f"{p}.{s['parameter']}")]
    broaden = s.get("retries", 0) > 0                         # retry: drop the product filter, fetch more
    hits = chunks.search(s["question"], [] if broaden else s["products"], k=80 if broaden else 40)
    return {"pinned": pinned, "candidates": hits}


# --------------------------------------------------------------------------------------------------
# 3. rerank (+ its helpers: similarity, mmr)
# --------------------------------------------------------------------------------------------------

def similarity(a: str, b: str) -> float:
    """Stand-in for cosine similarity between two embeddings: word overlap (Jaccard), 0.0 to 1.0."""
    x, y = set(tokens(a)), set(tokens(b))
    return len(x & y) / len(x | y) if x | y else 0.0


def mmr(ranked: list[Chunk], k: int, lam: float, pinned: list[Chunk]) -> list[Chunk]:
    """Maximal Marginal Relevance: pick one chunk at a time, scoring
         lam * relevance(chunk)  -  (1 - lam) * max similarity(chunk, chunks already picked)
    so a near-duplicate of something already picked loses to a slightly less relevant, NEW fact.
    `ranked` is best-first; relevance comes from that rank (real: the reranker's score).
    The pinned chunks start out as "already picked": always kept, and the rest must differ from them."""
    picked = list(pinned)
    relevance = {c.uuid: 1 - i / len(ranked) for i, c in enumerate(ranked)}   # 1.0 for the best, then lower
    pool = [c for c in ranked if c.uuid not in {p.uuid for p in picked}]
    while pool and len(picked) < k:
        # [Python] max(pool, key=f): the item with the highest f(item). default=0.0 covers "nothing picked yet".
        best = max(pool, key=lambda c: lam * relevance[c.uuid]
                   - (1 - lam) * max((similarity(c.text, p.text) for p in picked), default=0.0))
        picked.append(best)
        pool.remove(best)
    return picked


def rerank(s: QAState) -> dict:
    """Keep the best few candidates, without near-duplicates.
    [Real] a cross-encoder (Cohere Rerank / bge-reranker) scores each (question, chunk) pair and we keep
    the best 12; then MMR picks 6 that aren't near-duplicates. Here the search order stands in for the
    reranker, and word overlap stands in for embedding similarity between chunks.
    The pinned rule clauses always stay: MMR may never drop the proof."""
    ranked = s["candidates"][:12]          # real: sorted by cross-encoder score, best first
    # [LangGraph] Returning "candidates" again REPLACES the search hits with the 6 chosen chunks.
    return {"candidates": mmr(ranked, k=6, lam=0.5, pinned=s["pinned"])}


# --------------------------------------------------------------------------------------------------
# 4. latest_wins: the ₹500 -> ₹1,000 answer
# --------------------------------------------------------------------------------------------------

def latest_wins(s: QAState) -> dict:
    """The update rule, at query time. For each rule_key, among its clauses:
    the latest with effective_from <= as_of is CURRENT, older ones are HISTORY (replaced by the next one),
    later ones are UPCOMING. Nothing is stored: 'replaced by' is worked out here, every time.
    Example, UPI Lite limit asked today: OC-L2 (₹1,000, from 2024-12-16) is CURRENT, OC-L1 (₹500) is
    HISTORY "replaced by OC-L2 from 2024-12-16". Asked "on 10 Dec 2024": OC-L1 is CURRENT, OC-L2 UPCOMING."""
    as_of, out = s["as_of"], []
    # Group the chosen chunks by rule. Chunks without a rule_key all land in the None group.
    groups: dict[str | None, list[Chunk]] = {}
    for c in s["candidates"]:
        # [Python] d.setdefault(k, []) returns d[k], first creating it as [] if it isn't there.
        groups.setdefault(c.rule_key, []).append(c)
    for key, cs in groups.items():
        cs = sorted(cs, key=lambda c: c.effective_from)
        live = [c for c in cs if c.effective_from <= as_of]        # already in force on the asked date
        # [Python] enumerate(cs) gives (index, item) pairs.
        for i, c in enumerate(cs):
            if c.effective_from > as_of:
                role = "upcoming"
            elif key is None or c is live[-1]:
                role = "current"                           # clauses without a rule_key are just in force
            else:
                role = "history"
            nxt = cs[i + 1] if key is not None and i + 1 < len(cs) else None   # the clause that came after it
            out.append(Source(n=0, circular_id=c.circular_id, clause_path=c.clause_path, rule_key=c.rule_key,
                              page=c.page, text=c.text, effective_from=c.effective_from, role=role,
                              replaced_by=nxt.circular_id if nxt and role == "history" else None,
                              replaced_on=nxt.effective_from if nxt and role == "history" else None,
                              pdf_url=circulars[c.circular_id]["pdf_url"]))
    # Order: rule clauses first (current, upcoming, history), then the plain clauses.
    # [Python] Sorting by a tuple compares the first item, then the second on ties. False sorts before True.
    order = {"current": 0, "upcoming": 1, "history": 2}
    out.sort(key=lambda x: (x.rule_key is None, order[x.role]))
    # Number them [1], [2], ... in that order. model_copy(update=...) makes a copy with n changed
    # (the pydantic objects are treated as read-only records).
    return {"sources": [src.model_copy(update={"n": i + 1}) for i, src in enumerate(out)]}


# --------------------------------------------------------------------------------------------------
# 5. generate
# --------------------------------------------------------------------------------------------------

def generate(s: QAState) -> dict:
    """Write the answer from the numbered sources.  [Real] Claude Sonnet, see fake_llm.fake_answer."""
    answer, citations, found = fake_answer(s["intent"], s["parameter"], s["sources"])
    return {"answer": answer, "citations": citations, "found": found}


# --------------------------------------------------------------------------------------------------
# 6. check_grounding
# --------------------------------------------------------------------------------------------------

def numbers_in(text: str) -> set[str]:
    """Every number in the text, commas removed: "₹1,000 from 2024-12-16" -> {"1000", "2024", "12", "16"}."""
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*", text)}


def check_grounding(s: QAState) -> dict:
    """Every number in the answer must appear in a source it cites. Cheap, and catches the worst failure:
    a confident wrong limit. The [n] markers are removed first (they are numbers too).
    [LangGraph] It doesn't choose the next node itself: it writes `grounded` and `retries`, and the
    router routers.route_grounding reads them. Nodes do work; routers decide."""
    by_n = {src.n: src for src in s["sources"]}
    cited = [by_n[n] for n in s["citations"] if n in by_n]
    evidence = " ".join(f"{c.circular_id} {c.clause_path} {c.text} {c.effective_from}" for c in cited)
    claims = numbers_in(re.sub(r"\[\d+\]", "", s["answer"]))
    # [Python] For sets, a <= b means "a is a subset of b": every number claimed is in the evidence.
    ok = s["found"] and bool(cited) and claims <= numbers_in(evidence)
    return {"grounded": ok, "retries": s.get("retries", 0) + (0 if ok else 1)}


# --------------------------------------------------------------------------------------------------
# 7. The three end nodes. Each writes "final", the text the user sees, and leads to END.
# --------------------------------------------------------------------------------------------------

def cite_sources(s: QAState) -> dict:
    """Success. The answer plus the proof: circular id, clause, page, the exact text and a link, for every
    citation. This is the tool's main feature: the user can check every answer in the circular."""
    by_n = {src.n: src for src in s["sources"]}
    lines = [s["answer"], "", "Proof (check it in the circular):"]
    for n in s["citations"]:
        src = by_n[n]
        status = src.role.upper()
        if src.replaced_by:
            status += f", replaced by {src.replaced_by} from {src.replaced_on}"
        lines.append(f"  [{n}] {src.circular_id} > {src.clause_path}, page {src.page}, "
                     f"effective {src.effective_from} ({status})")
        lines.append(f"      \"{src.text}\"")
        lines.append(f"      {src.pdf_url or '(sample circular in data.py, no PDF)'}")
    lines.append("Check the source circular before acting.")
    return {"final": "\n".join(lines)}


def clarify_or_refuse(s: QAState) -> dict:
    """Off-topic -> refuse. A rule question without a product -> ask which product.
    [LangGraph] The thread keeps its state, so the user's reply ("UPI Lite") runs as a new turn on the same
    thread. A real chatbot could instead pause right here with interrupt() and resume on the reply."""
    if s["intent"] == "out_of_scope":
        return {"final": "I only answer questions about NPCI / UPI circulars."}
    return {"final": "Which product do you mean? " + ", ".join(PRODUCTS.values()) + "."}


def not_found(s: QAState) -> dict:
    """Grounding failed twice: saying "not found" beats guessing a number."""
    return {"final": "Not found in the indexed circulars. Try naming the product or the circular number."}
