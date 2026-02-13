"""
Cost tracking utilities.

Computes per-query and cumulative API costs based on model pricing.
"""

from typing import Dict, Any

from ..constants import SUPPORTED_MODELS


def compute_cost(
    root_model: str,
    root_input_tokens: int,
    root_output_tokens: int,
    sub_model: str,
    sub_input_tokens: int,
    sub_output_tokens: int,
) -> Dict[str, Any]:
    """Compute cost breakdown by model tier.

    Returns the same dict shape as v1's get_cost_estimate().
    """
    root_pricing = SUPPORTED_MODELS.get(
        root_model,
        {"input_per_mtok": 3.0, "output_per_mtok": 15.0},
    )
    sub_pricing = SUPPORTED_MODELS.get(
        sub_model,
        {"input_per_mtok": 0.25, "output_per_mtok": 1.25},
    )

    root_cost = (
        (root_input_tokens / 1_000_000) * root_pricing["input_per_mtok"]
        + (root_output_tokens / 1_000_000) * root_pricing["output_per_mtok"]
    )
    sub_cost = (
        (sub_input_tokens / 1_000_000) * sub_pricing["input_per_mtok"]
        + (sub_output_tokens / 1_000_000) * sub_pricing["output_per_mtok"]
    )

    return {
        "root_model": root_model,
        "root_input_tokens": root_input_tokens,
        "root_output_tokens": root_output_tokens,
        "root_cost_usd": round(root_cost, 4),
        "sub_model": sub_model,
        "sub_input_tokens": sub_input_tokens,
        "sub_output_tokens": sub_output_tokens,
        "sub_cost_usd": round(sub_cost, 4),
        "total_cost_usd": round(root_cost + sub_cost, 4),
    }
