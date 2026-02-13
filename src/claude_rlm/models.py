"""
Typed models for the Claude RLM system.

Provides Pydantic v2 models that replace the raw dicts used in v1.
All models support backward-compatible dict export via `.to_dict()`.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator

from .constants import SUPPORTED_MODELS


# =============================================================================
# CONFIGURATION
# =============================================================================


class RLMConfig(BaseModel):
    """Configuration for the RLM system.

    Drop-in replacement for the v1 dataclass. All fields have the same
    defaults and semantics.
    """

    # Model hierarchy (root handles orchestration, sub handles verification)
    root_model: str = "claude-sonnet-4-5-20250929"
    sub_model: str = "claude-haiku-4-5-20251001"

    # Token limits
    root_max_tokens: int = 16384
    sub_max_tokens: int = 4096

    # Context management
    max_sub_calls: int = 50
    sub_call_context_limit: int = 100_000  # ~25K tokens for sub-calls

    # Verification settings
    enable_verification: bool = True

    # Cost tracking
    track_costs: bool = True

    # Debugging
    verbose: bool = False
    save_trajectory: bool = True

    # Retry settings
    max_retries: int = 3
    retry_base_delay: float = 1.0

    # Code sandbox timeout (seconds)
    code_timeout: int = 30

    @field_validator("root_model")
    @classmethod
    def validate_root_model(cls, v: str) -> str:
        if v not in SUPPORTED_MODELS:
            raise ValueError(
                f"Unknown root_model '{v}'. "
                f"Supported: {list(SUPPORTED_MODELS.keys())}"
            )
        return v

    @field_validator("sub_model")
    @classmethod
    def validate_sub_model(cls, v: str) -> str:
        if v not in SUPPORTED_MODELS:
            raise ValueError(
                f"Unknown sub_model '{v}'. "
                f"Supported: {list(SUPPORTED_MODELS.keys())}"
            )
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Backward compat: export as plain dict."""
        return self.model_dump()

    model_config = {"frozen": False}


# =============================================================================
# COST TRACKING
# =============================================================================


class CostEstimate(BaseModel):
    """Per-query cost breakdown by model tier."""

    root_model: str = ""
    root_input_tokens: int = 0
    root_output_tokens: int = 0
    root_cost_usd: float = 0.0

    sub_model: str = ""
    sub_input_tokens: int = 0
    sub_output_tokens: int = 0
    sub_cost_usd: float = 0.0

    total_cost_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Backward compat: export as plain dict."""
        return self.model_dump()


# =============================================================================
# TRAJECTORY
# =============================================================================


class TrajectoryEntry(BaseModel):
    """Single step in the RLM query trajectory (for debugging/analysis)."""

    iteration: int = 0
    role: str = ""  # "root", "sub", "code"
    content: str = ""
    tokens_in: int = 0
    tokens_out: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


# =============================================================================
# QUERY RESULT
# =============================================================================


class QueryResult(BaseModel):
    """Structured result from an RLM query.

    Replaces the raw Dict[str, Any] returned by v1's `_build_result()`.
    The `.to_dict()` method produces the exact same dict shape as v1
    for backward compatibility.
    """

    answer: Optional[str] = None
    evidence: Optional[str] = None
    confidence: str = "unknown"
    verification: Optional[str] = None
    sub_calls_used: int = 0

    # Token counts (flat, matching v1 dict keys)
    root_input_tokens: int = 0
    root_output_tokens: int = 0
    sub_input_tokens: int = 0
    sub_output_tokens: int = 0

    # Optional structured cost breakdown
    cost: Optional[CostEstimate] = None

    # Debug trajectory
    trajectory: Optional[List[TrajectoryEntry]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Backward compat: flatten to the v1 dict format.

        v1 returned:
            {"answer": ..., "evidence": None, "confidence": "unknown",
             "verification": ..., "sub_calls_used": N,
             "root_input_tokens": N, "root_output_tokens": N,
             "sub_input_tokens": N, "sub_output_tokens": N,
             "trajectory": [...] or None}

        This method produces the same shape so existing consumers
        (agent_sdk_bridge.py, test_rlm.py) keep working.
        """
        d: Dict[str, Any] = {
            "answer": self.answer,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "verification": self.verification,
            "sub_calls_used": self.sub_calls_used,
            "root_input_tokens": self.root_input_tokens,
            "root_output_tokens": self.root_output_tokens,
            "sub_input_tokens": self.sub_input_tokens,
            "sub_output_tokens": self.sub_output_tokens,
            "trajectory": (
                [t.to_dict() for t in self.trajectory]
                if self.trajectory is not None
                else None
            ),
        }
        return d
