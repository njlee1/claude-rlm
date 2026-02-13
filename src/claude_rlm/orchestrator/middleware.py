"""
Middleware chain for query pre/post processing.

Middlewares transform queries before they reach the LLM and results
after they come back. This replaces scattered hardcoded logic
(synonym expansion, cost tracking, logging) with composable hooks.
"""

from typing import Protocol, Dict, Any, List, Optional, runtime_checkable


@runtime_checkable
class Middleware(Protocol):
    """Protocol for query middleware.

    Implement either or both methods. Returning the input unchanged
    is valid (pass-through middleware).
    """

    def pre_query(self, question: str, context: str) -> tuple:
        """Transform question and context before the query loop.

        Returns:
            (question, context) — potentially modified.
        """
        ...

    def post_query(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the result after the query loop completes.

        Returns:
            The result dict, potentially modified.
        """
        ...


class MiddlewareChain:
    """Ordered chain of middlewares.

    Runs pre_query hooks in order, post_query hooks in reverse order
    (like middleware stacks in web frameworks).
    """

    def __init__(self, middlewares: Optional[List[Middleware]] = None):
        self._middlewares: List[Middleware] = list(middlewares or [])

    def add(self, middleware: Middleware) -> None:
        """Add a middleware to the end of the chain."""
        self._middlewares.append(middleware)

    def run_pre(self, question: str, context: str) -> tuple:
        """Run all pre_query hooks in order."""
        for mw in self._middlewares:
            if hasattr(mw, "pre_query"):
                question, context = mw.pre_query(question, context)
        return question, context

    def run_post(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Run all post_query hooks in reverse order."""
        for mw in reversed(self._middlewares):
            if hasattr(mw, "post_query"):
                result = mw.post_query(result)
        return result


# =============================================================================
# Built-in Middlewares
# =============================================================================


class VerboseLoggingMiddleware:
    """Logs query and result details to stdout."""

    def pre_query(self, question: str, context: str) -> tuple:
        print(f"[RLM] Query: {question[:100]}...")
        print(f"[RLM] Context: {len(context)} chars")
        return question, context

    def post_query(self, result: Dict[str, Any]) -> Dict[str, Any]:
        answer = result.get("answer", "")
        confidence = result.get("confidence", "unknown")
        print(f"[RLM] Answer: {str(answer)[:200]}...")
        print(f"[RLM] Confidence: {confidence}")
        return result


class CostTrackingMiddleware:
    """Accumulates cost estimates across multiple queries."""

    def __init__(self):
        self.total_root_input: int = 0
        self.total_root_output: int = 0
        self.total_sub_input: int = 0
        self.total_sub_output: int = 0
        self.query_count: int = 0

    def pre_query(self, question: str, context: str) -> tuple:
        self.query_count += 1
        return question, context

    def post_query(self, result: Dict[str, Any]) -> Dict[str, Any]:
        self.total_root_input += result.get("root_input_tokens", 0)
        self.total_root_output += result.get("root_output_tokens", 0)
        self.total_sub_input += result.get("sub_input_tokens", 0)
        self.total_sub_output += result.get("sub_output_tokens", 0)
        return result

    def get_totals(self) -> Dict[str, int]:
        return {
            "query_count": self.query_count,
            "total_root_input": self.total_root_input,
            "total_root_output": self.total_root_output,
            "total_sub_input": self.total_sub_input,
            "total_sub_output": self.total_sub_output,
        }
