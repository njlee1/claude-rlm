"""
RLM Domain Plugins
==================

Domain-specific synonym groups, document detection, and query templates
for the Recursive Language Model document analysis engine.

Available domains:
    - FinanceDomain: SEC filings, annual reports, financial statements
    - LegalDomain: Contracts, agreements, court filings, regulations
    - MedicalDomain: Clinical reports, drug labels, guidelines, research
    - AcademicDomain: Research papers, theses, technical reports
    - InsuranceDomain: Policies, claims, endorsements, underwriting
    - RealEstateDomain: Leases, purchase agreements, property documents
    - ComplianceDomain: Audit reports, SOX, GDPR, HIPAA, risk assessments

Usage:
    from domains import detect_domain, DOMAIN_REGISTRY

    # Auto-detect domain from document text
    domain = detect_domain(text, filename="apple_10k.pdf")
    print(domain.name)  # "finance"

    # Get synonym regex for searching
    regex = domain.get_synonym_regex("revenue")
    # "revenue|net revenue|net sales|..."

    # Use a specific domain
    from domains import FinanceDomain
    fin = FinanceDomain()
    print(fin.get_synonyms("eps"))
"""

from .base import BaseDomain
from .finance import FinanceDomain
from .legal import LegalDomain
from .medical import MedicalDomain
from .academic import AcademicDomain
from .insurance import InsuranceDomain
from .real_estate import RealEstateDomain
from .compliance import ComplianceDomain


# Registry of all built-in domains
DOMAIN_REGISTRY = {
    "finance": FinanceDomain,
    "legal": LegalDomain,
    "medical": MedicalDomain,
    "academic": AcademicDomain,
    "insurance": InsuranceDomain,
    "real_estate": RealEstateDomain,
    "compliance": ComplianceDomain,
}


def detect_domain(text: str, filename: str = "", threshold: float = 0.3) -> BaseDomain:
    """Auto-detect the domain of a document.

    Runs all registered domain detectors against the provided text and filename.
    Returns the domain with the highest confidence score above the threshold.

    Args:
        text: First ~2000 characters of the document
        filename: The document filename (e.g., "apple_10k.pdf")
        threshold: Minimum confidence score to accept a domain match (default 0.3)

    Returns:
        The best-matching domain instance, or a generic BaseDomain if no match
    """
    best_domain = None
    best_score = 0.0

    for domain_cls in DOMAIN_REGISTRY.values():
        domain = domain_cls()
        score = domain.detect(text, filename)
        if score > best_score:
            best_score = score
            best_domain = domain

    if best_domain and best_score >= threshold:
        return best_domain

    return BaseDomain()


def list_domains():
    """Return info about all registered domains."""
    return {
        name: {
            "description": cls.description,
            "synonym_groups": len(cls.synonyms),
            "query_templates": len(cls.query_templates),
            "detection_patterns": len(cls.document_patterns),
        }
        for name, cls in DOMAIN_REGISTRY.items()
    }


__all__ = [
    "BaseDomain",
    "FinanceDomain",
    "LegalDomain",
    "MedicalDomain",
    "AcademicDomain",
    "InsuranceDomain",
    "RealEstateDomain",
    "ComplianceDomain",
    "DOMAIN_REGISTRY",
    "detect_domain",
    "list_domains",
]
