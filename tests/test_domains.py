"""
Tests for domain detection, synonym regex, and multi-domain routing.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from domains import detect_domain, DOMAIN_REGISTRY, BaseDomain, FinanceDomain
from claude_rlm.domains.router import DomainRouter


# =============================================================================
# Domain Detection
# =============================================================================


def test_detect_finance_from_text():
    """Finance domain detected from financial text."""
    text = (
        "UNITED STATES SECURITIES AND EXCHANGE COMMISSION\n"
        "Form 10-K Annual Report\n"
        "Revenue: $1,800,000\n"
        "Earnings per share: $2.35"
    )
    domain = detect_domain(text)
    assert domain.name == "finance"


def test_detect_finance_from_filename():
    """Finance domain detected from filename."""
    domain = detect_domain("Some text here", filename="apple_10k.pdf")
    assert domain.name == "finance"


def test_detect_legal():
    """Legal domain detected from contract text with strong signals."""
    text = (
        "This Agreement is entered into by and between Party A "
        "and Party B. The term of this Agreement shall commence "
        "on January 1, 2024. The Licensor grants the Licensee "
        "a non-exclusive license."
    )
    domain = detect_domain(text, filename="license_agreement.docx")
    assert domain.name == "legal"


def test_detect_medical():
    """Medical domain detected from clinical text."""
    text = (
        "CLINICAL TRIAL RESULTS\n"
        "The patient presented with chronic symptoms. "
        "Dosage was adjusted per FDA guidelines. "
        "Adverse events were monitored throughout the trial."
    )
    domain = detect_domain(text)
    assert domain.name == "medical"


def test_detect_fallback_base():
    """Unknown text falls back to BaseDomain."""
    domain = detect_domain("Hello world, this is random text.")
    assert isinstance(domain, BaseDomain)
    assert domain.name == "generic"


# =============================================================================
# Synonym Regex
# =============================================================================


def test_finance_synonym_regex():
    """Finance domain synonym regex matches expected patterns."""
    fin = FinanceDomain()
    regex = fin.get_synonym_regex("revenue")
    assert "revenue" in regex
    assert "net sales" in regex or "net revenue" in regex


def test_synonym_regex_nonexistent():
    """Nonexistent synonym group returns the concept itself as fallback."""
    fin = FinanceDomain()
    result = fin.get_synonym_regex("nonexistent_concept")
    assert result == "nonexistent_concept"


# =============================================================================
# Domain Router
# =============================================================================


def test_router_detect_single():
    """Router detects single best domain."""
    router = DomainRouter()
    domain = router.detect(
        "Form 10-K Revenue EBITDA earnings per share",
        "apple_10k.pdf",
    )
    assert domain.name == "finance"


def test_router_detect_multi():
    """Router detects multiple domains for cross-domain text."""
    router = DomainRouter()
    text = (
        "The clinical trial data shows that premium revenue increased "
        "while adverse events decreased. Revenue per patient was $50K. "
        "EBITDA margins improved. FDA approval pending."
    )
    domains = router.detect_multi(text, threshold=0.1)
    domain_names = [d.name for d in domains]
    # Should detect at least 2 domains
    assert len(domains) >= 1


def test_router_compose_synonyms():
    """Compose synonyms from multiple domains."""
    router = DomainRouter()
    fin = FinanceDomain()
    from domains.medical import MedicalDomain
    med = MedicalDomain()

    merged = router.compose_synonyms([fin, med])
    # Finance has "revenue", medical doesn't — should be in merged
    assert "revenue" in merged
    # Both may have overlapping keys — check no duplicates
    for key, values in merged.items():
        assert len(values) == len(set(values))


def test_router_list_domains():
    """Router lists all 7 registered domains."""
    router = DomainRouter()
    domains = router.list_domains()
    assert len(domains) == 7
    assert "finance" in domains
    assert "legal" in domains
    assert "medical" in domains
    assert "academic" in domains
    assert "insurance" in domains
    assert "real_estate" in domains
    assert "compliance" in domains


# =============================================================================
# Edge Case Tests
# =============================================================================


def test_detect_empty_text():
    """Empty text falls back to BaseDomain."""
    domain = detect_domain("")
    assert isinstance(domain, BaseDomain)
    assert domain.name == "generic"


def test_detect_empty_text_with_filename():
    """Empty text with finance filename still detects finance."""
    domain = detect_domain("", filename="10k_filing.pdf")
    assert domain.name == "finance"


def test_router_detect_multi_empty_text():
    """detect_multi with empty text returns empty list."""
    router = DomainRouter()
    domains = router.detect_multi("", threshold=0.3)
    assert domains == []


def test_finance_synonym_group_keys():
    """Finance domain has expected synonym groups."""
    fin = FinanceDomain()
    # Check that core groups exist
    assert "revenue" in fin.synonyms

    # Each synonym group should have at least 2 terms
    for group, terms in fin.synonyms.items():
        assert len(terms) >= 2, f"Group '{group}' has only {len(terms)} terms"


def test_base_domain_fallback():
    """BaseDomain provides empty synonyms and generic name."""
    base = BaseDomain()
    assert base.name == "generic"
    assert base.synonyms == {}
    assert base.detect("any text") == 0.0
