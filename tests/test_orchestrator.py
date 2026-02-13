"""
Tests for the query orchestrator, middleware, and result parser.

Uses mock LLM clients — no real API calls.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claude_rlm.orchestrator import (
    QueryOrchestrator,
    MiddlewareChain,
    VerboseLoggingMiddleware,
    CostTrackingMiddleware,
)
from claude_rlm.orchestrator.result_parser import parse_final_answer, build_result
from claude_rlm.api.cost_tracker import compute_cost


# =============================================================================
# Mock LLM Client
# =============================================================================


class MockLLMClient:
    """Mock LLM client that returns canned responses.

    Each call pops from the response list. If empty, returns a
    FINAL_ANSWER to prevent infinite loops.
    """

    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.calls = []

    def call(self, model, max_tokens, system, messages):
        self.calls.append({
            "model": model,
            "max_tokens": max_tokens,
            "system_len": len(system),
            "messages_len": len(messages),
        })
        if self.responses:
            text = self.responses.pop(0)
        else:
            text = "FINAL_ANSWER: default fallback answer"
        return (text, 100, 50)


# =============================================================================
# Result Parser
# =============================================================================


def test_parse_final_answer_full():
    """Parse response with all structured fields."""
    response = (
        "FINAL_ANSWER: Revenue is $1.8M\n"
        "SOURCE_EVIDENCE: Found on line 42: 'Revenue: $1,800,000'\n"
        "CONFIDENCE: high\n"
        "VERIFICATION_METHOD: regex + sub_query cross-check"
    )
    result = parse_final_answer(response, sub_call_count=3)
    assert result["answer"] == "Revenue is $1.8M"
    assert "line 42" in result["evidence"]
    assert result["confidence"] == "high"
    assert "regex" in result["verification"]
    assert result["sub_calls_used"] == 3


def test_parse_final_answer_minimal():
    """Parse response with only the answer."""
    response = "FINAL_ANSWER: 42"
    result = parse_final_answer(response)
    assert result["answer"] == "42"
    assert result["confidence"] == "unknown"


def test_parse_final_answer_no_marker():
    """Response without FINAL_ANSWER: falls back to full text."""
    response = "The revenue is approximately $1.8M based on line 42."
    result = parse_final_answer(response)
    assert result["answer"] == response


def test_build_result_shape():
    """build_result produces the v1 dict shape."""
    result = build_result(
        "$1.8M",
        source="FINAL() from code",
        sub_call_count=5,
        root_input_tokens=1000,
        root_output_tokens=500,
    )
    assert result["answer"] == "$1.8M"
    assert result["verification"] == "FINAL() from code"
    assert result["sub_calls_used"] == 5
    assert result["root_input_tokens"] == 1000
    assert result["evidence"] is None


# =============================================================================
# Middleware
# =============================================================================


def test_middleware_chain_order():
    """Pre hooks run forward, post hooks run backward."""
    order = []

    class MW1:
        def pre_query(self, q, c):
            order.append("pre1")
            return q, c
        def post_query(self, r):
            order.append("post1")
            return r

    class MW2:
        def pre_query(self, q, c):
            order.append("pre2")
            return q, c
        def post_query(self, r):
            order.append("post2")
            return r

    chain = MiddlewareChain([MW1(), MW2()])
    chain.run_pre("q", "c")
    chain.run_post({})

    assert order == ["pre1", "pre2", "post2", "post1"]


def test_cost_tracking_middleware():
    """CostTrackingMiddleware accumulates token counts."""
    mw = CostTrackingMiddleware()
    mw.pre_query("q1", "c")
    mw.post_query({"root_input_tokens": 100, "root_output_tokens": 50})
    mw.pre_query("q2", "c")
    mw.post_query({"root_input_tokens": 200, "root_output_tokens": 100})

    totals = mw.get_totals()
    assert totals["query_count"] == 2
    assert totals["total_root_input"] == 300
    assert totals["total_root_output"] == 150


def test_middleware_chain_empty():
    """Empty chain passes through unchanged."""
    chain = MiddlewareChain()
    q, c = chain.run_pre("question", "context")
    assert q == "question"
    assert c == "context"


# =============================================================================
# Query Orchestrator
# =============================================================================


def test_orchestrator_immediate_answer():
    """LLM returns FINAL_ANSWER immediately."""
    client = MockLLMClient([
        "FINAL_ANSWER: The revenue is $1.8M\nCONFIDENCE: high"
    ])

    orchestrator = QueryOrchestrator(
        llm_client=client,
        sub_query_fn=lambda p, c=None: "mock",
        system_prompt="You are a test.",
    )
    result = orchestrator.run("What is revenue?", "Q3 Revenue $1.8M")

    assert result["answer"] == "The revenue is $1.8M"
    assert result["confidence"] == "high"
    assert len(client.calls) == 1


def test_orchestrator_code_then_final():
    """LLM writes code, then provides FINAL_ANSWER."""
    client = MockLLMClient([
        '```repl\nprint("hello")\n```',
        "FINAL_ANSWER: Found it\nCONFIDENCE: medium",
    ])

    orchestrator = QueryOrchestrator(
        llm_client=client,
        sub_query_fn=lambda p, c=None: "mock",
        system_prompt="You are a test.",
    )
    result = orchestrator.run("test", "test context")

    assert result["answer"] == "Found it"
    assert len(client.calls) == 2


def test_orchestrator_final_from_code():
    """LLM writes code that calls FINAL()."""
    client = MockLLMClient([
        '```repl\nFINAL("$1.8M revenue")\n```',
    ])

    orchestrator = QueryOrchestrator(
        llm_client=client,
        sub_query_fn=lambda p, c=None: "mock",
        system_prompt="You are a test.",
    )
    result = orchestrator.run("test", "test context")

    assert result["answer"] == "$1.8M revenue"
    assert result["verification"] == "FINAL() from code"


def test_orchestrator_iteration_limit():
    """Orchestrator forces answer at iteration limit."""
    # Return code blocks that never terminate — the orchestrator
    # should force a FINAL_ANSWER after max_iterations
    client = MockLLMClient([
        '```repl\nprint("still thinking")\n```',
        '```repl\nprint("still thinking")\n```',
        '```repl\nprint("still thinking")\n```',
        "FINAL_ANSWER: forced answer",
    ])

    orchestrator = QueryOrchestrator(
        llm_client=client,
        sub_query_fn=lambda p, c=None: "mock",
        system_prompt="You are a test.",
    )
    result = orchestrator.run("test", "test context", max_iterations=3)

    assert result["answer"] is not None


def test_orchestrator_batch():
    """run_batch processes multiple questions."""
    client = MockLLMClient([
        "FINAL_ANSWER: answer1",
        "FINAL_ANSWER: answer2",
    ])

    orchestrator = QueryOrchestrator(
        llm_client=client,
        sub_query_fn=lambda p, c=None: "mock",
        system_prompt="You are a test.",
    )
    results = orchestrator.run_batch(
        ["q1", "q2"], "test context"
    )

    assert len(results) == 2
    assert results[0]["answer"] == "answer1"
    assert results[1]["answer"] == "answer2"


def test_orchestrator_with_middleware():
    """Middleware hooks are called during orchestration."""
    cost_mw = CostTrackingMiddleware()
    chain = MiddlewareChain([cost_mw])

    client = MockLLMClient([
        "FINAL_ANSWER: test answer",
    ])

    orchestrator = QueryOrchestrator(
        llm_client=client,
        sub_query_fn=lambda p, c=None: "mock",
        system_prompt="You are a test.",
        middleware=chain,
    )
    orchestrator.run("test", "test context")

    assert cost_mw.query_count == 1
    assert cost_mw.total_root_input == 100  # from MockLLMClient


# =============================================================================
# Cost Tracker
# =============================================================================


def test_compute_cost():
    """Cost computation matches expected values."""
    cost = compute_cost(
        root_model="claude-sonnet-4-5-20250929",
        root_input_tokens=1_000_000,
        root_output_tokens=100_000,
        sub_model="claude-haiku-4-5-20251001",
        sub_input_tokens=500_000,
        sub_output_tokens=50_000,
    )
    # Sonnet: 1M * 3.0/M + 100K * 15.0/M = 3.0 + 1.5 = 4.5
    assert cost["root_cost_usd"] == 4.5
    # Haiku: 500K * 0.25/M + 50K * 1.25/M = 0.125 + 0.0625 = 0.1875
    assert cost["sub_cost_usd"] == 0.1875
    assert cost["total_cost_usd"] == 4.6875
