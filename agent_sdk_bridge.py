#!/usr/bin/env python3
"""
RLM Platform — Agent SDK Bridge
================================

Wraps the ClaudeRLM engine for deployment as a production platform
via Anthropic's Agent SDK. Supports multiple domains (finance, legal,
medical, academic) with auto-detection.

Provides:
- Domain auto-detection from document content and filename
- Synonym-aware extraction using domain-specific term groups
- Pre-built query templates per domain
- Batch processing of multiple queries per document
- Structured JSON output with source verification

Adapted from the RLM paradigm by Zhang, Kraska, and Khattab (MIT CSAIL, arXiv:2512.24601v2).
Reference implementation: https://github.com/alexzhang13/rlm

Usage:
    from agent_sdk_bridge import RLMPlatform

    # Auto-detect domain
    platform = RLMPlatform()
    results = platform.extract("/path/to/document.pdf")

    # Or specify a domain explicitly
    from domains import LegalDomain
    platform = RLMPlatform(domain=LegalDomain())
    results = platform.extract("/path/to/contract.pdf")

    # Backward compatible: finance-specific shortcut
    from agent_sdk_bridge import FinanceRLMPlatform
    results = FinanceRLMPlatform().extract_financials("/path/to/10-K.pdf")
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from claude_rlm import ClaudeRLM, RLMConfig
from domains import BaseDomain, detect_domain
from domains.finance import FinanceDomain


# =============================================================================
# PLATFORM CONFIGURATION
# =============================================================================

@dataclass
class PlatformConfig:
    """Configuration for the RLM Platform."""
    root_model: str = "claude-sonnet-4-5-20250929"
    sub_model: str = "claude-haiku-4-5-20251001"
    max_iterations: int = 20
    max_sub_calls: int = 10
    verbose: bool = False


# =============================================================================
# RLM PLATFORM (domain-agnostic)
# =============================================================================

class RLMPlatform:
    """Production platform for document analysis using RLM.

    Supports any domain via the plugin system. If no domain is specified,
    auto-detects from the document content and filename.

    Args:
        domain: A domain plugin instance (e.g., FinanceDomain()). If None,
                auto-detection runs when a document is loaded.
        config: Platform configuration (model selection, limits, etc.)
    """

    def __init__(
        self,
        domain: Optional[BaseDomain] = None,
        config: Optional[PlatformConfig] = None,
    ):
        self.config = config or PlatformConfig()
        self.domain = domain
        self.rlm = ClaudeRLM(
            config=RLMConfig(
                root_model=self.config.root_model,
                sub_model=self.config.sub_model,
                max_sub_calls=self.config.max_sub_calls,
                verbose=self.config.verbose,
            )
        )
        self._loaded_path: Optional[str] = None

    def load_document(self, file_path: str) -> Dict[str, Any]:
        """Load a document and return its metadata.

        If no domain was specified, auto-detects from the first ~2000 chars.

        Supports: PDF, DOCX, PPTX, TXT, CSV
        """
        self._loaded_path = file_path
        summary = self.rlm.load_document(file_path)

        # Auto-detect domain if not explicitly set
        if self.domain is None:
            preview = summary[:2000] if isinstance(summary, str) else ""
            self.domain = detect_domain(preview, Path(file_path).name)

        return {
            "file_path": file_path,
            "file_size": Path(file_path).stat().st_size,
            "file_type": Path(file_path).suffix.lower(),
            "domain": self.domain.name,
            "summary": summary,
        }

    def process_document(
        self,
        file_path: str,
        queries: List[str],
        max_iterations: int = 20,
    ) -> Dict[str, Any]:
        """Process a document with custom queries.

        Args:
            file_path: Path to the document
            queries: List of questions to answer
            max_iterations: Max REPL iterations per query

        Returns:
            Dict with metadata and per-query results
        """
        if self._loaded_path != file_path:
            self.load_document(file_path)

        results = self.rlm.query_batch(queries, max_iterations=max_iterations)

        return {
            "file_path": file_path,
            "domain": self.domain.name if self.domain else "generic",
            "query_count": len(queries),
            "results": [
                {
                    "query": q,
                    "answer": r.get("final_answer", ""),
                    "iterations": r.get("iterations", 0),
                    "sub_calls": r.get("sub_calls", 0),
                    "confidence": self._assess_confidence(r),
                }
                for q, r in zip(queries, results)
            ],
        }

    def extract(
        self,
        file_path: str,
        topics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Extract information using domain-specific query templates.

        Uses the domain's pre-built query templates with synonym expansion.

        Args:
            file_path: Path to the document
            topics: Which topics to extract. Defaults to all templates in the domain.
                    For finance: "revenue", "expenses", "net_income", etc.
                    For legal: "parties", "obligations", "termination", etc.

        Returns:
            Structured dict with extracted data
        """
        if self._loaded_path != file_path:
            self.load_document(file_path)

        domain = self.domain or BaseDomain()

        if topics is None:
            topics = list(domain.query_templates.keys())

        queries = []
        for topic in topics:
            template = domain.query_templates.get(topic)
            if template is None:
                continue

            # Expand synonyms into the query template
            synonyms = domain.synonyms.get(topic, [])
            synonym_str = ", ".join(f'"{s}"' for s in synonyms[:8])
            query = template.format(synonyms=synonym_str)
            queries.append(query)

        return self.process_document(file_path, queries)

    # ── Backward-compatible finance shortcuts ──

    def extract_financials(
        self,
        file_path: str,
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Extract standard financial metrics. Convenience alias for extract()."""
        if self.domain is None:
            self.domain = FinanceDomain()
        return self.extract(file_path, topics=metrics)

    def extract_10k(self, file_path: str) -> Dict[str, Any]:
        """Specialized extraction for SEC 10-K filings."""
        if self.domain is None:
            self.domain = FinanceDomain()
        return self.extract(
            file_path,
            topics=["revenue", "expenses", "net_income",
                     "risk_factors", "cash_flow", "eps"],
        )

    def compare_periods(
        self,
        file_path: str,
        metric: str,
        periods: List[str],
    ) -> Dict[str, Any]:
        """Compare a metric across multiple periods using synonym expansion."""
        if self._loaded_path != file_path:
            self.load_document(file_path)

        domain = self.domain or BaseDomain()
        synonyms = domain.get_synonyms(metric)
        synonym_str = ", ".join(f'"{s}"' for s in synonyms[:8])

        query = (
            f"Compare {metric} across these periods: {', '.join(periods)}. "
            f"The document may use any of these terms: {synonym_str}. "
            f"For each period, report the exact value and calculate the "
            f"absolute and percentage change between consecutive periods."
        )

        return self.process_document(file_path, [query])

    @staticmethod
    def _assess_confidence(result: Dict[str, Any]) -> str:
        """Heuristic confidence assessment based on RLM execution metrics."""
        answer = result.get("final_answer", "")
        iterations = result.get("iterations", 0)
        sub_calls = result.get("sub_calls", 0)

        if not answer or answer == "NOT FOUND":
            return "low"
        if iterations <= 3 and sub_calls >= 1:
            return "high"
        if iterations <= 8:
            return "medium"
        return "low"


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

class FinanceRLMPlatform(RLMPlatform):
    """Finance-specific platform. Backward-compatible alias for RLMPlatform."""

    def __init__(self, config: Optional[PlatformConfig] = None):
        super().__init__(domain=FinanceDomain(), config=config)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface for document analysis with domain auto-detection."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python agent_sdk_bridge.py <file_path> [topic1,topic2,...] [--domain=NAME]")
        print("\nDomains: finance, legal, medical, academic (auto-detected if omitted)")
        print("\nFinance topics: revenue, expenses, net_income, risk_factors, cash_flow, eps")
        print("Legal topics:   parties, key_terms, obligations, termination, liability, governing_law")
        print("Medical topics: diagnoses, medications, lab_results, adverse_effects, vital_signs, treatment_plan")
        print("Academic topics: methodology, findings, limitations, contributions, datasets")
        print("\nExamples:")
        print("  python agent_sdk_bridge.py 10-K.pdf")
        print("  python agent_sdk_bridge.py 10-K.pdf revenue,net_income")
        print("  python agent_sdk_bridge.py contract.pdf --domain=legal")
        sys.exit(1)

    file_path = sys.argv[1]
    topics = None
    domain = None

    for arg in sys.argv[2:]:
        if arg.startswith("--domain="):
            domain_name = arg.split("=", 1)[1]
            from domains import DOMAIN_REGISTRY
            domain_cls = DOMAIN_REGISTRY.get(domain_name)
            if domain_cls:
                domain = domain_cls()
            else:
                print(f"Unknown domain: {domain_name}")
                print(f"Available: {', '.join(DOMAIN_REGISTRY.keys())}")
                sys.exit(1)
        else:
            topics = arg.split(",")

    platform = RLMPlatform(domain=domain)
    results = platform.extract(file_path, topics=topics)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
