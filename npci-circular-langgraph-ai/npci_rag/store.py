"""
The chunk store: an in-memory stand-in for Weaviate. APPEND-ONLY: there is add(), but no update and
no delete. Two ways to read it, and the nodes use both:

    by_rule(prefix)   a METADATA FILTER: every clause with that rule_key, oldest first. Exact, no ranking.
    search(query)     a KEYWORD SEARCH (simplified BM25), best first, optionally filtered by product.

[Real] Weaviate: search is hybrid (BM25 for exact words + vectors for meaning, fused), and by_rule is
fetch_objects() with a filter on the rule_key property.

Also here: the two module-level "databases" every other file shares, `chunks` and `circulars`.
[Python] A module is loaded once. `from .store import chunks` in two files gives both files the SAME
object, so what ingest.py adds, nodes.py can read.
"""
from __future__ import annotations

import math
import re
from collections import Counter

from .models import Chunk


def tokens(text: str) -> list[str]:
    """Lower-case words without stop words: "What is the UPI Lite limit?" -> ["upi", "lite", "limit"].
    Commas are dropped first so "₹1,000" becomes the single token "₹1000"."""
    stop = {"the", "a", "an", "of", "for", "to", "in", "on", "is", "what", "and", "or", "be", "shall", "by", "with"}
    # [Python] A list comprehension: [expression for item in iterable if condition].
    return [t for t in re.findall(r"[a-z0-9₹]+", text.lower().replace(",", "")) if t not in stop]


class ChunkStore:
    """Weaviate stand-in. Here search is a BM25-like keyword score only, enough for the sample questions."""

    def __init__(self) -> None:
        self.objects: dict[str, Chunk] = {}             # uuid -> Chunk

    def add(self, new: list[Chunk]) -> None:
        for c in new:
            # Deterministic uuid (a hash of circular id + clause path, see ingest.ingest_circular): ingesting
            # the same circular twice writes the same keys again, so there are never duplicates.
            self.objects[c.uuid] = c

    def by_rule(self, rule_prefix: str) -> list[Chunk]:
        """Metadata filter, not similarity: EVERY clause that states this rule, oldest first.
        [Real] collection.query.fetch_objects(filters=Filter.by_property("rule_key").like(f"{prefix}*"))
        A prefix, so "TAP_AND_PAY.per_txn_limit" also finds "TAP_AND_PAY.per_txn_limit.PoS"."""
        # [Python] sorted(iterable, key=f) sorts by f(item). The (... for ... if ...) inside is a generator
        #          expression: like a list comprehension, but it doesn't build the list first.
        return sorted((c for c in self.objects.values() if c.rule_key and c.rule_key.startswith(rule_prefix)),
                      key=lambda c: c.effective_from)

    def search(self, query: str, products: list[str], k: int) -> list[Chunk]:
        """Keyword search, best first, top k. A simplified BM25:
             score = sum over query words of  idf(word) * tf / (tf + 1.2)
        idf: rare words count more ("lite" beats "upi"). tf / (tf + 1.2): repeating a word helps,
        but less and less (saturation). An empty `products` list means "no product filter"."""
        # [Python] set(a) & set(b) is the intersection: the chunk shares at least one product with the filter.
        pool = [c for c in self.objects.values() if not products or set(products) & set(c.products)]
        # [Python] Counter("a b a".split()) == {"a": 2, "b": 1}: word -> how often it appears.
        docs = {c.uuid: Counter(tokens(c.header + " " + c.text)) for c in pool}
        df = Counter(t for d in docs.values() for t in d)     # document frequency: in how many chunks a word is
        scored = []
        for c in pool:
            tf = docs[c.uuid]
            s = sum(math.log(1 + len(pool) / df[t]) * tf[t] / (tf[t] + 1.2) for t in set(tokens(query)) if t in tf)
            if s > 0:
                scored.append((s, c))
        # [Python] key=lambda x: -x[0] sorts by score, highest first. [:k] keeps the first k.
        return [c for _, c in sorted(scored, key=lambda x: -x[0])[:k]]


# The shared "databases". Filled by ingest.py, read by nodes.py.
chunks = ChunkStore()
circulars: dict[str, dict] = {}        # circular registry: id -> circular dict. [Real] a Postgres table.
