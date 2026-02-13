#!/usr/bin/env python3
"""
Multi-document analysis using DocumentRegistry.

Load multiple documents, then query across them using
get_combined_context() for cross-document questions.

Usage:
    python examples/multi_document.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from claude_rlm import ClaudeRLM
from claude_rlm.document import DocumentRegistry


def main():
    # Registry manages multiple documents
    registry = DocumentRegistry()

    # Load documents (from text or files)
    registry.load_text("q1_report", """
    Q1 2024 Report
    Revenue: $1.2M
    Net Income: $400K
    Headcount: 50
    """)

    registry.load_text("q2_report", """
    Q2 2024 Report
    Revenue: $1.5M
    Net Income: $600K
    Headcount: 55
    """)

    registry.load_text("q3_report", """
    Q3 2024 Report
    Revenue: $1.8M
    Net Income: $800K
    Headcount: 62
    """)

    # Combine for cross-document analysis
    combined = registry.get_combined_context(["q1_report", "q2_report", "q3_report"])

    rlm = ClaudeRLM()
    rlm.load_text(combined)

    result = rlm.query(
        "Compare revenue growth across all three quarters. "
        "What is the quarter-over-quarter growth rate?"
    )
    print(f"Answer: {result['answer']}")

    # See what's loaded
    print("\nLoaded documents:")
    for meta in registry.list_documents():
        print(f"  {meta.doc_id}: {meta.char_count} chars")


if __name__ == "__main__":
    main()
