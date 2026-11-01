"""
NPCI Circular Intelligence: learning version of the RAG + LangGraph flow.

Runs fully offline. Everything that would be a cloud service is faked in memory,
with a comment saying what the real thing is:

    S3 + 10-minute job   ->  ingest_job(inbox)            (manifest keyed by content hash)
    Textract + Claude    ->  circulars already given as clauses with metadata
    Weaviate             ->  ChunkStore                   (keyword score + the same metadata filters)
    Claude Sonnet        ->  fake_plan() / fake_answer()  (keyword rules)

    pip install langgraph pydantic
    python npci_circular_graph.py

How updates (₹500 -> ₹1,000) are handled: APPEND-ONLY. Every clause is stored once with
static metadata (effective_from, rule_key) and is never edited or deleted. At query time,
among the clauses that state the same rule, the latest one in force on the asked date wins;
older ones are shown as history, future ones as upcoming.

The UPI Lite circulars OC-L1 / OC-L2 and their dates are SYNTHETIC placeholders for the
₹500 -> ₹1,000 example. OC-229 is reconstructed from what OC-229A says about it.
The other four are excerpts of the real circulars.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from datetime import date
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

TODAY = date.today()

PRODUCTS = {
    "UPI_LITE": "UPI Lite",
    "TAP_AND_PAY": "UPI Tap & Pay",
    "NRI_INTL_MOBILE": "NRI / international mobile numbers",
    "URCS_GST": "URCS back-office GST / ISD",
    "DISPUTES_MCC": "MCC misclassification disputes",
}
LABELS = {"per_txn_limit": "per transaction limit", "min_claim_amount": "minimum claim amount",
          "response_days": "response time", "isd_section": "ISD sections",
          "isd_update_window": "ISD update window", "permitted_country": "permitted countries"}


# =====================================================================================
# 1. Data shapes
# =====================================================================================

class Chunk(BaseModel):
    """One clause of one circular. A Weaviate object in the real design.
    Every field is written ONCE at ingest and never edited."""
    uuid: str
    circular_id: str
    clause_path: str
    text: str
    header: str                         # contextual header, embedded together with the text
    products: list[str]
    rule_key: str | None = None         # "UPI_LITE.per_txn_limit": which rule this clause sets, if any
    page: int
    issue_date: date
    effective_from: date                # the EFFECTIVE date, not the issue date


class QueryPlan(BaseModel):
    """What Claude extracts from the question (structured output)."""
    intent: Literal["rule_value", "what_changed", "explain", "out_of_scope"]
    products: list[str]
    parameter: str | None
    as_of: date | None


class Source(BaseModel):
    """A numbered piece of evidence: shown to the LLM, then to the user as proof."""
    n: int
    circular_id: str
    clause_path: str
    rule_key: str | None
    page: int
    text: str
    effective_from: date
    role: Literal["current", "history", "upcoming"]
    replaced_by: str | None = None      # worked out at query time, never stored
    replaced_on: date | None = None
    pdf_url: str | None


# =====================================================================================
# 2. Sample circulars: what OCR + Claude extraction would hand to the ingest step.
#    Each clause: (clause_path, page, text, rule_key). rule_key is set when the clause
#    states a looked-up rule (a limit, a window, a list); None for everything else.
# =====================================================================================

NPCI = "https://www.npci.org.in/uploads/"

CIRCULARS = [
    {   # SYNTHETIC placeholder: the older UPI Lite limit
        "id": "OC-L1", "subject": "UPI Lite: transaction limits", "issue_date": "2023-10-01",
        "effective_from": "2023-10-01", "products": ["UPI_LITE"], "pdf_url": None,
        "clauses": [
            ("Guidelines > 3", 1, "The per transaction limit for UPI Lite shall be ₹500.", "UPI_LITE.per_txn_limit"),
            ("Guidelines > 4", 1, "UPI Lite payments up to the per transaction limit shall not require UPI PIN.",
             None),
        ],
    },
    {   # SYNTHETIC placeholder: issued 2 Dec, effective 16 Dec -> issue date != effective date
        "id": "OC-L2", "subject": "UPI Lite: enhancement of per transaction limit", "issue_date": "2024-12-02",
        "effective_from": "2024-12-16", "products": ["UPI_LITE"], "pdf_url": None,
        "clauses": [
            ("Main", 1, "With reference to circular OC-L1, the UPI Lite per transaction limit is revised.", None),
            ("Guidelines > 2(a)", 1, "The per transaction limit for UPI Lite is enhanced from ₹500 to ₹1,000, "
                                     "effective 16 December 2024.", "UPI_LITE.per_txn_limit"),
        ],
    },
    {
        "id": "UPI-OC-186A-2026-27", "subject": "Enhancement - UPI Tap & Pay on Point of Sale (PoS)",
        "issue_date": "2026-09-10", "effective_from": "2026-09-10", "products": ["TAP_AND_PAY"],
        "pdf_url": NPCI + "UPI_I_OC_No_186_A_I_Enhancement_UPI_Tap_and_Pay_on_Point_of_Sale_Po_S_e695625b85.pdf",
        "clauses": [
            ("Main", 1, "With reference to UPI Operating Circular NPCI/UPI/OC-186/2023-24 dated 19th December 2023, "
                        "UPI Tap & Pay through NFC on QR was introduced. UPI Tap & Pay shall now be extended to "
                        "Point of Sale (PoS) terminals.", None),
            ("Key Guidelines > 1", 1, "Members and UPI Application Providers shall ensure that UPI Tap & Pay "
                                      "transactions on PoS terminals are accepted only for Person-to-Merchant (P2M) "
                                      "transactions.", None),
            # a new SCOPE (PoS) gets its own rule key, so it never competes with the QR rules
            ("Key Guidelines > 3", 1, "Members and UPI Application Providers shall ensure that per transaction limit "
                                      "is capped at ₹5000, up to which additional factor of authentication shall "
                                      "not be required.", "TAP_AND_PAY.per_txn_limit.PoS"),
            ("UPI Application Provider > 2", 2, "UPI Application Providers shall ensure that device lock is enabled "
                                                "as a prerequisite for activating UPI Tap & Pay. The device shall be "
                                                "in an unlocked state at the time of initiating a transaction.", None),
        ],
    },
    {   # RECONSTRUCTED from OC-229A's own summary of it (we don't have the OC-229 PDF)
        "id": "UPI-OC-229-2025-26", "subject": "ISD/GSTIN option in URCS (reconstructed)",
        "issue_date": "2025-11-12", "effective_from": "2025-11-17", "products": ["URCS_GST"], "pdf_url": None,
        "clauses": [
            ("Main", 1, "The Input Service Distributor (ISD)/GSTIN option would be enabled in the URCS system for "
                        "both payable and receivable sections.", "URCS_GST.isd_section"),
        ],
    },
    {
        "id": "UPI-OC-229A-2026-27", "subject": "Implementation of Revised ISD-GSTIN Option in URCS Back-Office System",
        "issue_date": "2026-08-24", "effective_from": "2026-09-15", "products": ["URCS_GST"],
        "pdf_url": NPCI + "UPI_OC_229_A_ISD_GSTIN_Input_Service_Distributor_Option_in_UPI_URCS_898c087730.pdf",
        "clauses": [
            ("Main > a", 1, "The receivable section has been removed from the ISD functionality. Users will now be "
                            "able to update ISD details only for the payable section.", "URCS_GST.isd_section"),
            ("Main > c", 1, "Users are permitted to update only one GSTIN or ISD per product per bank in a month.",
             None),
            ("Main > d", 1, "ISD/GSTIN update should be submitted in URCS between the 15th and 31st or last day of "
                            "every month. Back Office system will not permit users to update ISD/GSTIN details "
                            "between the 1st to 14th of every month.", "URCS_GST.isd_update_window"),
            ("Go-Live", 1, "Revised ISD-GSTIN functionality will be made live on Sep 15, 2026.", None),
        ],
    },
    {
        "id": "UPI-OC-239-2026-27", "subject": "UPI - Process for Resolution of MCC Misclassification related disputes",
        "issue_date": "2026-10-14", "effective_from": "2026-10-14", "products": ["DISPUTES_MCC"],
        "pdf_url": NPCI + "UPI_OC_239_UPI_Process_for_Resolution_of_MCC_Misclassification_related_disputes_"
                          "7770320097.pdf",
        "clauses": [
            ("2.3 Claim Eligibility > a(i)", 5, "Amount Threshold for a Claim: Minimum aggregate Claim amount must "
                                                "be INR 10,00,000 (Ten Lakhs rupees only).",
             "DISPUTES_MCC.min_claim_amount"),
            ("4.2 Pre-Compliance Response > a", 8, "Responding Party must submit response in 23 calendar days. On "
                                                   "expiry of 23rd day, if no response is received, responding party "
                                                   "will have a period of 7 calendar days as grace period.",
             "DISPUTES_MCC.response_days"),
            ("4.4 Panel for Resolution of Disputes > b", 10, "Panel shall endeavor to review the Claim and resolve "
                                                             "the same within 90 calendar days from Panel Reference "
                                                             "Date.", None),
        ],
    },
    {
        "id": "UPI-OC-161A-2026-27", "subject": "Addition of New Countries to the List of Permitted International "
                                               "Mobile Numbers in UPI",
        "issue_date": "2026-10-01", "effective_from": "2026-10-01", "products": ["NRI_INTL_MOBILE"],
        "pdf_url": NPCI + "UPI_OC_161_A_Digital_cc63c6c44f.pdf",
        "clauses": [
            ("Main", 1, "With reference to NPCI/UPI/OC-161/2022-23, international mobile numbers of 12 countries "
                        "were permitted. Now, international mobile numbers from the following 19 countries are being "
                        "added: Bahrain, Bhutan, Brazil, Germany, Greece, Ireland, Italy, Japan, Kuwait, Maldives, "
                        "Nepal, Netherlands, New Zealand, Philippines, Portugal, South Africa, Spain, Sweden, "
                        "Thailand. All compliance requirements shall remain as is.", "NRI_INTL_MOBILE.permitted_country"),
        ],
    },
]


# =====================================================================================
# 3. Chunk store (in memory). Real: Weaviate. APPEND-ONLY: no update, no delete.
# =====================================================================================

def tokens(text: str) -> list[str]:
    stop = {"the", "a", "an", "of", "for", "to", "in", "on", "is", "what", "and", "or", "be", "shall", "by", "with"}
    return [t for t in re.findall(r"[a-z0-9₹]+", text.lower().replace(",", "")) if t not in stop]


class ChunkStore:
    """Weaviate stand-in. Real search is hybrid (BM25 + vector); here it is a BM25-like keyword score."""

    def __init__(self) -> None:
        self.objects: dict[str, Chunk] = {}

    def add(self, new: list[Chunk]) -> None:
        for c in new:
            self.objects[c.uuid] = c                    # deterministic uuid: re-ingest overwrites, no duplicates

    def by_rule(self, rule_prefix: str) -> list[Chunk]:
        """Metadata filter, not similarity: EVERY clause that states this rule, oldest first.
        Real: fetch_objects(filters=Filter.by_property("rule_key").like(f"{prefix}*"))"""
        return sorted((c for c in self.objects.values() if c.rule_key and c.rule_key.startswith(rule_prefix)),
                      key=lambda c: c.effective_from)

    def search(self, query: str, products: list[str], k: int) -> list[Chunk]:
        pool = [c for c in self.objects.values() if not products or set(products) & set(c.products)]
        docs = {c.uuid: Counter(tokens(c.header + " " + c.text)) for c in pool}
        df = Counter(t for d in docs.values() for t in d)
        scored = []
        for c in pool:
            tf = docs[c.uuid]
            s = sum(math.log(1 + len(pool) / df[t]) * tf[t] / (tf[t] + 1.2) for t in set(tokens(query)) if t in tf)
            if s > 0:
                scored.append((s, c))
        return [c for _, c in sorted(scored, key=lambda x: -x[0])[:k]]


chunks = ChunkStore()
circulars: dict[str, dict] = {}        # circular registry (Postgres in the real design)


# =====================================================================================
# 4. Ingestion. Real: EventBridge rate(10 minutes) -> one task -> S3 -> Textract -> Claude.
# =====================================================================================

manifest: dict[str, str] = {}          # sha256 -> status. A Postgres table in the real design.


def ingest_circular(c: dict) -> int:
    """Write each clause ONCE with its static metadata. Nothing older is touched:
    the new ₹1,000 clause simply sits next to the old ₹500 one."""
    cid = c["id"]
    circulars[cid] = c
    new = [Chunk(uuid=hashlib.sha1(f"{cid}:{path}".encode()).hexdigest(), circular_id=cid, clause_path=path,
                 text=text, header=f"[{cid} | {c['subject']} | {c['issue_date']} | {path}]",
                 products=c["products"], rule_key=rule_key, page=page,
                 issue_date=date.fromisoformat(c["issue_date"]), effective_from=date.fromisoformat(c["effective_from"]))
           for path, page, text, rule_key in c["clauses"]]
    chunks.add(new)
    return len(new)


def ingest_job(inbox: list[dict]) -> None:
    """One scheduled run. Real: take a lock (pg_try_advisory_lock), list S3, hash each new PDF."""
    for c in inbox:
        sha = hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest()
        if manifest.get(sha) == "INDEXED":
            print(f"  skip {c['id']}: same content already indexed")
            continue
        n = ingest_circular(c)
        manifest[sha] = "INDEXED"
        print(f"  indexed {c['id']}: {n} chunks appended (effective {c['effective_from']})")


# =====================================================================================
# 5. Fake Claude. Real:
#      llm = ChatAnthropic(model="claude-sonnet-5-5", max_tokens=2048)
#      plan = llm.with_structured_output(QueryPlan).invoke([("system", PLANNER_PROMPT), ("human", q)])
# =====================================================================================

KEYWORDS = {
    "UPI_LITE": ["lite"],
    "TAP_AND_PAY": ["tap", "pos", "nfc"],
    "URCS_GST": ["isd", "gstin", "gst", "urcs"],
    "DISPUTES_MCC": ["mcc", "dispute", "claim", "prd"],
    "NRI_INTL_MOBILE": ["countries", "country", "international", "nri"],
}
MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()


def parse_date(text: str) -> date | None:
    m = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]{3})[a-z]*\.?\s+(\d{4})", text.lower())
    return date(int(m[3]), MONTHS.index(m[2]) + 1, int(m[1])) if m and m[2] in MONTHS else None


def fake_plan(question: str, previous: dict) -> QueryPlan:
    q = question.lower()
    products = [p for p, words in KEYWORDS.items() if any(re.search(rf"\b{w}\b", q) for w in words)]
    parameter = None
    if "limit" in q:
        parameter = "per_txn_limit"
    elif "minimum claim" in q:
        parameter = "min_claim_amount"
    elif "respond" in q or "response" in q:
        parameter = "response_days"
    elif "isd" in q and any(w in q for w in ("section", "receivable", "payable")):
        parameter = "isd_section"

    follow_up = q.startswith("and ") or "before that" in q
    if follow_up and not products:                       # "and before that?" -> reuse the last turn
        products, parameter = previous.get("products", []), parameter or previous.get("parameter")

    on_topic = products or any(w in q for w in ("upi", "npci", "circular", "limit"))
    if not on_topic:
        intent = "out_of_scope"
    elif re.search(r"\b(before|chang\w*|previous|history)\b", q):
        intent = "what_changed"
    elif parameter:
        intent = "rule_value"
    else:
        intent = "explain"
    return QueryPlan(intent=intent, products=products, parameter=parameter, as_of=parse_date(q))


AMOUNT = r"(?:₹|INR )\s?\d(?:[\d,]*\d)?|\b\d+ calendar days\b"
AMOUNT_RE = re.compile(AMOUNT)
FROM_TO_RE = re.compile(rf"from ({AMOUNT}) to ({AMOUNT})")


def fake_answer(intent: str, parameter: str | None, sources: list[Source]) -> tuple[str, list[int], bool]:
    """Real: Claude Sonnet with the numbered sources in the prompt, told that CURRENT beats HISTORY,
    and structured output (answer, citations, found)."""
    def value(s: Source) -> str:
        change = FROM_TO_RE.search(s.text)              # "enhanced from ₹500 to ₹1,000" -> ₹1,000
        if change:
            return change.group(2)
        found = AMOUNT_RE.findall(s.text)                # "23 calendar days ... 7 calendar days" -> the first
        return found[0] if found else f"\"{s.text}\""

    def label(s: Source) -> str:
        product, param = s.rule_key.split(".")[:2]
        return f"{PRODUCTS[product]} {LABELS[param]}"

    rules = [s for s in sources if s.rule_key and s.rule_key.split(".")[1] == parameter]   # only the asked rule
    if intent == "what_changed" and rules:
        steps = [f"{value(s)} from {s.effective_from} ({s.circular_id}) [{s.n}]"
                 for s in sorted(rules, key=lambda s: s.effective_from)]
        text = f"{label(rules[0])}: " + " -> ".join(steps) + "."
    elif intent == "rule_value" and any(s.role == "current" for s in rules):
        parts = []
        for s in rules:
            if s.role == "current":
                parts.append(f"{label(s)} is {value(s)} ({s.circular_id}, {s.clause_path}), "
                             f"in force since {s.effective_from} [{s.n}].")
            elif s.role == "upcoming":
                parts.append(f"It changes to {value(s)} from {s.effective_from} ({s.circular_id}) [{s.n}].")
            elif s.role == "history":
                parts.append(f"Earlier: {value(s)} under {s.circular_id} [{s.n}].")
        text = " ".join(parts)
    else:
        current = [s for s in sources if s.role == "current"]
        if not current:
            return "", [], False
        text = " ".join(f"{s.text} [{s.n}]" for s in current[:2])
    return text, sorted({int(n) for n in re.findall(r"\[(\d+)\]", text)}), True


# =====================================================================================
# 6. The LangGraph flow
# =====================================================================================

class QAState(TypedDict, total=False):
    question: str
    intent: str
    products: list[str]
    parameter: str | None
    as_of: date
    pinned: list[Chunk]                 # every clause of the asked rule, fetched by metadata
    candidates: list[Chunk]
    sources: list[Source]
    answer: str
    citations: list[int]
    found: bool
    grounded: bool
    retries: int
    final: str


def understand(s: QAState) -> dict:
    plan = fake_plan(s["question"], {"products": s.get("products", []), "parameter": s.get("parameter")})
    return {  # also resets every per-turn field: the checkpointer keeps state across turns of a thread
        "intent": plan.intent, "products": plan.products, "parameter": plan.parameter,
        "as_of": plan.as_of or TODAY, "pinned": [], "candidates": [], "sources": [],
        "answer": "", "citations": [], "found": False, "grounded": False, "retries": 0, "final": "",
    }


def route_intent(s: QAState) -> str:
    if s["intent"] == "out_of_scope":
        return "clarify_or_refuse"
    if s["intent"] in ("rule_value", "what_changed") and not s["products"]:
        return "clarify_or_refuse"                                       # "which product's limit?"
    return "retrieve"


def retrieve(s: QAState) -> dict:
    """Two sources of candidates:
    - rule questions: EVERY clause with that rule_key, by metadata filter. The newest clause can't be
      missed by similarity search, so "latest wins" can't silently fall back to the old ₹500.
    - everything: hybrid search (BM25 + vector in Weaviate), filtered by product."""
    pinned = []
    if s["parameter"]:
        pinned = [c for p in s["products"] for c in chunks.by_rule(f"{p}.{s['parameter']}")]
    broaden = s.get("retries", 0) > 0                         # retry: drop the product filter, fetch more
    hits = chunks.search(s["question"], [] if broaden else s["products"], k=80 if broaden else 40)
    return {"pinned": pinned, "candidates": hits}


def similarity(a: str, b: str) -> float:
    """Stand-in for cosine similarity between two embeddings: word overlap (Jaccard)."""
    x, y = set(tokens(a)), set(tokens(b))
    return len(x & y) / len(x | y) if x | y else 0.0


def mmr(ranked: list[Chunk], k: int, lam: float, pinned: list[Chunk]) -> list[Chunk]:
    """Maximal Marginal Relevance: pick one chunk at a time, scoring
         lam * relevance(chunk)  -  (1 - lam) * max similarity(chunk, chunks already picked)
    so a near-duplicate of something already picked loses to a slightly less relevant, NEW fact.
    `ranked` is best-first; relevance comes from that rank (real: the reranker's score)."""
    picked = list(pinned)
    relevance = {c.uuid: 1 - i / len(ranked) for i, c in enumerate(ranked)}
    pool = [c for c in ranked if c.uuid not in {p.uuid for p in picked}]
    while pool and len(picked) < k:
        best = max(pool, key=lambda c: lam * relevance[c.uuid]
                   - (1 - lam) * max((similarity(c.text, p.text) for p in picked), default=0.0))
        picked.append(best)
        pool.remove(best)
    return picked


def rerank(s: QAState) -> dict:
    """Real: a cross-encoder (Cohere Rerank / bge-reranker) scores each (question, chunk) pair and we keep
    the best 12; then MMR picks 6 that aren't near-duplicates. Here the search order stands in for the
    reranker, and word overlap stands in for embedding similarity between chunks.
    The pinned rule clauses always stay: MMR may never drop the proof."""
    ranked = s["candidates"][:12]          # real: sorted by cross-encoder score, best first
    return {"candidates": mmr(ranked, k=6, lam=0.5, pinned=s["pinned"])}


def latest_wins(s: QAState) -> dict:
    """The update rule, at query time. For each rule_key, among its clauses:
    the latest with effective_from <= as_of is CURRENT, older ones are HISTORY (replaced by the next one),
    later ones are UPCOMING. Nothing is stored: 'replaced by' is worked out here, every time."""
    as_of, out = s["as_of"], []
    groups: dict[str | None, list[Chunk]] = {}
    for c in s["candidates"]:
        groups.setdefault(c.rule_key, []).append(c)
    for key, cs in groups.items():
        cs = sorted(cs, key=lambda c: c.effective_from)
        live = [c for c in cs if c.effective_from <= as_of]
        for i, c in enumerate(cs):
            if c.effective_from > as_of:
                role = "upcoming"
            elif key is None or c is live[-1]:
                role = "current"                           # clauses without a rule_key are just in force
            else:
                role = "history"
            nxt = cs[i + 1] if key is not None and i + 1 < len(cs) else None
            out.append(Source(n=0, circular_id=c.circular_id, clause_path=c.clause_path, rule_key=c.rule_key,
                              page=c.page, text=c.text, effective_from=c.effective_from, role=role,
                              replaced_by=nxt.circular_id if nxt and role == "history" else None,
                              replaced_on=nxt.effective_from if nxt and role == "history" else None,
                              pdf_url=circulars[c.circular_id]["pdf_url"]))
    order = {"current": 0, "upcoming": 1, "history": 2}
    out.sort(key=lambda x: (x.rule_key is None, order[x.role]))
    return {"sources": [src.model_copy(update={"n": i + 1}) for i, src in enumerate(out)]}


def generate(s: QAState) -> dict:
    answer, citations, found = fake_answer(s["intent"], s["parameter"], s["sources"])
    return {"answer": answer, "citations": citations, "found": found}


def numbers_in(text: str) -> set[str]:
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*", text)}


def check_grounding(s: QAState) -> dict:
    """Every number in the answer must appear in a source it cites. Cheap, and catches the worst failures."""
    by_n = {src.n: src for src in s["sources"]}
    cited = [by_n[n] for n in s["citations"] if n in by_n]
    evidence = " ".join(f"{c.circular_id} {c.clause_path} {c.text} {c.effective_from}" for c in cited)
    claims = numbers_in(re.sub(r"\[\d+\]", "", s["answer"]))
    ok = s["found"] and bool(cited) and claims <= numbers_in(evidence)
    return {"grounded": ok, "retries": s.get("retries", 0) + (0 if ok else 1)}


def route_grounding(s: QAState) -> str:
    if s["grounded"]:
        return "cite_sources"
    return "retrieve" if s["retries"] <= 1 else "not_found"


def cite_sources(s: QAState) -> dict:
    """The answer plus the proof: circular id, clause, page, the exact text and a link, for every citation."""
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
        lines.append(f"      {src.pdf_url or '(sample circular in this file, no PDF)'}")
    lines.append("Check the source circular before acting.")
    return {"final": "\n".join(lines)}


def clarify_or_refuse(s: QAState) -> dict:
    if s["intent"] == "out_of_scope":
        return {"final": "I only answer questions about NPCI / UPI circulars."}
    return {"final": "Which product do you mean? " + ", ".join(PRODUCTS.values()) + "."}


def not_found(s: QAState) -> dict:
    return {"final": "Not found in the indexed circulars. Try naming the product or the circular number."}


def build_graph():
    g = StateGraph(QAState)
    for fn in (understand, retrieve, rerank, latest_wins, generate, check_grounding,
               cite_sources, clarify_or_refuse, not_found):
        g.add_node(fn.__name__, fn)

    g.add_edge(START, "understand")
    g.add_conditional_edges("understand", route_intent, ["retrieve", "clarify_or_refuse"])
    g.add_edge("retrieve", "rerank")
    g.add_edge("rerank", "latest_wins")
    g.add_edge("latest_wins", "generate")
    g.add_edge("generate", "check_grounding")
    g.add_conditional_edges("check_grounding", route_grounding, ["cite_sources", "retrieve", "not_found"])
    for terminal in ("cite_sources", "clarify_or_refuse", "not_found"):
        g.add_edge(terminal, END)
    # Real: PostgresSaver, so a thread survives restarts. Memory is enough to show follow-ups.
    # The checkpointer serialises state; our pydantic classes must be allow-listed to be read back.
    serde = JsonPlusSerializer(allowed_msgpack_modules=[(__name__, cls.__name__) for cls in (Chunk, Source)])
    return g.compile(checkpointer=InMemorySaver(serde=serde))


# =====================================================================================
# 7. Demo
# =====================================================================================

def main() -> None:
    print("Ingest run 1 (every 10 minutes in the real system):")
    ingest_job(CIRCULARS)
    print("Ingest run 2 (same files again):")
    ingest_job(CIRCULARS[:1])

    app = build_graph()
    questions = [
        ("pm-1", "What is the UPI Lite per transaction limit?"),
        ("pm-1", "And before that?"),
        ("pm-1", "What was the UPI Lite limit on 10 Dec 2024?"),
        ("pm-2", "What is the Tap & Pay limit on PoS without an extra factor of authentication?"),
        ("pm-2", "How many days does the responding party get to respond in an MCC dispute?"),
        ("pm-2", "How did the ISD sections in URCS change?"),
        ("pm-2", "When can a bank update ISD details in URCS?"),
        ("pm-3", "What's the per transaction limit?"),
        ("pm-3", "Who won the cricket match?"),
    ]
    for thread, q in questions:
        out = app.invoke({"question": q}, config={"configurable": {"thread_id": thread}})
        print(f"\n{'=' * 100}\nQ ({thread}): {q}\n{'-' * 100}\n{out['final']}")


if __name__ == "__main__":
    main()
