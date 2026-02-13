"""
Backward compatibility shim.

Ensures that old import paths continue to work:

    # v1 (still works)
    from claude_rlm import ClaudeRLM, RLMConfig

    # v2 (preferred)
    from claude_rlm.models import RLMConfig, QueryResult
    from claude_rlm.constants import SUPPORTED_MODELS

This module re-exports the v1 public names from their new locations
so that root-level `claude_rlm.py` can delegate here, and so that
`from claude_rlm import X` works whether the user has the root file
or the src/ package installed.
"""

# Re-export models
from .models import RLMConfig, QueryResult, CostEstimate, TrajectoryEntry

# Re-export constants
from .constants import SUPPORTED_MODELS, MAX_OUTPUT_CHARS

__all__ = [
    "RLMConfig",
    "QueryResult",
    "CostEstimate",
    "TrajectoryEntry",
    "SUPPORTED_MODELS",
    "MAX_OUTPUT_CHARS",
]
