#!/usr/bin/env python3
"""
Batch processing — run multiple queries against one document.

query_batch() runs each query independently, resetting state
between queries to prevent cross-contamination.

Usage:
    python examples/batch.py
"""

from claude_rlm import ClaudeRLM


def main():
    rlm = ClaudeRLM()
    rlm.load_document("report.pdf")

    queries = [
        "What is the total headcount?",
        "List all product names mentioned",
        "What are the key risk factors?",
        "Summarize the CEO's letter",
    ]

    results = rlm.query_batch(queries)

    for query, result in zip(queries, results):
        print(f"\nQ: {query}")
        print(f"A: {result['answer']}")

    # Sum tokens across all queries
    total_root = sum(
        r["root_input_tokens"] + r["root_output_tokens"] for r in results
    )
    total_sub = sum(
        r["sub_input_tokens"] + r["sub_output_tokens"] for r in results
    )
    print(f"\nTotal tokens across all queries: {total_root + total_sub:,}")


if __name__ == "__main__":
    main()
