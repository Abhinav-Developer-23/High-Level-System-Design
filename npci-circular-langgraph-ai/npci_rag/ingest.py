"""
Ingestion: the job that fills the store. It is NOT part of the LangGraph graph; the graph only reads
what this job wrote.

[Real] EventBridge rate(10 minutes) -> one ECS task -> list new PDFs in S3 (date prefixes + manifest)
-> Textract OCR -> Claude extraction into clauses + metadata -> OpenAI embeddings -> Weaviate.
A Postgres advisory lock makes sure only one run works at a time.

Two rules that make it safe to run every 10 minutes:
    1. Idempotent: a manifest keyed by the file's SHA-256. Same content seen again -> skipped.
    2. Append-only: a new circular only ADDS chunks. Older circulars are never edited or deleted,
       so the ₹1,000 clause simply sits next to the ₹500 one, and the query side picks the winner.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date

from .models import Chunk
from .store import chunks, circulars

manifest: dict[str, str] = {}          # sha256 of the file -> status. [Real] a Postgres table.


def ingest_circular(c: dict) -> int:
    """Write each clause ONCE with its static metadata. Returns how many chunks were written."""
    cid = c["id"]
    circulars[cid] = c
    new = [Chunk(uuid=hashlib.sha1(f"{cid}:{path}".encode()).hexdigest(), circular_id=cid, clause_path=path,
                 text=text,
                 # The header is embedded WITH the text, so a clause like "capped at ₹5000" still carries
                 # which circular and topic it belongs to when it is searched on its own.
                 header=f"[{cid} | {c['subject']} | {c['issue_date']} | {path}]",
                 products=c["products"], rule_key=rule_key, page=page,
                 issue_date=date.fromisoformat(c["issue_date"]), effective_from=date.fromisoformat(c["effective_from"]))
           # [Python] Tuple unpacking in a loop: each clause tuple is split into four names.
           for path, page, text, rule_key in c["clauses"]]
    chunks.add(new)
    return len(new)


def ingest_job(inbox: list[dict], verbose: bool = True) -> None:
    """One scheduled run over the files in the inbox.
    [Real] take the lock (pg_try_advisory_lock), list S3 by date prefix, hash each new PDF.
    The content hash is the idempotency key: the same file uploaded twice (or the job crashing and
    running again) is skipped, so nothing is indexed twice."""
    for c in inbox:
        sha = hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest()
        if manifest.get(sha) == "INDEXED":
            if verbose:
                print(f"  skip {c['id']}: same content already indexed")
            continue
        n = ingest_circular(c)
        # Marked INDEXED only after every chunk is written: a crash before this line means the next run
        # redoes the file, and the deterministic uuids overwrite instead of duplicating.
        manifest[sha] = "INDEXED"
        if verbose:
            print(f"  indexed {c['id']}: {n} chunks appended (effective {c['effective_from']})")
