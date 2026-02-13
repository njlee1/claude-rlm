"""
Multi-domain router and synonym composition.

Extends the existing domain detection with multi-domain support,
enabling cross-domain document analysis.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Import from the root-level domains package
_ROOT_DIR = str(Path(__file__).parent.parent.parent.parent)
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from domains import DOMAIN_REGISTRY, BaseDomain, detect_domain


class DomainRouter:
    """Multi-domain detection and synonym composition.

    Extends the existing single-domain detect_domain() with:
    - detect_multi(): returns all domains above a threshold
    - compose_synonyms(): merges synonym groups from multiple domains

    Usage:
        router = DomainRouter()

        # Single best domain
        domain = router.detect("Revenue was $1.8M...", "apple_10k.pdf")

        # Multiple domains for cross-domain docs
        domains = router.detect_multi(
            "Premium revenue increased while clinical trials progressed...",
            threshold=0.2,
        )

        # Merged synonyms for cross-domain search
        synonyms = router.compose_synonyms(domains)
    """

    def __init__(self, registry: Optional[Dict] = None):
        self._registry = registry or DOMAIN_REGISTRY

    def detect(self, text: str, filename: str = "") -> BaseDomain:
        """Detect the single best domain.

        Delegates to the existing detect_domain() function.
        """
        return detect_domain(text, filename)

    def detect_multi(
        self,
        text: str,
        filename: str = "",
        threshold: float = 0.3,
    ) -> List[BaseDomain]:
        """Detect all domains above a confidence threshold.

        Args:
            text: First ~2000 characters of the document.
            filename: The document filename.
            threshold: Minimum confidence score to include a domain.

        Returns:
            List of matching domains, sorted by confidence (highest first).
        """
        scored = []
        for domain_cls in self._registry.values():
            domain = domain_cls()
            score = domain.detect(text, filename)
            if score >= threshold:
                scored.append((score, domain))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [domain for _, domain in scored]

    def compose_synonyms(self, domains: List[BaseDomain]) -> Dict[str, List[str]]:
        """Merge synonym groups from multiple domains.

        When a key exists in multiple domains, lists are concatenated
        and deduplicated. This enables cross-domain searches.

        Args:
            domains: List of domain instances to merge.

        Returns:
            Merged synonym dict with deduplicated values.
        """
        merged: Dict[str, List[str]] = {}
        for domain in domains:
            for key, synonyms in domain.synonyms.items():
                if key in merged:
                    existing = set(merged[key])
                    for s in synonyms:
                        if s not in existing:
                            merged[key].append(s)
                            existing.add(s)
                else:
                    merged[key] = list(synonyms)
        return merged

    def list_domains(self) -> Dict[str, Dict]:
        """List all registered domains with stats."""
        result = {}
        for name, cls in self._registry.items():
            total_terms = sum(len(v) for v in cls.synonyms.values())
            result[name] = {
                "description": cls.description,
                "synonym_groups": len(cls.synonyms),
                "total_terms": total_terms,
                "query_templates": len(cls.query_templates),
                "detection_patterns": len(cls.document_patterns),
            }
        return result
