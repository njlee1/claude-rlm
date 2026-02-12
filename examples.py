#!/usr/bin/env python3
"""
Claude RLM - Usage Examples
===========================

Demonstrates how to use the RLM system for various document analysis tasks.
These examples use Mode B (Programmatic API). For Mode A (Claude Code Agent),
copy CLAUDE.md and .claude/ to your project root and use Claude Code directly.
"""

import anthropic
from claude_rlm import ClaudeRLM, RLMConfig, RLMPatterns


# =============================================================================
# BASIC USAGE
# =============================================================================

def example_basic():
    """Basic document query."""

    rlm = ClaudeRLM()
    rlm.load_document("financial_report.pdf")

    result = rlm.query("What was the total revenue for Q3 2024?")

    print(f"Answer: {result['answer']}")
    print(f"Evidence: {result['evidence']}")
    print(f"Confidence: {result['confidence']}")


# =============================================================================
# CUSTOM CONFIGURATION
# =============================================================================

def example_custom_config():
    """Using custom configuration for better accuracy or lower cost."""

    # High accuracy config
    high_accuracy_config = RLMConfig(
        root_model="claude-opus-4-6",
        sub_model="claude-sonnet-4-5-20250929",
        max_sub_calls=100,
        verbose=True,
    )

    # Cost-optimized config (default models)
    cost_optimized_config = RLMConfig(
        root_model="claude-sonnet-4-5-20250929",
        sub_model="claude-haiku-4-5-20251001",
        max_sub_calls=20,
    )

    rlm = ClaudeRLM(high_accuracy_config)
    rlm.load_document("complex_legal_document.pdf")

    result = rlm.query("What are all the liability clauses?")

    # Check costs with per-model breakdown
    costs = rlm.get_cost_estimate()
    print(f"Root model cost: ${costs['root_cost_usd']}")
    print(f"Sub model cost: ${costs['sub_cost_usd']}")
    print(f"Total cost: ${costs['total_cost_usd']}")


# =============================================================================
# USING PATTERNS
# =============================================================================

def example_patterns():
    """Using pre-built query patterns."""

    rlm = ClaudeRLM()
    rlm.load_document("annual_report.pdf")

    # Find specific value
    result = RLMPatterns.find_specific_value(
        rlm,
        value_description="Q4 2024 net income",
        expected_format="currency (e.g., $1.5 million)",
    )
    print(f"Net Income: {result['answer']}")

    # Compare entities
    rlm.reset_state()
    result = RLMPatterns.compare_entities(
        rlm,
        entity1="Product Line A",
        entity2="Product Line B",
        comparison_criteria=["Revenue growth", "Profit margin", "Market share"],
    )
    print(f"Comparison: {result['answer']}")

    # Extract all instances
    rlm.reset_state()
    result = RLMPatterns.extract_all_instances(
        rlm,
        pattern_description="all executive names and their titles",
        output_format="table with columns: Name, Title, Department",
    )
    print(f"Executives: {result['answer']}")


# =============================================================================
# LOADING TEXT DIRECTLY
# =============================================================================

def example_text_input():
    """Loading text directly instead of from file."""

    rlm = ClaudeRLM()

    document_text = """
    Company XYZ Financial Summary
    =============================

    Q1 2024: Revenue $1.2M, Expenses $800K, Net Income $400K
    Q2 2024: Revenue $1.5M, Expenses $900K, Net Income $600K
    Q3 2024: Revenue $1.8M, Expenses $1.0M, Net Income $800K
    Q4 2024: Revenue $2.1M, Expenses $1.2M, Net Income $900K

    Total Annual Revenue: $6.6M
    Total Annual Net Income: $2.7M
    """

    rlm.load_text(document_text)

    result = rlm.query("Which quarter had the highest profit margin?")
    print(f"Answer: {result['answer']}")


# =============================================================================
# MULTI-DOCUMENT ANALYSIS
# =============================================================================

def example_multi_document():
    """Analyzing multiple documents together."""

    rlm = ClaudeRLM()

    docs = []
    for filename in ["report_2022.txt", "report_2023.txt", "report_2024.txt"]:
        with open(filename) as f:
            docs.append(f"=== {filename} ===\n{f.read()}")

    combined = "\n\n".join(docs)
    rlm.load_text(combined)

    result = rlm.query(
        "Compare the revenue trends across all three years. "
        "What is the year-over-year growth rate?"
    )
    print(f"Trend Analysis: {result['answer']}")


# =============================================================================
# WITH DOCLING PREPROCESSING
# =============================================================================

def example_with_docling():
    """Using IBM Docling for better PDF extraction before RLM processing."""

    try:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        docling_result = converter.convert("complex_document.pdf")
        clean_text = docling_result.document.export_to_markdown()

        rlm = ClaudeRLM()
        rlm.load_text(clean_text)

        result = rlm.query("Summarize all tables in this document")
        print(f"Table Summary: {result['answer']}")

    except ImportError:
        print("Docling not installed. Run: pip install docling")


# =============================================================================
# COST TRACKING
# =============================================================================

def example_cost_tracking():
    """Detailed cost tracking with per-model breakdown."""

    config = RLMConfig(verbose=True, save_trajectory=True)

    rlm = ClaudeRLM(config)
    rlm.load_document("document.pdf")

    result = rlm.query("Complex multi-part question here")

    costs = rlm.get_cost_estimate()
    print(f"\nCost Breakdown:")
    print(f"  Root model ({costs['root_model']}):")
    print(f"    Input tokens:  {costs['root_input_tokens']:,}")
    print(f"    Output tokens: {costs['root_output_tokens']:,}")
    print(f"    Cost:          ${costs['root_cost_usd']}")
    print(f"  Sub model ({costs['sub_model']}):")
    print(f"    Input tokens:  {costs['sub_input_tokens']:,}")
    print(f"    Output tokens: {costs['sub_output_tokens']:,}")
    print(f"    Cost:          ${costs['sub_cost_usd']}")
    print(f"  Total:           ${costs['total_cost_usd']}")
    print(f"  Sub-calls used:  {result['sub_calls_used']}")


# =============================================================================
# BATCH PROCESSING
# =============================================================================

def example_batch():
    """Process multiple queries efficiently with query_batch().

    query_batch() caches document metadata and runs each query
    independently, avoiding redundant document probing.
    """

    rlm = ClaudeRLM()
    rlm.load_document("comprehensive_report.pdf")

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

    # Note: query_batch resets state per query, so get_cost_estimate()
    # only reflects the LAST query. For total costs, sum from results:
    total_root = sum(r["root_input_tokens"] + r["root_output_tokens"] for r in results)
    total_sub = sum(r["sub_input_tokens"] + r["sub_output_tokens"] for r in results)
    print(f"\nTotal tokens across all queries: {total_root + total_sub:,}")


# =============================================================================
# ERROR HANDLING
# =============================================================================

def example_error_handling():
    """Handling errors gracefully."""

    config = RLMConfig(
        max_retries=5,
        retry_base_delay=2.0,
        verbose=True,
    )

    rlm = ClaudeRLM(config)

    try:
        rlm.load_document("document.pdf")
        result = rlm.query("What is the main conclusion?")
        print(f"Answer: {result['answer']}")
    except FileNotFoundError as e:
        print(f"Document not found: {e}")
    except anthropic.RateLimitError:
        print("Rate limited after all retries. Try again later.")
    except anthropic.APIError as e:
        print(f"API error: {e}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("Claude RLM Examples")
    print("=" * 60)
    print()
    print("Available examples:")
    print("  example_basic()          - Basic document query")
    print("  example_custom_config()  - Custom model configuration")
    print("  example_patterns()       - Pre-built query patterns")
    print("  example_text_input()     - Load text directly")
    print("  example_multi_document() - Analyze multiple documents")
    print("  example_with_docling()   - Docling preprocessing")
    print("  example_cost_tracking()  - Detailed cost breakdown")
    print("  example_batch()          - Batch processing")
    print("  example_error_handling() - Error handling patterns")
    print()
    print("Uncomment the example you want to run in this file.")
