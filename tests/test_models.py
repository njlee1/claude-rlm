"""
Tests for Pydantic models in src/claude_rlm/models.py.

Validates:
- RLMConfig validation and defaults
- QueryResult construction and .to_dict() backward compat
- CostEstimate serialization
- TrajectoryEntry basics
"""

import sys
from pathlib import Path

import pytest

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claude_rlm.models import RLMConfig, QueryResult, CostEstimate, TrajectoryEntry
from claude_rlm.constants import SUPPORTED_MODELS


# =============================================================================
# RLMConfig
# =============================================================================


def test_rlmconfig_defaults():
    """Default config should use Sonnet 4.5 root + Haiku 4.5 sub."""
    config = RLMConfig()
    assert config.root_model == "claude-sonnet-4-5-20250929"
    assert config.sub_model == "claude-haiku-4-5-20251001"
    assert config.root_max_tokens == 16384
    assert config.max_sub_calls == 50
    assert config.verbose is False


def test_rlmconfig_custom():
    """Custom values should override defaults."""
    config = RLMConfig(
        root_model="claude-opus-4-6",
        verbose=True,
        max_retries=5,
    )
    assert config.root_model == "claude-opus-4-6"
    assert config.verbose is True
    assert config.max_retries == 5


def test_rlmconfig_invalid_model():
    """Unknown model ID should raise ValidationError."""
    with pytest.raises(Exception):  # Pydantic ValidationError
        RLMConfig(root_model="gpt-4-turbo")


def test_rlmconfig_to_dict():
    """to_dict() should return a plain dict with all fields."""
    config = RLMConfig()
    d = config.to_dict()
    assert isinstance(d, dict)
    assert d["root_model"] == "claude-sonnet-4-5-20250929"
    assert "verbose" in d
    assert "code_timeout" in d


# =============================================================================
# QueryResult
# =============================================================================


def test_queryresult_defaults():
    """Empty QueryResult has safe defaults."""
    result = QueryResult()
    assert result.answer is None
    assert result.confidence == "unknown"
    assert result.sub_calls_used == 0
    assert result.trajectory is None


def test_queryresult_to_dict_v1_shape():
    """to_dict() should produce the exact v1 dict shape."""
    result = QueryResult(
        answer="$1.8M",
        verification="FINAL() from code",
        sub_calls_used=3,
        root_input_tokens=1000,
        root_output_tokens=500,
    )
    d = result.to_dict()

    # Must have all v1 keys
    assert d["answer"] == "$1.8M"
    assert d["verification"] == "FINAL() from code"
    assert d["sub_calls_used"] == 3
    assert d["root_input_tokens"] == 1000
    assert d["root_output_tokens"] == 500
    assert d["evidence"] is None
    assert d["confidence"] == "unknown"
    assert d["sub_input_tokens"] == 0
    assert d["sub_output_tokens"] == 0
    assert d["trajectory"] is None


def test_queryresult_with_trajectory():
    """QueryResult with trajectory entries serializes correctly."""
    entries = [
        TrajectoryEntry(iteration=1, role="root", content="checking revenue"),
        TrajectoryEntry(iteration=2, role="code", content="regex match"),
    ]
    result = QueryResult(answer="$1.8M", trajectory=entries)
    d = result.to_dict()

    assert len(d["trajectory"]) == 2
    assert d["trajectory"][0]["role"] == "root"
    assert d["trajectory"][1]["iteration"] == 2


# =============================================================================
# CostEstimate
# =============================================================================


def test_cost_estimate_defaults():
    """CostEstimate starts at zero."""
    cost = CostEstimate()
    assert cost.total_cost_usd == 0.0
    assert cost.root_cost_usd == 0.0


def test_cost_estimate_to_dict():
    """to_dict() on CostEstimate returns all fields."""
    cost = CostEstimate(
        root_model="claude-sonnet-4-5-20250929",
        root_input_tokens=10000,
        root_cost_usd=0.03,
        total_cost_usd=0.035,
    )
    d = cost.to_dict()
    assert d["root_model"] == "claude-sonnet-4-5-20250929"
    assert d["total_cost_usd"] == 0.035


# =============================================================================
# TrajectoryEntry
# =============================================================================


def test_trajectory_entry():
    """TrajectoryEntry captures iteration metadata."""
    entry = TrajectoryEntry(
        iteration=1,
        role="root",
        content="Found revenue mention on line 42",
        tokens_in=500,
        tokens_out=200,
    )
    assert entry.iteration == 1
    d = entry.to_dict()
    assert d["tokens_in"] == 500
