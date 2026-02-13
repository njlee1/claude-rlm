#!/usr/bin/env python3
"""
Unified CLI for Claude RLM.

Subcommands:
    query   — Run a document query using the RLM REPL loop
    detect  — Auto-detect the domain of a document
    domains — List all registered domains with stats

Usage:
    claude-rlm query report.pdf "What was Q3 revenue?"
    claude-rlm detect contract.pdf
    claude-rlm domains
"""

import argparse
import sys
from pathlib import Path


def cmd_query(args):
    """Run a document query via the RLM engine."""
    # Lazy import to avoid loading heavy deps until needed
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from claude_rlm import ClaudeRLM, RLMConfig

    config = RLMConfig(
        root_model=args.root_model,
        sub_model=args.sub_model,
        verbose=args.verbose,
    )

    rlm = ClaudeRLM(config)
    rlm.load_document(args.document)

    result = rlm.query(args.query, max_iterations=args.max_iterations)

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"\nAnswer: {result['answer']}")
    print(f"\nEvidence: {result['evidence']}")
    print(f"\nConfidence: {result['confidence']}")
    print(f"\nSub-calls used: {result['sub_calls_used']}")

    costs = rlm.get_cost_estimate()
    print(f"\nCost breakdown:")
    print(f"  Root ({costs['root_model']}): ${costs['root_cost_usd']}")
    print(f"  Sub  ({costs['sub_model']}): ${costs['sub_cost_usd']}")
    print(f"  Total: ${costs['total_cost_usd']}")


def cmd_detect(args):
    """Auto-detect the domain of a document."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from domains import DOMAIN_REGISTRY

    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {args.file}")
        sys.exit(1)

    try:
        text = path.read_text(errors="replace")[:3000]
    except Exception:
        text = ""

    print(f"File: {path.name} ({path.stat().st_size:,} bytes)")
    print()
    print("Domain Detection Scores:")
    print("-" * 40)

    scores = {}
    for name, cls in DOMAIN_REGISTRY.items():
        domain = cls()
        score = domain.detect(text, path.name)
        scores[name] = score
        bar = "#" * int(score * 30)
        print(f"  {name:14s}  {score:.2f}  {bar}")

    best_name = max(scores, key=lambda k: scores[k])
    best_score = scores[best_name]

    print()
    if best_score >= 0.3:
        domain = DOMAIN_REGISTRY[best_name]()
        print(f"Detected domain: {domain.name} ({domain.description})")
        print()
        print(f"Synonym groups available ({len(domain.synonyms)}):")
        for concept, terms in domain.synonyms.items():
            preview = ", ".join(terms[:5])
            if len(terms) > 5:
                preview += "..."
            print(f"  {concept}: {preview}")
        print()
        print(f"Query templates available ({len(domain.query_templates)}):")
        for topic in domain.query_templates:
            print(f"  - {topic}")
    else:
        print("No domain detected with sufficient confidence.")
        print("The document will be analyzed with generic keyword search.")


def cmd_domains(args):
    """List all registered domains with stats."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from domains import list_domains, DOMAIN_REGISTRY

    print("Claude RLM — Registered Domains")
    print("=" * 60)
    print()

    info = list_domains()
    for name, stats in info.items():
        domain = DOMAIN_REGISTRY[name]()
        print(f"  {name:14s}  {domain.description}")
        print(f"    {'synonym groups':20s}  {stats['synonym_groups']}")
        print(f"    {'query templates':20s}  {stats['query_templates']}")
        print(f"    {'detection patterns':20s}  {stats['detection_patterns']}")
        # Count total terms
        total_terms = sum(len(v) for v in domain.synonyms.values())
        print(f"    {'total terms':20s}  {total_terms}")
        print()

    total_groups = sum(s["synonym_groups"] for s in info.values())
    total_templates = sum(s["query_templates"] for s in info.values())
    total_patterns = sum(s["detection_patterns"] for s in info.values())
    print(f"Total: {len(info)} domains, {total_groups} synonym groups, "
          f"{total_templates} templates, {total_patterns} patterns")


def main():
    """Entry point for the claude-rlm CLI."""
    parser = argparse.ArgumentParser(
        prog="claude-rlm",
        description="Claude RLM — Recursive Language Model for Document Analysis",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- query ---
    p_query = subparsers.add_parser("query", help="Run a document query")
    p_query.add_argument("document", help="Path to document file")
    p_query.add_argument("query", help="Question to answer")
    p_query.add_argument("--verbose", "-v", action="store_true")
    p_query.add_argument(
        "--root-model",
        default="claude-sonnet-4-5-20250929",
        help="Root model (default: claude-sonnet-4-5-20250929)",
    )
    p_query.add_argument(
        "--sub-model",
        default="claude-haiku-4-5-20251001",
        help="Sub model (default: claude-haiku-4-5-20251001)",
    )
    p_query.add_argument(
        "--max-iterations", type=int, default=20, help="Max REPL iterations"
    )
    p_query.set_defaults(func=cmd_query)

    # --- detect ---
    p_detect = subparsers.add_parser("detect", help="Auto-detect document domain")
    p_detect.add_argument("file", help="Path to document file")
    p_detect.set_defaults(func=cmd_detect)

    # --- domains ---
    p_domains = subparsers.add_parser("domains", help="List registered domains")
    p_domains.set_defaults(func=cmd_domains)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
