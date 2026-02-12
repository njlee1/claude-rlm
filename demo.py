#!/usr/bin/env python3
"""
claude-rlm demo — Quick document analysis with domain auto-detection.

Usage:
    python demo.py                              # Show help and available domains
    python demo.py path/to/document.pdf         # Auto-detect domain, extract all topics
    python demo.py path/to/10-K.pdf revenue     # Extract specific topic
    python demo.py contract.pdf --domain=legal  # Force a specific domain

Domains: finance, legal, medical, academic, insurance, real_estate, compliance
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from domains import list_domains, DOMAIN_REGISTRY


def show_help():
    """Print usage information."""
    print("claude-rlm — Recursive Language Model for Document Analysis")
    print("=" * 60)
    print()
    print("Usage:")
    print("  python demo.py <file_path> [topics] [--domain=NAME]")
    print()
    print("Available Domains:")
    for name, info in list_domains().items():
        print(f"  {name:10s}  {info['synonym_groups']} synonym groups, "
              f"{info['query_templates']} templates, "
              f"{info['detection_patterns']} detection patterns")
    print()
    print("Domain Topics:")
    for name, cls in DOMAIN_REGISTRY.items():
        domain = cls()
        topics = ", ".join(domain.query_templates.keys())
        print(f"  {name:10s}  {topics}")
    print()
    print("Examples:")
    print("  python demo.py 10-K.pdf                    # Auto-detect → finance")
    print("  python demo.py 10-K.pdf revenue,eps        # Finance: specific metrics")
    print("  python demo.py contract.pdf --domain=legal # Legal: all topics")
    print("  python demo.py paper.pdf methodology       # Academic: specific topic")
    print()
    print("How it works:")
    print("  1. Auto-detects the document domain from content + filename")
    print("  2. Expands search terms using domain-specific synonym groups")
    print("  3. Extracts data using pre-built query templates")
    print("  4. Cross-verifies findings against multiple document sections")
    print()
    print("For Claude Code integration:")
    print("  - Agent: ~/.claude/agents/rlm.md (multi-domain)")
    print("  - Agent: ~/.claude/agents/finance-rlm.md (finance specialist)")
    print("  - Command: /rlm <file> <question>")


def demo_detect(file_path: str):
    """Demonstrate domain auto-detection on a file."""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    # Read first 3000 chars for detection
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
        print(f"  {name:10s}  {score:.2f}  {bar}")

    best_name = max(scores, key=lambda k: scores[k])
    best_score = scores[best_name]

    print()
    if best_score >= 0.3:
        domain = DOMAIN_REGISTRY[best_name]()
        print(f"Detected domain: {domain.name} ({domain.description})")
        print()
        print(f"Synonym groups available ({len(domain.synonyms)}):")
        for concept, terms in domain.synonyms.items():
            print(f"  {concept}: {', '.join(terms[:5])}{'...' if len(terms) > 5 else ''}")
        print()
        print(f"Query templates available ({len(domain.query_templates)}):")
        for topic in domain.query_templates:
            print(f"  - {topic}")
    else:
        print("No domain detected with sufficient confidence.")
        print("The document will be analyzed with generic keyword search.")

    return best_name, best_score


def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    file_path = sys.argv[1]

    if file_path in ("--help", "-h", "help"):
        show_help()
        sys.exit(0)

    # Parse optional arguments
    topics = None
    domain_name = None
    for arg in sys.argv[2:]:
        if arg.startswith("--domain="):
            domain_name = arg.split("=", 1)[1]
        else:
            topics = arg.split(",")

    # Run detection demo
    detected_name, detected_score = demo_detect(file_path)

    # Show what would happen with the RLM platform
    effective_domain = domain_name or (detected_name if detected_score >= 0.3 else "generic")
    print()
    print("=" * 60)
    print(f"To analyze this document with the RLM platform:")
    print()
    print("  from agent_sdk_bridge import RLMPlatform")
    if domain_name:
        print(f"  from domains import {DOMAIN_REGISTRY[domain_name].__name__}")
        print(f"  platform = RLMPlatform(domain={DOMAIN_REGISTRY[domain_name].__name__}())")
    else:
        print(f"  platform = RLMPlatform()  # auto-detects → {effective_domain}")
    if topics:
        print(f'  results = platform.extract("{file_path}", topics={topics})')
    else:
        print(f'  results = platform.extract("{file_path}")')
    print()
    print("Or via Claude Code:")
    print(f'  /rlm {file_path} "Your question here"')


if __name__ == "__main__":
    main()
