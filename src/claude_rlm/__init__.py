"""
Claude RLM — Recursive Language Model for Document Analysis
============================================================

Treats documents as external environments queried via a REPL loop,
avoiding "context rot" on long documents.

Public API:
    from claude_rlm import ClaudeRLM, RLMConfig
    from claude_rlm.models import QueryResult, CostEstimate

Adapted from arXiv:2512.24601v2 (Zhang, Kraska, Khattab — MIT CSAIL).
Reference: https://github.com/alexzhang13/rlm
"""

__version__ = "0.2.0"

# Phase 1: Export models and constants from their new homes.
# In later phases, ClaudeRLM itself will move here too.
# For now, the root claude_rlm.py still provides ClaudeRLM.
from .models import RLMConfig, QueryResult, CostEstimate, TrajectoryEntry
from .constants import SUPPORTED_MODELS, MAX_OUTPUT_CHARS
from .interfaces.patterns import RLMPatterns

__all__ = [
    # Models
    "RLMConfig",
    "QueryResult",
    "CostEstimate",
    "TrajectoryEntry",

    # Patterns
    "RLMPatterns",

    # Constants
    "SUPPORTED_MODELS",
    "MAX_OUTPUT_CHARS",
]
