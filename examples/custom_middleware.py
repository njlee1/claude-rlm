#!/usr/bin/env python3
"""
Custom middleware example — extend the query pipeline.

Middleware hooks run before and after each query, enabling:
- Synonym expansion
- Cost tracking
- Logging
- Custom pre/post processing

Usage:
    python examples/custom_middleware.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from claude_rlm.orchestrator import MiddlewareChain, CostTrackingMiddleware


class TimingMiddleware:
    """Example middleware that tracks query timing."""

    def __init__(self):
        import time
        self._time = time
        self._start = None

    def pre_query(self, question, context):
        self._start = self._time.time()
        print(f"[TIMING] Starting query: {question[:50]}...")
        return question, context

    def post_query(self, result):
        elapsed = self._time.time() - self._start
        print(f"[TIMING] Query completed in {elapsed:.1f}s")
        result["timing_seconds"] = round(elapsed, 2)
        return result


class ConfidenceFilterMiddleware:
    """Example middleware that warns on low-confidence results."""

    def pre_query(self, question, context):
        return question, context

    def post_query(self, result):
        confidence = result.get("confidence", "unknown")
        if confidence == "low":
            print(f"[WARNING] Low confidence result — consider verifying")
        return result


def main():
    # Build a middleware chain
    chain = MiddlewareChain([
        TimingMiddleware(),
        CostTrackingMiddleware(),
        ConfidenceFilterMiddleware(),
    ])

    # Middleware runs in order for pre_query, reversed for post_query:
    #   pre:  Timing → Cost → Confidence
    #   post: Confidence → Cost → Timing

    # Example: process a question through the chain
    question = "What was the total revenue for Q3 2024?"
    context = "Q3 2024: Revenue $1.8M, Net Income $800K"

    # Pre-query hooks
    question, context = chain.pre_query(question, context)

    # Simulate a result (normally from QueryOrchestrator)
    result = {
        "answer": "$1.8M",
        "confidence": "high",
        "root_input_tokens": 500,
        "root_output_tokens": 200,
    }

    # Post-query hooks
    result = chain.post_query(result)

    print(f"\nFinal result: {result}")


if __name__ == "__main__":
    main()
