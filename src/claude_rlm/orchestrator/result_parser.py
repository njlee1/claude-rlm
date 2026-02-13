"""
Result parsing utilities.

Extracts structured answers from LLM responses using regex patterns.
These are pure functions — no side effects, fully testable without mocks.
"""

import re
from typing import Dict, Any, Optional, List


def parse_final_answer(
    response: str,
    sub_call_count: int = 0,
    root_input_tokens: int = 0,
    root_output_tokens: int = 0,
    sub_input_tokens: int = 0,
    sub_output_tokens: int = 0,
    trajectory: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Parse FINAL_ANSWER: format from LLM response.

    Extracts answer, evidence, confidence, and verification from
    the structured output format:

        FINAL_ANSWER: <answer>
        SOURCE_EVIDENCE: <evidence>
        CONFIDENCE: <high|medium|low>
        VERIFICATION_METHOD: <method>

    Args:
        response: Raw LLM response text.
        sub_call_count: Number of sub-queries used.
        root_input_tokens: Root model input token count.
        root_output_tokens: Root model output token count.
        sub_input_tokens: Sub model input token count.
        sub_output_tokens: Sub model output token count.
        trajectory: Optional debug trajectory.

    Returns:
        Dict matching the v1 result shape.
    """
    result: Dict[str, Any] = {
        "answer": None,
        "evidence": None,
        "confidence": "unknown",
        "verification": None,
        "sub_calls_used": sub_call_count,
        "root_input_tokens": root_input_tokens,
        "root_output_tokens": root_output_tokens,
        "sub_input_tokens": sub_input_tokens,
        "sub_output_tokens": sub_output_tokens,
        "trajectory": trajectory,
    }

    patterns = {
        "answer": r"FINAL_ANSWER:\s*(.+?)(?=SOURCE_EVIDENCE:|CONFIDENCE:|VERIFICATION_METHOD:|$)",
        "evidence": r"SOURCE_EVIDENCE:\s*(.+?)(?=CONFIDENCE:|VERIFICATION_METHOD:|$)",
        "confidence": r"CONFIDENCE:\s*(\w+)",
        "verification": r"VERIFICATION_METHOD:\s*(.+?)(?=$)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            result[key] = match.group(1).strip()

    if not result["answer"]:
        result["answer"] = response

    return result


def build_result(
    answer: str,
    source: str = "unknown",
    sub_call_count: int = 0,
    root_input_tokens: int = 0,
    root_output_tokens: int = 0,
    sub_input_tokens: int = 0,
    sub_output_tokens: int = 0,
    trajectory: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Build a result dict from a FINAL() termination.

    Args:
        answer: The final answer string.
        source: How the answer was produced (e.g. "FINAL() from code").
        sub_call_count: Number of sub-queries used.
        root_input_tokens: Root model input token count.
        root_output_tokens: Root model output token count.
        sub_input_tokens: Sub model input token count.
        sub_output_tokens: Sub model output token count.
        trajectory: Optional debug trajectory.

    Returns:
        Dict matching the v1 result shape.
    """
    return {
        "answer": answer,
        "evidence": None,
        "confidence": "unknown",
        "verification": source,
        "sub_calls_used": sub_call_count,
        "root_input_tokens": root_input_tokens,
        "root_output_tokens": root_output_tokens,
        "sub_input_tokens": sub_input_tokens,
        "sub_output_tokens": sub_output_tokens,
        "trajectory": trajectory,
    }
