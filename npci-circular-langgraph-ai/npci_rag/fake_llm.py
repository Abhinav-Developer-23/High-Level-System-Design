"""
Fake Claude: keyword rules standing in for the two LLM calls, so the demo runs offline and gives the
same output every time. The nodes call these exactly where they would call the LLM:

    fake_plan    used by nodes.understand   [Real] structured output into QueryPlan
    fake_answer  used by nodes.generate     [Real] a cited answer from the numbered sources

[Real] with LangChain:
    from langchain_anthropic import ChatAnthropic
    llm = ChatAnthropic(model="claude-sonnet-5-5", max_tokens=2048)
    plan = llm.with_structured_output(QueryPlan).invoke([("system", PLANNER_PROMPT), ("human", question)])

Swapping these for real calls changes nothing in the graph: same inputs, same outputs, same state keys.
That is the point of keeping the LLM behind a function.
"""
from __future__ import annotations

import re
from datetime import date

from .data import LABELS, PRODUCTS
from .models import QueryPlan, Source

# Which words in a question point at which product.
KEYWORDS = {
    "UPI_LITE": ["lite"],
    "TAP_AND_PAY": ["tap", "pos", "nfc"],
    "URCS_GST": ["isd", "gstin", "gst", "urcs"],
    "DISPUTES_MCC": ["mcc", "dispute", "claim", "prd"],
    "NRI_INTL_MOBILE": ["countries", "country", "international", "nri"],
}
MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()


def parse_date(text: str) -> date | None:
    """ "... on 10 Dec 2024?" -> date(2024, 12, 10). None when the question names no date."""
    m = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]{3})[a-z]*\.?\s+(\d{4})", text.lower())
    # [Python] m[3] is the same as m.group(3): the third (...) group of the regex.
    return date(int(m[3]), MONTHS.index(m[2]) + 1, int(m[1])) if m and m[2] in MONTHS else None


def fake_plan(question: str, previous: dict) -> QueryPlan:
    """Read the question: which products, which rule parameter, what kind of question, which date.
    `previous` holds the last turn's products/parameter, for follow-ups like "And before that?"."""
    q = question.lower()
    # \b is a word boundary, so "pos" matches "PoS" but not "possible".
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
        # [Python] `a or b` gives a if a is truthy, else b: keep a new parameter if one was found.
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


# An amount in the text: "₹1,000", "INR 10,00,000" or "23 calendar days".
AMOUNT = r"(?:₹|INR )\s?\d(?:[\d,]*\d)?|\b\d+ calendar days\b"
AMOUNT_RE = re.compile(AMOUNT)
# "from ₹500 to ₹1,000": group(1) is the old value, group(2) the new one.
FROM_TO_RE = re.compile(rf"from ({AMOUNT}) to ({AMOUNT})")


def fake_answer(intent: str, parameter: str | None, sources: list[Source]) -> tuple[str, list[int], bool]:
    """Write the answer from the numbered sources. Returns (answer text, cited [n] numbers, found?).
    [Real] Claude Sonnet with the numbered sources in the prompt, told that CURRENT beats HISTORY and to
    cite every fact as [n], with structured output (answer, citations, found)."""

    # [Python] Functions defined inside a function: small helpers only this function uses.
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
        # The history of the rule, oldest first: "₹500 from 2023-10-01 (OC-L1) [2] -> ₹1,000 from ..."
        steps = [f"{value(s)} from {s.effective_from} ({s.circular_id}) [{s.n}]"
                 for s in sorted(rules, key=lambda s: s.effective_from)]
        text = f"{label(rules[0])}: " + " -> ".join(steps) + "."
    elif intent == "rule_value" and any(s.role == "current" for s in rules):
        # The current value first, then what's coming and what it used to be.
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
        # "explain" questions: quote the best current clauses.
        current = [s for s in sources if s.role == "current"]
        if not current:
            return "", [], False                         # found=False: check_grounding will fail it
        text = " ".join(f"{s.text} [{s.n}]" for s in current[:2])
    # The citations are the [n] markers actually written in the text, so they can't disagree with it.
    return text, sorted({int(n) for n in re.findall(r"\[(\d+)\]", text)}), True
