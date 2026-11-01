"""
NPCI Circular Intelligence: learning version of the RAG + LangGraph flow.

Runs fully offline. Everything that would be a cloud service is faked in memory,
with a comment saying what the real thing is:

    S3 + 10-minute job   ->  ingest_job(inbox)            (manifest keyed by content hash)
    Textract + Claude    ->  circulars already given as clauses + change operations
    Postgres ledger      ->  RuleLedger                   (versions with valid_from / valid_to)
    Weaviate             ->  ChunkStore                   (keyword score + the same metadata filters)
    Claude Sonnet        ->  fake_plan() / fake_answer()  (keyword rules)

    pip install langgraph pydantic
    python npci_circular_graph.py

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

OPEN_END = date(9999, 12, 31)          # "still in force": a sentinel instead of NULL
TODAY = date.today()

PRODUCTS = {
    "UPI_LITE": "UPI Lite",
    "TAP_AND_PAY": "UPI Tap & Pay",
    "NRI_INTL_MOBILE": "NRI / international mobile numbers",
    "URCS_GST": "URCS back-office GST / ISD",
    "DISPUTES_MCC": "MCC misclassification disputes",
}
LABELS = {"per_txn_limit": "per transaction limit", "min_claim_amount": "minimum claim amount",
          "response_days": "response time", "isd_section": "ISD section",
          "isd_update_window": "ISD update window", "permitted_country": "permitted country"}


# =====================================================================================
# 1. Data shapes
# =====================================================================================

class RuleVersion(BaseModel):
    """One version of one rule. Postgres table `rule_fact` in the real design."""
    id: int
    product: str
    parameter: str
    scope: str = ""                     # sub-scope ("PoS") or a list member ("Bahrain", "receivable")
    value: float | None = None
    text: str | None = None
    unit: str = ""
    circular_id: str
    clause_path: str
    valid_from: date                    # the EFFECTIVE date, not the issue date
    valid_to: date = OPEN_END           # exclusive: valid on [valid_from, valid_to)
    superseded_by: str | None = None
    status: Literal["ACTIVE", "VOID"] = "ACTIVE"   # VOID = corrected away by a corrigendum, never valid

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.product, self.parameter, self.scope)

    def valid_on(self, d: date) -> bool:
        return self.status == "ACTIVE" and self.valid_from <= d < self.valid_to

    def shown(self) -> str:
        if self.value is None:
            return self.text or ""
        v = int(self.value) if self.value == int(self.value) else self.value
        return f"₹{inr(v)}" if self.unit == "INR" else f"{v} {self.unit}".strip()


def inr(n: int | float) -> str:
    """Indian digit grouping, as circulars write it: 1000000 -> 10,00,000."""
    head, last3 = str(int(n))[:-3], str(int(n))[-3:]
    groups = []
    while len(head) > 2:
        head, groups = head[:-2], [head[-2:]] + groups
    return ",".join(([head] if head else []) + groups + [last3])


class Chunk(BaseModel):
    """One clause of one circular. A Weaviate object in the real design."""
    uuid: str
    circular_id: str
    clause_path: str
    text: str
    header: str                         # contextual header, embedded together with the text
    products: list[str]
    page: int
    effective_from: date
    effective_to: date = OPEN_END
    superseded_by: str | None = None
    partly_changed_by: str | None = None   # some, not all, rules of this clause were changed
    visible: bool = False               # True only after the whole circular is written

    def valid_on(self, d: date) -> bool:
        return self.effective_from <= d < self.effective_to


class QueryPlan(BaseModel):
    """What Claude extracts from the question (structured output)."""
    intent: Literal["rule_value", "what_changed", "explain", "out_of_scope"]
    products: list[str]
    parameter: str | None
    as_of: date | None


class Source(BaseModel):
    """A numbered piece of evidence: shown to the LLM, then to the user as proof."""
    n: int
    kind: Literal["rule", "clause"]
    circular_id: str
    clause_path: str
    scope: str = ""
    page: int | None
    text: str
    effective_from: date
    effective_to: date
    role: Literal["current", "history", "upcoming"]
    superseded_by: str | None
    partly_changed_by: str | None = None
    pdf_url: str | None


# =====================================================================================
# 2. Sample circulars: what OCR + Claude extraction would hand to the ingest step.
#    "changes" are CHANGE OPERATIONS, not raw facts: the op says what the circular does
#    to the rules already in force (see RuleLedger.apply_change).
# =====================================================================================

NPCI = "https://www.npci.org.in/uploads/"

CIRCULARS = [
    {   # SYNTHETIC placeholder: the older UPI Lite limit
        "id": "OC-L1", "subject": "UPI Lite: transaction limits", "issue_date": "2023-10-01",
        "effective_from": "2023-10-01", "products": ["UPI_LITE"], "pdf_url": None,
        "clauses": [
            ("Guidelines > 3", 1, "The per transaction limit for UPI Lite shall be ₹500."),
            ("Guidelines > 4", 1, "UPI Lite payments up to the per transaction limit shall not require UPI PIN."),
        ],
        "changes": [{"op": "NEW", "product": "UPI_LITE", "parameter": "per_txn_limit", "value": 500,
                     "unit": "INR", "clause": "Guidelines > 3"}],
    },
    {   # SYNTHETIC placeholder: issued 2 Dec, effective 16 Dec -> issue date != effective date
        "id": "OC-L2", "subject": "UPI Lite: enhancement of per transaction limit", "issue_date": "2024-12-02",
        "effective_from": "2024-12-16", "products": ["UPI_LITE"], "pdf_url": None,
        "clauses": [
            ("Main", 1, "With reference to circular OC-L1, the UPI Lite per transaction limit is revised."),
            ("Guidelines > 2(a)", 1, "The per transaction limit for UPI Lite is enhanced from ₹500 to ₹1,000, "
                                     "effective 16 December 2024."),
        ],
        "changes": [{"op": "REPLACE", "product": "UPI_LITE", "parameter": "per_txn_limit", "value": 1000,
                     "unit": "INR", "clause": "Guidelines > 2(a)"}],
    },
    {
        "id": "UPI-OC-186A-2026-27", "subject": "Enhancement - UPI Tap & Pay on Point of Sale (PoS)",
        "issue_date": "2026-09-10", "effective_from": "2026-09-10", "products": ["TAP_AND_PAY"],
        "pdf_url": NPCI + "UPI_I_OC_No_186_A_I_Enhancement_UPI_Tap_and_Pay_on_Point_of_Sale_Po_S_e695625b85.pdf",
        "clauses": [
            ("Main", 1, "With reference to UPI Operating Circular NPCI/UPI/OC-186/2023-24 dated 19th December 2023, "
                        "UPI Tap & Pay through NFC on QR was introduced. UPI Tap & Pay shall now be extended to "
                        "Point of Sale (PoS) terminals."),
            ("Key Guidelines > 1", 1, "Members and UPI Application Providers shall ensure that UPI Tap & Pay "
                                      "transactions on PoS terminals are accepted only for Person-to-Merchant (P2M) "
                                      "transactions."),
            ("Key Guidelines > 3", 1, "Members and UPI Application Providers shall ensure that per transaction limit "
                                      "is capped at ₹5000, up to which additional factor of authentication shall "
                                      "not be required."),
            ("UPI Application Provider > 2", 2, "UPI Application Providers shall ensure that device lock is enabled "
                                                "as a prerequisite for activating UPI Tap & Pay. The device shall be "
                                                "in an unlocked state at the time of initiating a transaction."),
        ],
        # Tap & Pay on QR (OC-186) keeps its own rules: PoS is a NEW SCOPE, not a replacement
        "changes": [{"op": "EXTEND_SCOPE", "product": "TAP_AND_PAY", "parameter": "per_txn_limit", "scope": "PoS",
                     "value": 5000, "unit": "INR", "clause": "Key Guidelines > 3"}],
    },
    {   # RECONSTRUCTED from OC-229A's own summary of it (we don't have the OC-229 PDF)
        "id": "UPI-OC-229-2025-26", "subject": "ISD/GSTIN option in URCS (reconstructed)",
        "issue_date": "2025-11-12", "effective_from": "2025-11-17", "products": ["URCS_GST"], "pdf_url": None,
        "clauses": [
            ("Main", 1, "The Input Service Distributor (ISD)/GSTIN option would be enabled in the URCS system for "
                        "both payable and receivable sections."),
        ],
        "changes": [{"op": "ADD_MEMBER", "product": "URCS_GST", "parameter": "isd_section",
                     "members": ["payable", "receivable"], "clause": "Main"}],
    },
    {
        "id": "UPI-OC-229A-2026-27", "subject": "Implementation of Revised ISD-GSTIN Option in URCS Back-Office System",
        "issue_date": "2026-08-24", "effective_from": "2026-09-15", "products": ["URCS_GST"],
        "pdf_url": NPCI + "UPI_OC_229_A_ISD_GSTIN_Input_Service_Distributor_Option_in_UPI_URCS_898c087730.pdf",
        "clauses": [
            ("Main > a", 1, "The receivable section has been removed from the ISD functionality. Users will now be "
                            "able to update ISD details only for the payable section."),
            ("Main > c", 1, "Users are permitted to update only one GSTIN or ISD per product per bank in a month."),
            ("Main > d", 1, "ISD/GSTIN update should be submitted in URCS between the 15th and 31st or last day of "
                            "every month. Back Office system will not permit users to update ISD/GSTIN details "
                            "between the 1st to 14th of every month."),
            ("Go-Live", 1, "Revised ISD-GSTIN functionality will be made live on Sep 15, 2026."),
        ],
        "changes": [
            {"op": "REMOVE_MEMBER", "product": "URCS_GST", "parameter": "isd_section", "member": "receivable",
             "clause": "Main > a"},
            {"op": "NEW", "product": "URCS_GST", "parameter": "isd_update_window", "text": "15th to month end",
             "clause": "Main > d"},
        ],
    },
    {
        "id": "UPI-OC-239-2026-27", "subject": "UPI - Process for Resolution of MCC Misclassification related disputes",
        "issue_date": "2026-10-14", "effective_from": "2026-10-14", "products": ["DISPUTES_MCC"],
        "pdf_url": NPCI + "UPI_OC_239_UPI_Process_for_Resolution_of_MCC_Misclassification_related_disputes_"
                          "7770320097.pdf",
        "clauses": [
            ("2.3 Claim Eligibility > a(i)", 5, "Amount Threshold for a Claim: Minimum aggregate Claim amount must "
                                                "be INR 10,00,000 (Ten Lakhs rupees only)."),
            ("4.2 Pre-Compliance Response > a", 8, "Responding Party must submit response in 23 calendar days. On "
                                                   "expiry of 23rd day, if no response is received, responding party "
                                                   "will have a period of 7 calendar days as grace period."),
            ("4.4 Panel for Resolution of Disputes > b", 10, "Panel shall endeavor to review the Claim and resolve "
                                                             "the same within 90 calendar days from Panel Reference "
                                                             "Date."),
        ],
        "changes": [
            {"op": "NEW", "product": "DISPUTES_MCC", "parameter": "min_claim_amount", "value": 1000000,
             "unit": "INR", "clause": "2.3 Claim Eligibility > a(i)"},
            {"op": "NEW", "product": "DISPUTES_MCC", "parameter": "response_days", "value": 23, "unit": "days",
             "clause": "4.2 Pre-Compliance Response > a"},
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
                        "Thailand. All compliance requirements shall remain as is."),
        ],
        # a list grows: one row per new member; the 12 existing members are untouched
        "changes": [{"op": "ADD_MEMBER", "product": "NRI_INTL_MOBILE", "parameter": "permitted_country",
                     "members": ["Bahrain", "Bhutan", "Brazil", "Germany", "Greece", "Ireland", "Italy", "Japan",
                                 "Kuwait", "Maldives", "Nepal", "Netherlands", "New Zealand", "Philippines",
                                 "Portugal", "South Africa", "Spain", "Sweden", "Thailand"],
                     "clause": "Main"}],
    },
]


# =====================================================================================
# 3. Stores (in memory). Real: Postgres for the ledger, Weaviate for chunks.
# =====================================================================================

class RuleLedger:
    """Postgres stand-in. In SQL, a partial unique index guarantees one open version per rule.

    apply_change() is the ONE place that turns a change operation into row changes.
    Every op is "close some rows, open some rows". Nothing is ever deleted, so every
    query stays the same: rows valid on the asked date.
    """

    def __init__(self) -> None:
        self.rows: list[RuleVersion] = []
        self.circulars: dict[str, dict] = {}

    def versions(self, product: str, parameter: str | None) -> list[RuleVersion]:
        rows = [r for r in self.rows if r.status == "ACTIVE" and r.product == product
                and (parameter is None or r.parameter == parameter)]
        return sorted(rows, key=lambda r: (r.parameter, r.scope, r.valid_from))

    def _current(self, key: tuple[str, str, str], d: date) -> RuleVersion | None:
        return next((r for r in self.rows if r.key == key and r.valid_on(d)), None)

    def _open(self, ch: dict, cid: str, valid_from: date, *, scope: str | None = None, text: str | None = None,
              valid_to: date = OPEN_END, like: RuleVersion | None = None) -> RuleVersion:
        base = like.model_dump(exclude={"id", "valid_from", "valid_to", "superseded_by", "status"}) if like else {
            "product": ch["product"], "parameter": ch["parameter"], "scope": ch.get("scope", ""),
            "value": ch.get("value"), "text": ch.get("text"), "unit": ch.get("unit", ""),
            "circular_id": cid, "clause_path": ch["clause"]}
        if scope is not None:
            base["scope"] = scope
        if text is not None:
            base["text"] = text
        row = RuleVersion(id=len(self.rows) + 1, valid_from=valid_from, valid_to=valid_to, **base)
        self.rows.append(row)
        return row

    def _close(self, row: RuleVersion, on: date, by: str) -> RuleVersion:
        # In production a reviewer approves every close before it happens (maker-checker).
        closed = row.model_copy(update={"valid_to": on, "superseded_by": by})
        self.rows[self.rows.index(row)] = closed
        return closed

    def apply_change(self, ch: dict, cid: str, eff: date) -> tuple[list[str], list[RuleVersion]]:
        """Returns (notes for the log, rows that were closed or voided)."""
        op, notes, closed = ch["op"], [], []
        key = (ch.get("product"), ch.get("parameter"), ch.get("scope", ""))

        if op in ("NEW", "REPLACE", "EXTEND_SCOPE", "RESTATE"):
            cur = self._current(key, eff)
            if cur and (cur.value, cur.text) == (ch.get("value"), ch.get("text")):
                notes.append(f"{op}: {cur.shown()} restated, no new version ({cid} kept as an extra citation)")
            else:
                if cur:
                    closed.append(self._close(cur, eff, cid))
                new = self._open(ch, cid, eff)
                notes.append(f"{op}: " + (f"closed {cur.shown()} ({cur.circular_id}) on {eff}, " if cur else "")
                             + f"opened {LABELS[new.parameter]}" + (f" [{new.scope}]" if new.scope else "")
                             + f" = {new.shown()}")

        elif op == "ADD_MEMBER":                                  # a list grows: one row per new member
            for m in ch["members"]:
                if not self._current((ch["product"], ch["parameter"], m), eff):
                    self._open(ch, cid, eff, scope=m, text="allowed")
            notes.append(f"ADD_MEMBER: {len(ch['members'])} {LABELS[ch['parameter']]} rows opened, "
                         f"existing members untouched")

        elif op == "REMOVE_MEMBER":                               # a list shrinks: close, open nothing
            cur = self._current((ch["product"], ch["parameter"], ch["member"]), eff)
            if cur:
                closed.append(self._close(cur, eff, cid))
                notes.append(f"REMOVE_MEMBER: closed {LABELS[cur.parameter]} [{cur.scope}] "
                             f"({cur.circular_id}) on {eff}, nothing opened")

        elif op == "TEMPORARY":                                   # e.g. a relaxation until a date, then back
            until = date.fromisoformat(ch["until"])
            cur = self._current(key, eff)
            if cur:
                closed.append(self._close(cur, eff, cid))
            temp = self._open(ch, cid, eff, valid_to=until)
            if cur:
                self._open(ch, cid, until, like=cur)              # the old value again, citing the old circular
            notes.append(f"TEMPORARY: {temp.shown()} from {eff} until {until}"
                         + (f", then {cur.shown()} again" if cur else ""))

        elif op == "CORRECT":                                     # corrigendum: the wrong row was never valid
            for wrong in [r for r in self.rows if r.key == key and r.circular_id == ch["target"]
                          and r.status == "ACTIVE"]:
                void = wrong.model_copy(update={"status": "VOID", "superseded_by": cid})
                self.rows[self.rows.index(wrong)] = void
                closed.append(void)
                fixed = self._open(ch, cid, wrong.valid_from, valid_to=wrong.valid_to)
                notes.append(f"CORRECT: {wrong.shown()} ({wrong.circular_id}) voided, "
                             f"{fixed.shown()} from {wrong.valid_from} instead")

        elif op == "WITHDRAW":                                    # rescinded: the previous value comes back
            for row in [r for r in self.rows if r.circular_id == ch["target"] and r.valid_on(eff)]:
                closed.append(self._close(row, eff, cid))
                prev = next((p for p in self.rows if p.key == row.key and p.status == "ACTIVE"
                             and p.valid_to == row.valid_from), None)       # the version just before it
                if prev:
                    self._open(ch, cid, eff, like=prev)
                notes.append(f"WITHDRAW: closed {row.shown()} ({row.circular_id}) on {eff}"
                             + (f", {prev.shown()} back in force" if prev else ""))

        elif op == "REFERENCE_ONLY":                              # cites another circular, changes nothing
            notes.append(f"REFERENCE_ONLY: link {cid} -> {ch['target']}, no rule changed")
        return notes, closed

    def still_cited(self, circular_id: str, clause_path: str, after: date) -> bool:
        return any(r.circular_id == circular_id and r.clause_path == clause_path and r.status == "ACTIVE"
                   and r.valid_to > after for r in self.rows)


def tokens(text: str) -> list[str]:
    stop = {"the", "a", "an", "of", "for", "to", "in", "on", "is", "what", "and", "or", "be", "shall", "by", "with"}
    return [t for t in re.findall(r"[a-z0-9₹]+", text.lower().replace(",", "")) if t not in stop]


class ChunkStore:
    """Weaviate stand-in. Real search is hybrid (BM25 + vector); here it is a BM25-like keyword score.
    The metadata filters are the part that matters, and they are the same as in Weaviate."""

    def __init__(self) -> None:
        self.objects: dict[str, Chunk] = {}

    def upsert(self, chunks: list[Chunk]) -> None:
        for c in chunks:
            self.objects[c.uuid] = c                    # deterministic uuid: re-ingest overwrites, no duplicates

    def patch(self, circular_id: str, clause_path: str, **props) -> None:
        """Metadata-only update. Real Weaviate keeps the stored vector: no re-embedding."""
        for u, c in self.objects.items():
            if c.circular_id == circular_id and c.clause_path == clause_path:
                self.objects[u] = c.model_copy(update=props)

    def set_visible(self, circular_id: str) -> None:
        for u, c in self.objects.items():
            if c.circular_id == circular_id:
                self.objects[u] = c.model_copy(update={"visible": True})

    def by_clause(self, circular_id: str, clause_path: str) -> list[Chunk]:
        return [c for c in self.objects.values()
                if c.visible and c.circular_id == circular_id and c.clause_path == clause_path]

    def search(self, query: str, as_of: date | None, products: list[str], k: int) -> list[Chunk]:
        # Weaviate: filters=effective_from <= as_of AND effective_to > as_of AND products contains_any [...]
        pool = [c for c in self.objects.values()
                if c.visible and (as_of is None or c.valid_on(as_of))
                and (not products or set(products) & set(c.products))]
        docs = {c.uuid: Counter(tokens(c.header + " " + c.text)) for c in pool}
        df = Counter(t for d in docs.values() for t in d)
        scored = []
        for c in pool:
            tf = docs[c.uuid]
            s = sum(math.log(1 + len(pool) / df[t]) * tf[t] / (tf[t] + 1.2) for t in set(tokens(query)) if t in tf)
            if s > 0:
                scored.append((s, c))
        return [c for _, c in sorted(scored, key=lambda x: -x[0])[:k]]


ledger, chunks = RuleLedger(), ChunkStore()


# =====================================================================================
# 4. Ingestion. Real: EventBridge rate(10 minutes) -> one task -> S3 -> Textract -> Claude.
# =====================================================================================

manifest: dict[str, str] = {}          # sha256 -> status. A Postgres table in the real design.


def ingest_circular(c: dict) -> list[str]:
    cid, eff = c["id"], date.fromisoformat(c["effective_from"])
    ledger.circulars[cid] = c

    # (1) one chunk per clause, with a contextual header, written INVISIBLE first
    chunks.upsert([
        Chunk(uuid=hashlib.sha1(f"{cid}:{path}".encode()).hexdigest(), circular_id=cid, clause_path=path,
              text=text, header=f"[{cid} | {c['subject']} | {c['issue_date']} | {path}]",
              products=c["products"], page=page, effective_from=eff)
        for path, page, text in c["clauses"]
    ])

    # (2) change operations -> ledger. Closing happens here; nothing is overwritten or deleted.
    notes = []
    for ch in c["changes"]:
        op_notes, closed = ledger.apply_change(ch, cid, eff)
        notes += op_notes
        # (3) the closed rule's clause chunk: close it only if no other open rule still cites it
        for row in closed:
            if ledger.still_cited(row.circular_id, row.clause_path, after=eff):
                chunks.patch(row.circular_id, row.clause_path, partly_changed_by=cid)
            else:
                chunks.patch(row.circular_id, row.clause_path, effective_to=eff, superseded_by=cid)

    # (4) only now can queries see the new circular
    chunks.set_visible(cid)
    return notes


def ingest_job(inbox: list[dict]) -> None:
    """One scheduled run. Real: take a lock (pg_try_advisory_lock), list S3, hash each new PDF."""
    for c in inbox:
        sha = hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest()
        if manifest.get(sha) == "INDEXED":
            print(f"  skip {c['id']}: same content already indexed")
            continue
        notes = ingest_circular(c)
        manifest[sha] = "INDEXED"
        print(f"  indexed {c['id']}" + "".join(f"\n      {n}" for n in notes))


def print_ledger() -> None:
    print("Rule ledger (nothing is ever deleted; list members collapsed):")
    rows, i = ledger.rows, 0
    while i < len(rows):
        r, j = rows[i], i
        while j + 1 < len(rows) and (rows[j + 1].parameter, rows[j + 1].circular_id, rows[j + 1].valid_to) == \
                (r.parameter, r.circular_id, r.valid_to) and r.parameter == "permitted_country":
            j += 1
        scope = r.scope if j == i else f"{j - i + 1} members"
        to = "open" if r.valid_to == OPEN_END else str(r.valid_to)
        print(f"  {r.product:<16}{r.parameter:<20}{scope:<13}{(r.shown() if j == i else ''):<20}"
              f"{r.circular_id:<22}{r.valid_from} -> {to:<11}{r.superseded_by or ''}")
        i = j + 1


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


def fake_answer(intent: str, sources: list[Source]) -> tuple[str, list[int], bool]:
    """Real: Claude Sonnet with the sources in the prompt and structured output (answer, citations, found)."""
    rules = [s for s in sources if s.kind == "rule"]
    clauses = [s for s in sources if s.kind == "clause"]
    clause_of = {(s.circular_id, s.clause_path): s.n for s in clauses}

    def proof(r: Source) -> str:
        m = clause_of.get((r.circular_id, r.clause_path))
        return f" [{r.n}]" + (f"[{m}]" if m else "")

    def value(r: Source) -> str:
        return r.text.split(" = ")[1]

    if intent == "what_changed" and rules:
        parts = []
        for scope in dict.fromkeys(r.scope for r in rules):            # one history line per scope / member
            rs = [r for r in rules if r.scope == scope]
            steps = [f"{value(r)} from {r.effective_from} ({r.circular_id}){proof(r)}" for r in rs]
            last = rs[-1]
            if last.effective_to != OPEN_END and not any(r.effective_from == last.effective_to for r in rs):
                why = next((c for c in clauses if c.circular_id == last.superseded_by
                            and scope.lower() in c.text.lower()), None)
                steps.append(f"ended {last.effective_to} ({last.superseded_by})" + (f" [{why.n}]" if why else ""))
            parts.append((f"{scope}: " if scope else "") + " -> ".join(steps))
        text = "History: " + "; ".join(parts) + "."
    elif intent == "rule_value" and any(r.role == "current" for r in rules):
        parts = []
        for r in rules:
            if r.role == "current":
                parts.append(f"{r.text.replace(' = ', ' is ')} ({r.circular_id}, {r.clause_path}), "
                             f"in force since {r.effective_from}{proof(r)}.")
            elif r.role == "upcoming":
                parts.append(f"It changes to {value(r)} from {r.effective_from} ({r.circular_id}){proof(r)}.")
        text = " ".join(parts)
    else:
        current = [s for s in clauses if s.role == "current"]
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
    ledger_rows: list[RuleVersion]
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
        "as_of": plan.as_of or TODAY, "ledger_rows": [], "candidates": [], "sources": [],
        "answer": "", "citations": [], "found": False, "grounded": False, "retries": 0, "final": "",
    }


def route_intent(s: QAState) -> str:
    if s["intent"] == "out_of_scope":
        return "clarify_or_refuse"
    if s["intent"] in ("rule_value", "what_changed"):
        return "rule_lookup" if s["products"] else "clarify_or_refuse"   # "which product's limit?"
    return "retrieve"


def rule_lookup(s: QAState) -> dict:
    """Exact values come from the ledger (SQL), never from similarity search."""
    rows = []
    for p in s["products"]:
        history = ledger.versions(p, s["parameter"])
        if s["intent"] == "what_changed":
            rows += history
        else:
            rows += [r for r in history if r.valid_on(s["as_of"])]
            rows += [r for r in history if r.valid_from > s["as_of"]][:1]      # the next change, if any
    return {"ledger_rows": rows}


def retrieve(s: QAState) -> dict:
    broaden = s.get("retries", 0) > 0                         # retry: drop the product filter, fetch more
    as_of = None if s["intent"] == "what_changed" else s["as_of"]
    hits = chunks.search(s["question"], as_of, [] if broaden else s["products"], k=40 if broaden else 20)
    proof = [c for r in s["ledger_rows"] for c in chunks.by_clause(r.circular_id, r.clause_path)]
    seen, out = set(), []
    for c in proof + hits:                                    # the clauses that state the rule go first
        if c.uuid not in seen:
            seen.add(c.uuid)
            out.append(c)
    return {"candidates": out}


def rerank(s: QAState) -> dict:
    """Real: a cross-encoder (Cohere Rerank / bge-reranker) scores question + chunk together; keep 6."""
    return {"candidates": s["candidates"][:6]}


def resolve_versions(s: QAState) -> dict:
    """Number every piece of evidence and label it current / history / upcoming for the asked date."""
    as_of, out = s["as_of"], []

    def role(f: date, t: date) -> str:
        return "current" if f <= as_of < t else ("upcoming" if f > as_of else "history")

    for r in s["ledger_rows"]:
        page = next((c.page for c in chunks.by_clause(r.circular_id, r.clause_path)), None)
        label = f"{PRODUCTS[r.product]} {LABELS[r.parameter]}" + (f" ({r.scope})" if r.scope else "")
        out.append(Source(n=len(out) + 1, kind="rule", circular_id=r.circular_id, clause_path=r.clause_path,
                          scope=r.scope, page=page, text=f"{label} = {r.shown()}", effective_from=r.valid_from,
                          effective_to=r.valid_to, role=role(r.valid_from, r.valid_to),
                          superseded_by=r.superseded_by, pdf_url=ledger.circulars[r.circular_id]["pdf_url"]))
    for c in s["candidates"]:
        out.append(Source(n=len(out) + 1, kind="clause", circular_id=c.circular_id, clause_path=c.clause_path,
                          page=c.page, text=c.text, effective_from=c.effective_from, effective_to=c.effective_to,
                          role=role(c.effective_from, c.effective_to), superseded_by=c.superseded_by,
                          partly_changed_by=c.partly_changed_by, pdf_url=ledger.circulars[c.circular_id]["pdf_url"]))
    return {"sources": out}


def generate(s: QAState) -> dict:
    answer, citations, found = fake_answer(s["intent"], s["sources"])
    return {"answer": answer, "citations": citations, "found": found}


def numbers_in(text: str) -> set[str]:
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*", text)}


def check_grounding(s: QAState) -> dict:
    """Every number in the answer must appear in a source it cites. Cheap, and catches the worst failures."""
    by_n = {src.n: src for src in s["sources"]}
    cited = [by_n[n] for n in s["citations"] if n in by_n]
    evidence = " ".join(f"{c.circular_id} {c.clause_path} {c.text} {c.effective_from} {c.effective_to} "
                        f"{c.superseded_by or ''}" for c in cited)
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
    groups: dict[tuple[str, str], list[Source]] = {}       # a rule row and its clause are one piece of proof
    for n in s["citations"]:
        groups.setdefault((by_n[n].circular_id, by_n[n].clause_path), []).append(by_n[n])
    lines = [s["answer"], "", "Proof (check it in the circular):"]
    for group in groups.values():
        src = next((g for g in group if g.kind == "clause"), group[0])
        status = src.role.upper()
        if src.superseded_by and src.effective_to != OPEN_END:
            status += f", superseded by {src.superseded_by} on {src.effective_to}"
        if src.partly_changed_by:
            status += f", partly changed by {src.partly_changed_by}"
        marks = "".join(f"[{g.n}]" for g in group)
        lines.append(f"  {marks} {src.circular_id} > {src.clause_path}, page {src.page}, "
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
    for fn in (understand, rule_lookup, retrieve, rerank, resolve_versions, generate, check_grounding,
               cite_sources, clarify_or_refuse, not_found):
        g.add_node(fn.__name__, fn)

    g.add_edge(START, "understand")
    g.add_conditional_edges("understand", route_intent, ["rule_lookup", "retrieve", "clarify_or_refuse"])
    g.add_edge("rule_lookup", "retrieve")           # still fetch the clause text, to cite it as proof
    g.add_edge("retrieve", "rerank")
    g.add_edge("rerank", "resolve_versions")
    g.add_edge("resolve_versions", "generate")
    g.add_edge("generate", "check_grounding")
    g.add_conditional_edges("check_grounding", route_grounding, ["cite_sources", "retrieve", "not_found"])
    for terminal in ("cite_sources", "clarify_or_refuse", "not_found"):
        g.add_edge(terminal, END)
    # Real: PostgresSaver, so a thread survives restarts. Memory is enough to show follow-ups.
    # The checkpointer serialises state; our pydantic classes must be allow-listed to be read back.
    serde = JsonPlusSerializer(allowed_msgpack_modules=[(__name__, cls.__name__)
                                                        for cls in (RuleVersion, Chunk, Source)])
    return g.compile(checkpointer=InMemorySaver(serde=serde))


# =====================================================================================
# 7. Demo
# =====================================================================================

def main() -> None:
    print("Ingest run 1 (every 10 minutes in the real system):")
    ingest_job(CIRCULARS)
    print("Ingest run 2 (same files again):")
    ingest_job(CIRCULARS[:1])
    print()
    print_ledger()

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
