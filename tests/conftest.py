"""
Shared test fixtures for claude-rlm test suite.
"""

import sys
from pathlib import Path

import pytest

# Ensure src/ package and root-level modules are importable
SRC_DIR = str(Path(__file__).parent.parent / "src")
ROOT_DIR = str(Path(__file__).parent.parent)
for p in [SRC_DIR, ROOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture
def sample_context() -> str:
    """A short financial document snippet for testing."""
    return (
        "Q1 2024: Revenue $1.0M, Net Income $200K. "
        "Q2 2024: Revenue $1.5M, Net Income $350K. "
        "Q3 2024: Revenue $1.8M, Net Income $420K. "
        "Total Assets: $5.2M. Total Liabilities: $2.1M. "
        "Earnings Per Share (EPS): $2.35 diluted."
    )


@pytest.fixture
def sample_legal_context() -> str:
    """A short legal document snippet for testing."""
    return (
        "This Agreement is entered into by and between Party A (the 'Licensor') "
        "and Party B (the 'Licensee'). The term of this Agreement shall commence "
        "on January 1, 2024 and terminate on December 31, 2026. Either party may "
        "terminate this Agreement upon 90 days written notice."
    )
