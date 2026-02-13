"""
Constants for the Claude RLM system.

Centralized model pricing, supported model IDs, and system-wide limits.
"""

from typing import Dict, Any


# =============================================================================
# SUPPORTED MODELS
# =============================================================================

SUPPORTED_MODELS: Dict[str, Dict[str, Any]] = {
    "claude-opus-4-6": {
        "name": "Claude Opus 4.6",
        "input_per_mtok": 15.0,
        "output_per_mtok": 75.0,
    },
    "claude-sonnet-4-5-20250929": {
        "name": "Claude Sonnet 4.5",
        "input_per_mtok": 3.0,
        "output_per_mtok": 15.0,
    },
    "claude-haiku-4-5-20251001": {
        "name": "Claude Haiku 4.5",
        "input_per_mtok": 0.25,
        "output_per_mtok": 1.25,
    },
    # Legacy model IDs (still valid)
    "claude-sonnet-4-20250514": {
        "name": "Claude Sonnet 4.0",
        "input_per_mtok": 3.0,
        "output_per_mtok": 15.0,
    },
    "claude-opus-4-5-20251101": {
        "name": "Claude Opus 4.5",
        "input_per_mtok": 15.0,
        "output_per_mtok": 75.0,
    },
}

# Maximum characters of REPL output fed back to the model per iteration.
# Matches the original RLM repo's format_iteration() 20K char truncation.
MAX_OUTPUT_CHARS: int = 20_000
