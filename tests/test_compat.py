"""
Backward compatibility tests.

Ensures that both old (root-level) and new (src/ package) import paths work.
"""

import sys
from pathlib import Path

# Ensure both src/ and root are on path
SRC_DIR = str(Path(__file__).parent.parent / "src")
ROOT_DIR = str(Path(__file__).parent.parent)
for p in [SRC_DIR, ROOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)


def test_new_package_import():
    """New src/ package should be importable."""
    from claude_rlm.models import RLMConfig, QueryResult, CostEstimate, TrajectoryEntry
    from claude_rlm.constants import SUPPORTED_MODELS, MAX_OUTPUT_CHARS

    assert RLMConfig is not None
    assert QueryResult is not None
    assert isinstance(SUPPORTED_MODELS, dict)
    assert MAX_OUTPUT_CHARS == 20_000


def test_compat_module_import():
    """_compat module re-exports everything."""
    from claude_rlm._compat import (
        RLMConfig,
        QueryResult,
        CostEstimate,
        TrajectoryEntry,
        SUPPORTED_MODELS,
        MAX_OUTPUT_CHARS,
    )

    assert RLMConfig is not None
    assert QueryResult is not None
    assert isinstance(SUPPORTED_MODELS, dict)


def test_package_init_reexports():
    """Top-level claude_rlm package exports models and constants."""
    from claude_rlm import (
        RLMConfig,
        QueryResult,
        CostEstimate,
        TrajectoryEntry,
        SUPPORTED_MODELS,
        MAX_OUTPUT_CHARS,
    )

    config = RLMConfig()
    assert config.root_model == "claude-sonnet-4-5-20250929"


def test_supported_models_consistent():
    """SUPPORTED_MODELS should be the same object from both paths."""
    from claude_rlm.constants import SUPPORTED_MODELS as from_constants
    from claude_rlm import SUPPORTED_MODELS as from_init

    assert from_constants is from_init
    assert "claude-sonnet-4-5-20250929" in from_constants
    assert "claude-haiku-4-5-20251001" in from_constants
