"""
Base domain class for RLM domain-specific analysis.

Each domain (finance, legal, medical, academic) implements this interface
to provide synonym groups, document detection, and query templates.

To create a custom domain:
    1. Subclass BaseDomain
    2. Define synonyms, document_patterns, and query_templates
    3. Register it in domains/__init__.py
"""

import re
from typing import Dict, List


class BaseDomain:
    """Abstract base class for RLM domain plugins."""

    name: str = "generic"
    description: str = "Generic document analysis"

    # Term synonym groups: concept → list of equivalent terms
    # Example: {"revenue": ["revenue", "net sales", "total sales", ...]}
    synonyms: Dict[str, List[str]] = {}

    # Regex patterns that indicate this domain (used for auto-detection)
    # Example: [r"Form 10-[KQ]", r"SEC FILING", r"Consolidated Statements"]
    document_patterns: List[str] = []

    # How to split documents in this domain
    # Options: "sections", "items", "slides", "chapters", "pages"
    chunking_strategy: str = "sections"

    # Pre-built extraction queries for this domain
    # Example: {"revenue": "What is the total revenue for each period?"}
    query_templates: Dict[str, str] = {}

    def detect(self, text: str, filename: str = "") -> float:
        """Return confidence score 0.0-1.0 that this document belongs to this domain.

        Args:
            text: First ~2000 characters of the document
            filename: The document filename (e.g., "apple_10k.pdf")

        Returns:
            Float between 0.0 (definitely not this domain) and 1.0 (definitely this domain)
        """
        score = 0.0
        filename_lower = filename.lower()

        # Check document content patterns
        matches = 0
        for pattern in self.document_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1

        if self.document_patterns:
            score = min(matches / max(len(self.document_patterns) * 0.3, 1), 1.0)

        # Boost if filename contains domain-specific keywords
        for keyword in self._filename_keywords():
            if keyword in filename_lower:
                score = min(score + 0.3, 1.0)

        return round(score, 2)

    def get_synonym_regex(self, concept: str) -> str:
        """Build a regex pattern matching all synonyms for a concept.

        Args:
            concept: The concept to look up (e.g., "revenue", "party")

        Returns:
            Pipe-separated regex string (e.g., "revenue|net sales|total sales")
        """
        terms = self.synonyms.get(concept.lower(), [concept])
        escaped = [t.replace("(", r"\(").replace(")", r"\)") for t in terms]
        return "|".join(escaped)

    def get_all_synonym_regexes(self) -> Dict[str, str]:
        """Return regex patterns for all synonym groups."""
        return {concept: self.get_synonym_regex(concept) for concept in self.synonyms}

    def get_synonyms(self, concept: str) -> List[str]:
        """Look up all known synonyms for a concept."""
        return self.synonyms.get(concept.lower(), [concept])

    def _filename_keywords(self) -> List[str]:
        """Override to provide domain-specific filename keywords for detection."""
        return []
