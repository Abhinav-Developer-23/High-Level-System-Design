"""
Running the graph: the demo and the learning commands. `python -m npci_rag` runs this file.

    python -m npci_rag                                  the demo: ingest + 9 questions on 3 threads
    python -m npci_rag --graph                          print the wiring as Mermaid text
    python -m npci_rag --ask "QUESTION"                 one question (thread "cli")
    python -m npci_rag --ask "QUESTION" --stream        ... and print what every node returned
    python -m npci_rag --ask "QUESTION" --state         ... and the state saved after the run
    python -m npci_rag --ask "QUESTION" --history       ... and every checkpoint of the thread
    python -m npci_rag --chat                           type questions; follow-ups share one thread

Each LangGraph call used here is explained where it is used: invoke (demo, ask), stream (ask),
get_state (show_state), get_state_history (show_history), get_graph (main).
"""
from __future__ import annotations

import argparse

from .data import CIRCULARS
from .graph import build_graph
from .ingest import ingest_job
from .models import Chunk, Source


def thread(thread_id: str) -> dict:
    """[LangGraph] The config that selects a conversation. Every call with the same thread_id continues the
    same saved state. A graph with a checkpointer REQUIRES a thread_id: invoke without one raises an error."""
    return {"configurable": {"thread_id": thread_id}}


def short(value) -> str:
    """A one-line preview of a state value, for the --stream / --state printouts."""
    if isinstance(value, list):
        if value and isinstance(value[0], Source):
            return f"{len(value)} sources: " + ", ".join(f"[{v.n}] {v.circular_id} {v.role}" for v in value)
        if value and isinstance(value[0], Chunk):
            return f"{len(value)} chunks: " + ", ".join(f"{v.circular_id} {v.clause_path}" for v in value[:4]) \
                + (", ..." if len(value) > 4 else "")
    text = str(value).replace("\n", " | ")
    return text if len(text) <= 110 else text[:107] + "..."


def ask(app, question: str, thread_id: str, stream: bool) -> None:
    """Run one question. With stream=True, print what each node returned, as it happens."""
    print(f"\nQ ({thread_id}): {question}")
    if stream:
        # [LangGraph] stream_mode="updates" yields one dict per finished node: {node_name: what_it_returned}.
        # Other modes: "values" (the whole state after every step), "messages" (LLM tokens, for chat UIs),
        # "debug" (everything). The run is exactly the same; only what you get to see differs.
        for update in app.stream({"question": question}, thread(thread_id), stream_mode="updates"):
            for node, changes in update.items():
                print(f"\n  -> {node} returned:")
                for key, value in (changes or {}).items():
                    print(f"       {key:<11} = {short(value)}")
        # When the stream ends, the final state is in the checkpoint; read it back.
        final = app.get_state(thread(thread_id)).values["final"]
    else:
        # [LangGraph] invoke = run to END and return the final state as a plain dict.
        final = app.invoke({"question": question}, thread(thread_id))["final"]
    print(f"{'-' * 100}\n{final}")


def show_state(app, thread_id: str) -> None:
    """[LangGraph] get_state(config) -> a StateSnapshot of the thread's LATEST checkpoint:
         .values    the state dict
         .next      the node(s) that would run next: () when the run reached END
         .config    includes the checkpoint_id; pass it back to replay from this point
         .metadata  the step number and where the checkpoint came from"""
    snap = app.get_state(thread(thread_id))
    print(f"\nget_state: step={snap.metadata['step']}  next={snap.next}  "
          f"checkpoint_id={snap.config['configurable']['checkpoint_id']}")
    for key, value in snap.values.items():
        print(f"  {key:<11} = {short(value)}")


def show_history(app, thread_id: str) -> None:
    """[LangGraph] get_state_history(config) -> every checkpoint of the thread, NEWEST first, one per step.
    source="input" is the checkpoint where your input was written; source="loop" ones come after nodes ran.
    .next is the node that runs AFTER that checkpoint, so reading the list bottom-up replays the run.
    Passing an old snapshot's .config to invoke re-runs from that point ("time travel")."""
    print(f"\nget_state_history (newest first) for thread {thread_id!r}:")
    for snap in app.get_state_history(thread(thread_id)):
        print(f"  step {snap.metadata['step']:>3}  source={snap.metadata['source']:<6} next={snap.next}")


def chat(app, thread_id: str) -> None:
    """Type questions. They all share one thread, so follow-ups ("And before that?") work."""
    print("Ask about the sample circulars. Empty line or 'quit' to stop. Try:")
    print("  What is the UPI Lite per transaction limit?  ->  And before that?  ->  What was it on 10 Dec 2024?")
    while True:
        try:
            q = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() in ("quit", "exit"):
            break
        ask(app, q, thread_id, stream=False)


def demo(app) -> None:
    """The fixed demo: 9 questions on 3 threads. pm-1 shows follow-ups and as-of dates, pm-2 other
    products, pm-3 the clarify / refuse paths."""
    questions = [
        ("pm-1", "What is the UPI Lite per transaction limit?"),
        ("pm-1", "And before that?"),                                   # follow-up: product comes from the thread
        ("pm-1", "What was the UPI Lite limit on 10 Dec 2024?"),        # as_of: ₹500 current, ₹1,000 upcoming
        ("pm-2", "What is the Tap & Pay limit on PoS without an extra factor of authentication?"),
        ("pm-2", "How many days does the responding party get to respond in an MCC dispute?"),
        ("pm-2", "How did the ISD sections in URCS change?"),
        ("pm-2", "When can a bank update ISD details in URCS?"),
        ("pm-3", "What's the per transaction limit?"),                  # no product -> "which product?"
        ("pm-3", "Who won the cricket match?"),                         # off-topic -> refuse
    ]
    for thread_id, q in questions:
        out = app.invoke({"question": q}, config=thread(thread_id))
        print(f"\n{'=' * 100}\nQ ({thread_id}): {q}\n{'-' * 100}\n{out['final']}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m npci_rag",
                                     description="NPCI circular Q&A: a LangGraph learning demo (offline).")
    parser.add_argument("--ask", metavar="QUESTION", help="ask one question instead of running the demo")
    parser.add_argument("--thread", default="cli", help="thread id for --ask / --chat (default: cli)")
    parser.add_argument("--stream", action="store_true", help="with --ask: print what every node returned")
    parser.add_argument("--state", action="store_true", help="with --ask: print the saved state afterwards")
    parser.add_argument("--history", action="store_true", help="with --ask: list the thread's checkpoints")
    parser.add_argument("--graph", action="store_true", help="print the graph as Mermaid text and exit")
    parser.add_argument("--chat", action="store_true", help="type questions in a loop on one thread")
    args = parser.parse_args()

    app = build_graph()
    if args.graph:
        # [LangGraph] get_graph() describes the compiled graph (nodes + edges, conditional ones dotted).
        # draw_mermaid() returns it as Mermaid text: paste it into https://mermaid.live to see the picture.
        print(app.get_graph().draw_mermaid())
        return

    if args.ask or args.chat:
        ingest_job(CIRCULARS, verbose=False)
        if args.chat:
            chat(app, args.thread)
            return
        ask(app, args.ask, args.thread, args.stream)
        if args.state:
            show_state(app, args.thread)
        if args.history:
            show_history(app, args.thread)
        return

    # The default: the full demo.
    print("Ingest run 1 (every 10 minutes in the real system):")
    ingest_job(CIRCULARS)
    print("Ingest run 2 (same files again):")
    ingest_job(CIRCULARS[:1])
    demo(app)


# [Python] True only when this file is run (python -m npci_rag), not when it is imported.
if __name__ == "__main__":
    main()
