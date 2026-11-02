"""
START HERE. LangGraph in plain words, then build_graph(): where the nodes and routers are wired together.
=========================================================================================================

LangGraph runs a program drawn as a GRAPH: boxes (nodes) joined by arrows (edges). Ours
(svg/n03-query-graph.svg draws it; `python -m npci_rag --graph` prints it):

  START -> understand -+-> retrieve -> rerank -> latest_wins -> generate -> check_grounding -+-> cite_sources -> END
                       |      ^                                                             |
                       |      +------------------ retry once (search wider) ----------------+
                       |                                                                    +-> not_found    -> END
                       +-> clarify_or_refuse -> END      ("which product?" / off-topic)

Six ideas cover everything in this package.

1. STATE (state.py). One dict shared by the whole run. Its keys are declared once, as a TypedDict.
   Think of it as a whiteboard: every node reads it, and writes its results onto it for the nodes after.

2. NODE (nodes.py). A plain Python function:    def my_node(state) -> dict
   It gets the current state, does ONE job, and returns ONLY the keys it changes, for example
   {"answer": "...", "found": True}. LangGraph merges that dict into the state. A node never edits the
   state in place and never calls the next node itself; the edges decide what runs next.
   Merge rule: by default a returned key REPLACES the old value. A key can have a "reducer" that
   appends instead (state.py shows one); this graph needs none.

3. EDGE. "After node A, always run node B":    g.add_edge("A", "B")
   START and END are the special names for "a run begins here" and "the run stops here".

4. CONDITIONAL EDGE (routers.py). "After node A, ask a function which node runs next":
       g.add_conditional_edges("A", router, ["B", "C"])
   The router gets the state and returns a node NAME. A loop is just a conditional edge pointing back
   to an earlier node (check_grounding -> retrieve).

5. COMPILE, then RUN. g.compile() checks the wiring (every edge points at a node that exists, START
   leads somewhere) and returns an "app". Then (see __main__.py):
       app.invoke(input, config)   runs from START to END and returns the final state (a dict)
       app.stream(input, config)   the same run, but yields after every node, so you can watch it
   `input` is a partial state, e.g. {"question": "..."}; it is merged in before the first node.

6. CHECKPOINTER + THREAD (this is what makes follow-up questions work).
   compile(checkpointer=InMemorySaver()) makes LangGraph SAVE the state after every step, filed under a
   thread id you pass in the config:
       config = {"configurable": {"thread_id": "pm-1"}}
   The next invoke with the SAME thread id starts from the saved state, with the new input merged on top.
   So "And before that?" still sees products=["UPI_LITE"] from the previous question. A new thread id
   starts empty. app.get_state(config) reads the latest saved state; app.get_state_history(config) lists
   every saved step (debugging, "time travel").

How a run executes: in "super-steps". Each step runs the node(s) that are due, applies the dicts they
returned to the state, saves a checkpoint, then follows the edges to find the next node(s). Repeat
until END. Here exactly one node is due per step, so a run is a simple sequence; when one node has
edges to several nodes, those run in parallel, in one step.

Not used here (learn these next): reducers / add_messages, ToolNode and tool calling, interrupt() for
human-in-the-loop, Send() for fan-out, subgraphs, async nodes. ../langgraph-ai-debugger/LangGraph.md
covers them.
"""
from __future__ import annotations

# [LangGraph] The LangGraph imports:
#   StateGraph          the builder: add nodes and edges to it, then .compile() it into a runnable app
#   START, END          the two special node names: where every run begins, and where it stops
#   InMemorySaver       a "checkpointer": saves the state after every step (in a Python dict here)
#   JsonPlusSerializer  how the checkpointer turns the state into bytes and back
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph

from .models import Chunk, Source
from .nodes import (check_grounding, cite_sources, clarify_or_refuse, generate, latest_wins, not_found,
                    rerank, retrieve, understand)
from .routers import route_grounding, route_intent
from .state import QAState


def build_graph():
    """Turn the nodes and routers into a runnable app."""
    # [LangGraph] The builder. QAState tells it which keys (channels) the state has.
    g = StateGraph(QAState)

    # [LangGraph] add_node(name, function). Each function's own name is the node's name.
    for fn in (understand, retrieve, rerank, latest_wins, generate, check_grounding,
               cite_sources, clarify_or_refuse, not_found):
        g.add_node(fn.__name__, fn)

    # [LangGraph] A fixed edge: "after A, always B". Every run starts at START.
    g.add_edge(START, "understand")

    # [LangGraph] A conditional edge: after "understand", call route_intent(state); it returns the next
    # node's name. The list names every node the router may return: LangGraph uses it to draw the graph
    # and check the names. Without it, the diagram can't show where the router may go.
    g.add_conditional_edges("understand", route_intent, ["retrieve", "clarify_or_refuse"])

    # The main pipeline, one fixed edge after another.
    g.add_edge("retrieve", "rerank")
    g.add_edge("rerank", "latest_wins")
    g.add_edge("latest_wins", "generate")
    g.add_edge("generate", "check_grounding")

    # [LangGraph] The second decision point. "retrieve" in this list makes the retry loop.
    g.add_conditional_edges("check_grounding", route_grounding, ["cite_sources", "retrieve", "not_found"])

    # [LangGraph] Three ways to finish. A node that leads to END is the last one of the run; whatever it
    # wrote (here: "final") is in the state that app.invoke returns.
    for terminal in ("cite_sources", "clarify_or_refuse", "not_found"):
        g.add_edge(terminal, END)

    # [LangGraph] The checkpointer saves the state after every step, per thread_id (idea 6 above).
    # [Real] PostgresSaver, so a thread survives restarts and every server sees the same threads.
    #        InMemorySaver keeps them in a Python dict: enough to show follow-ups, gone when the program ends.
    # Saving turns the state into bytes (msgpack) and back. Plain types (str, int, date, list, dict) come
    # back by themselves. Our own pydantic classes (Chunk, Source) are rebuilt only if allow-listed here:
    # a safety rule, so a tampered checkpoint can't make LangGraph create arbitrary classes. Without the
    # list, LangGraph logs a warning for each class it reads back.
    # [Python] cls.__module__ is the module the class was defined in: "npci_rag.models".
    serde = JsonPlusSerializer(allowed_msgpack_modules=[(cls.__module__, cls.__name__) for cls in (Chunk, Source)])

    # [LangGraph] compile() checks the wiring and returns the app (a CompiledStateGraph). From here on you
    # use the app: invoke / stream / get_state / get_state_history / get_graph.
    return g.compile(checkpointer=InMemorySaver(serde=serde))
