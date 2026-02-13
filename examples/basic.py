#!/usr/bin/env python3
"""
Basic RLM query — load a document and ask a question.

Usage:
    python examples/basic.py
"""

from claude_rlm import ClaudeRLM


def main():
    # Default config: sonnet root + haiku sub (cost-optimized)
    rlm = ClaudeRLM()

    # Load from text directly
    rlm.load_text("""
    Company XYZ Financial Summary
    =============================

    Q1 2024: Revenue $1.2M, Expenses $800K, Net Income $400K
    Q2 2024: Revenue $1.5M, Expenses $900K, Net Income $600K
    Q3 2024: Revenue $1.8M, Expenses $1.0M, Net Income $800K
    Q4 2024: Revenue $2.1M, Expenses $1.2M, Net Income $900K

    Total Annual Revenue: $6.6M
    Total Annual Net Income: $2.7M
    """)

    result = rlm.query("Which quarter had the highest profit margin?")

    print(f"Answer: {result['answer']}")
    print(f"Evidence: {result['evidence']}")
    print(f"Confidence: {result['confidence']}")

    # Or load from file:
    # rlm.load_document("report.pdf")
    # result = rlm.query("What was the total revenue?")


if __name__ == "__main__":
    main()
