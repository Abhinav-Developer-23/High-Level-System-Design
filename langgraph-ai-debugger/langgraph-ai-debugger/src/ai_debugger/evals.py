"""Evaluating the debugger: code checks + Claude Opus 5.5 as LLM-as-a-judge + (optional) RAGAS.

    ai-debugger eval --golden evals/golden.jsonl            # run the graph on each golden case, score it
    ai-debugger eval --threads 7f3a9c4be1d20a55,…            # score real threads from the checkpoint DB
    ai-debugger eval --golden … --ragas                      # add RAGAS metrics (pip extra: `uv sync --extra eval`)
    ai-debugger eval --golden … --baseline var/evals/last.json   # exit 1 if a score dropped (a CI gate)

Three layers of scoring, cheapest first:

1. **Code checks** (`check`): no LLM, free, objective. Right system? Expected tools called (e.g.
   `get_txn` for a txn question)? Required facts in the answer (e.g. "U30")? Under the cost budget?
2. **LLM-as-a-judge** (`judge`): Claude Opus 5.5 grades each answer against a rubric written for
   this job (root cause, evidence, completeness, actionability, safety), 1–5 each, reasoning first.
   The judge is a *stronger* model than the one being judged (the app runs on Sonnet 5).
3. **RAGAS** (`ragas_scores`): standard metrics from the RAGAS library, with Opus 5.5 as its LLM:
   `Faithfulness` (is every claim in the answer supported by the tool outputs? = hallucination
   check) and `FactualCorrectness` (does the answer agree with the reference answer?).

A *sample* is one question with what the debugger produced: the answer, the tool outputs it saw
(the "retrieved contexts" in RAGAS terms), the tools it called, its cost and latency.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from pydantic import BaseModel, Field

from .config import VAR_DIR, get_settings

JUDGE_MODEL = "claude-opus-5-5"
CONTEXT_CHARS = 4000          # per tool output shown to the judge
DEFAULT_BUDGET_USD = 0.50     # per question, for the cost check


# --------------------------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------------------------

class GoldenCase(BaseModel):
    """One line of evals/golden.jsonl: a question with what a good answer must contain."""
    id: str
    question: str
    system: str | None = None                      # expected tpap / tsp
    reference: str | None = None                   # a correct answer, written by an engineer
    must_include: list[str] = []                   # facts the answer must state, e.g. ["U30"]
    expected_tools: list[str] = []                 # tools a good investigation calls, e.g. ["get_txn"]
    budget_usd: float = DEFAULT_BUDGET_USD


class Sample(BaseModel):
    """What the debugger produced for one question: the input to every scorer."""
    case: GoldenCase
    answer: str
    contexts: list[str]                            # tool outputs the agent saw
    tools_called: list[str]
    system: str | None
    cost_usd: float
    latency_ms: int


def load_golden(path: Path) -> list[GoldenCase]:
    return [GoldenCase.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("//")]


def sample_from_state(case: GoldenCase, state: dict[str, Any], latency_ms: int = 0) -> Sample:
    """Turn a thread's saved graph state into a Sample (works for live runs and old threads)."""
    msgs = state.get("agent_messages") or []
    contexts = [m.content if isinstance(m.content, str) else json.dumps(m.content, default=str)
                for m in msgs if isinstance(m, ToolMessage)]
    tools = [tc["name"] for m in msgs if isinstance(m, AIMessage) for tc in m.tool_calls]
    return Sample(case=case, answer=state.get("findings") or state.get("report") or "",
                  contexts=[c[:CONTEXT_CHARS] for c in contexts], tools_called=tools,
                  system=state.get("system"), latency_ms=latency_ms,
                  cost_usd=round(sum(r.get("cost_usd", 0) for r in state.get("runs") or []), 4))


# --------------------------------------------------------------------------------------------
# 1. code checks
# --------------------------------------------------------------------------------------------

def check(s: Sample) -> dict[str, bool]:
    """Free, deterministic checks. Each one is pass/fail."""
    answer = s.answer.lower()
    return {
        "right_system": s.case.system is None or s.system == s.case.system,
        "expected_tools": set(s.case.expected_tools) <= set(s.tools_called),
        "must_include": all(f.lower() in answer for f in s.case.must_include),
        "under_budget": s.cost_usd <= s.case.budget_usd,
        "answered": len(s.answer.strip()) > 50,
        "has_proof": "## proof" in answer,               # the model wrote its own Proof section
    }


# --------------------------------------------------------------------------------------------
# 2. LLM-as-a-judge: Claude Opus 5.5
# --------------------------------------------------------------------------------------------

class Verdict(BaseModel):
    """The judge's grade. `reasoning` comes first so the model thinks before it scores."""
    reasoning: str = Field(description="Step by step: compare the answer with the evidence and the reference.")
    root_cause: int = Field(ge=1, le=5, description="Is the stated cause correct (per the reference / evidence)?")
    evidence: int = Field(ge=1, le=5, description="Is every claim backed by a tool output? 1 = invented facts.")
    completeness: int = Field(ge=1, le=5, description="DB and logs checked, NPCI codes explained, timeline given?")
    actionability: int = Field(ge=1, le=5, description="Clear next step for the on-call / PM?")
    safety: int = Field(ge=1, le=5, description="Read-only, one system only, no guessed ids?")
    unsupported_claims: list[str] = Field(description="Claims in the answer that no tool output supports.")


JUDGE_RUBRIC = """You grade answers from a production-debugging agent for UPI payments (TPAP / TSP).
You get the question, the tool outputs the agent saw (its only evidence), a reference answer written
by an engineer (may be missing), and the agent's answer.

Grade 1-5 on each criterion; 5 = an expert engineer would sign it off, 3 = usable with gaps, 1 = wrong
or harmful. Be strict about evidence: a claim that no tool output supports is a hallucination, even if
it sounds plausible. Do not reward length. Judge only what is in front of you."""


def judge_model() -> Any:
    """Opus 5.5 with Claude's native structured output (`json_schema`).

    Not the default `function_calling` method: that forces a tool call, which Opus 5.5 rejects.
    """
    s = get_settings()
    llm = ChatAnthropic(model=JUDGE_MODEL, max_tokens=4096, timeout=s.llm_timeout_s,
                        api_key=s.anthropic_api_key or None)
    return llm.with_structured_output(Verdict, method="json_schema")


async def judge(s: Sample, model: Any | None = None) -> Verdict:
    evidence = "\n\n".join(f"<tool_output n={i}>\n{c}\n</tool_output>" for i, c in enumerate(s.contexts, 1))
    prompt = (f"<question>\n{s.case.question}\n</question>\n\n<evidence>\n{evidence or '(no tool output)'}\n"
              f"</evidence>\n\n<reference>\n{s.case.reference or '(none: grade on evidence only)'}\n</reference>\n\n"
              f"<answer>\n{s.answer}\n</answer>")
    return await (model or judge_model()).ainvoke([SystemMessage(JUDGE_RUBRIC), HumanMessage(prompt)])


# --------------------------------------------------------------------------------------------
# 3. RAGAS (optional extra)
# --------------------------------------------------------------------------------------------

def ragas_scores(samples: list[Sample]) -> list[dict[str, float]]:
    """Faithfulness + FactualCorrectness from RAGAS, with Opus 5.5 as the evaluator LLM.

    Written for the RAGAS 0.2/0.3 API. Install with `uv sync --extra eval`.
    """
    from ragas import EvaluationDataset, SingleTurnSample, evaluate  # imported here: optional extra
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import FactualCorrectness, Faithfulness

    class _OpusForRagas(ChatAnthropic):
        """RAGAS sets `temperature` on its LLM; Opus 5.5 rejects sampling parameters with a 400.
        Drop them from the request payload."""

        def _get_request_payload(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            payload = super()._get_request_payload(*args, **kwargs)
            for key in ("temperature", "top_p", "top_k"):
                payload.pop(key, None)
            return payload

    s = get_settings()
    llm = LangchainLLMWrapper(_OpusForRagas(model=JUDGE_MODEL, max_tokens=4096, api_key=s.anthropic_api_key or None))
    dataset = EvaluationDataset(samples=[
        SingleTurnSample(user_input=x.case.question, response=x.answer, retrieved_contexts=x.contexts or [""],
                         reference=x.case.reference or "") for x in samples])
    metrics = [Faithfulness(llm=llm)]
    if all(x.case.reference for x in samples):     # FactualCorrectness needs a reference answer
        metrics.append(FactualCorrectness(llm=llm))
    result = evaluate(dataset=dataset, metrics=metrics, llm=llm)
    cols = [m.name for m in metrics]
    return [{c: float(row[c]) for c in cols} for row in result.to_pandas().to_dict("records")]


# --------------------------------------------------------------------------------------------
# running and reporting
# --------------------------------------------------------------------------------------------

async def run_case(graph: Any, case: GoldenCase) -> Sample:
    """Run the real graph on one golden question, in a fresh thread, and capture a Sample."""
    cfg = {"configurable": {"thread_id": f"eval-{case.id}-{uuid.uuid4().hex[:6]}"},
           "recursion_limit": get_settings().recursion_limit}
    opts = {"system": case.system} if case.system else {}
    t0 = time.monotonic()
    await graph.ainvoke({"question": case.question, "options": opts}, cfg)
    state = (await graph.aget_state(cfg)).values
    return sample_from_state(case, state, latency_ms=int((time.monotonic() - t0) * 1000))


def summarize(rows: list[dict[str, Any]]) -> dict[str, float]:
    """Averages over all cases: check pass rates, judge scores (1-5), RAGAS scores (0-1)."""
    keys = {k for r in rows for k, v in r["scores"].items() if isinstance(v, int | float | bool)}
    return {k: round(sum(float(r["scores"].get(k, 0)) for r in rows) / len(rows), 3) for k in sorted(keys)}


LOWER_IS_BETTER = {"cost_usd", "latency_ms"}


def regressions(now: dict[str, float], baseline: dict[str, float], tolerance: float = 0.05) -> list[str]:
    """Averages that got worse by more than `tolerance` (relative) since the baseline run.

    Worse = lower for scores and pass rates, higher for cost and latency.
    """
    worse = []
    for k, v in now.items():
        b = baseline.get(k)
        if not b:
            continue
        if (v > b * (1 + tolerance)) if k in LOWER_IS_BETTER else (v < b * (1 - tolerance)):
            worse.append(f"{k}: {b} → {v}")
    return worse


def write_report(rows: list[dict[str, Any]], summary: dict[str, float]) -> Path:
    """var/evals/<time>.json (machine-readable, usable as the next --baseline) + a .md table."""
    out = VAR_DIR / "evals"
    out.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = out / f"{stamp}.json"
    path.write_text(json.dumps({"summary": summary, "cases": rows}, indent=1, default=str), encoding="utf-8")
    cols = sorted(summary)
    lines = ["| case | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    lines += [f"| {r['id']} | " + " | ".join(str(r["scores"].get(c, "")) for c in cols) + " |" for r in rows]
    lines.append("| **average** | " + " | ".join(str(summary[c]) for c in cols) + " |")
    (out / f"{stamp}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


async def evaluate_samples(samples: list[Sample]) -> list[dict[str, Any]]:
    """Score every sample with the code checks and the Opus judge. Returns one row per case."""
    model = judge_model()
    rows = []
    for s in samples:
        verdict = await judge(s, model)
        scores: dict[str, Any] = {f"check_{k}": v for k, v in check(s).items()}
        scores.update({f"judge_{k}": getattr(verdict, k)
                       for k in ("root_cause", "evidence", "completeness", "actionability", "safety")})
        scores.update(cost_usd=s.cost_usd, latency_ms=s.latency_ms)
        rows.append({"id": s.case.id, "scores": scores, "reasoning": verdict.reasoning,
                     "unsupported_claims": verdict.unsupported_claims, "tools_called": s.tools_called})
    return rows


def add_ragas(rows: list[dict[str, Any]], samples: list[Sample]) -> None:
    """Add the RAGAS scores to the rows. Call it outside asyncio: RAGAS's `evaluate()` is synchronous
    and runs its own event loop."""
    for row, extra in zip(rows, ragas_scores(samples), strict=True):
        row["scores"].update({f"ragas_{k}": round(v, 3) for k, v in extra.items()})
