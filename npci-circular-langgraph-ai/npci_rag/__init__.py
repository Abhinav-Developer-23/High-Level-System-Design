"""
npci_rag: NPCI Circular Intelligence, the learning version of the RAG + LangGraph flow.
========================================================================================

A question-answering bot over NPCI circulars, written as a LangGraph graph. Ask
"What is the UPI Lite per transaction limit?" and it answers AND shows the proof: circular id,
clause, page, the exact sentence and a link to the PDF. It runs fully offline: S3, Textract,
Weaviate and Claude are replaced by small in-memory fakes, each marked with a [Real] comment.

RUN IT (from the npci-circular-langgraph-ai folder, the one that CONTAINS this package)
    pip install langgraph pydantic
    python -m npci_rag                       # the demo: ingest + 9 questions
    python -m npci_rag --help                # all the learning commands (see README.md)

    [Python] `python -m npci_rag` runs the package's __main__.py. It must be started from the
    parent folder, so Python can find the `npci_rag` folder as a package.

THE FILES, and the order to read them in
    graph.py      START HERE. "LangGraph in plain words" at the top, then build_graph(): the wiring.
    state.py      QAState: the dict every node reads and writes.
    nodes.py      The nodes, in the order they run (understand -> retrieve -> ... -> cite_sources).
    routers.py    The two functions that choose the next node (the conditional edges).
    __main__.py   Running the graph: invoke, stream, threads, get_state, get_state_history.

    Then the "business" part, which the nodes call:
    models.py     Chunk, QueryPlan, Source: the records passed around.
    data.py       The sample circulars, and the product / parameter names.
    store.py      ChunkStore: the Weaviate stand-in (keyword search + metadata filter).
    ingest.py     The 10-minute ingest job: content-hash manifest, append-only writes.
    fake_llm.py   fake_plan / fake_answer: keyword rules standing in for the two Claude calls.

    How the files depend on each other (an arrow means "imports"):
        __main__ -> graph -> nodes -> store, fake_llm, models, data
                         -> routers
                         -> state  -> models
        __main__ -> ingest -> store, models

COMMENT TAGS, so you can search for one kind (e.g. grep -rn "\\[LangGraph\\]" npci_rag)
    [LangGraph]  a LangGraph idea or API
    [Python]     Python syntax that may be new
    [Real]       what the production design does instead of the in-memory fake

UPDATES (₹500 -> ₹1,000) ARE APPEND-ONLY
    Every clause is stored once with static metadata (effective_from, rule_key) and is never
    edited or deleted. At query time, among the clauses that state the same rule, the latest one in
    force on the asked date wins (nodes.latest_wins); older ones are history, future ones upcoming.

[Python] This file (__init__.py) is what makes the folder a PACKAGE. Inside the package, files import
each other with a leading dot: `from .models import Chunk` means "models.py in this same package".
"""
