"""
Anthropic API client wrapper.

Wraps the anthropic SDK with retry logic and exposes the LLMClient
protocol interface for use with QueryOrchestrator.
"""

import asyncio
import time
from typing import Dict, List, Any

import anthropic


class AnthropicClient:
    """Anthropic API client implementing the LLMClient protocol.

    Provides exponential-backoff retry on rate limits and API errors.

    Usage:
        client = AnthropicClient(max_retries=3)
        text, in_tok, out_tok = client.call(
            model="claude-sonnet-4-5-20250929",
            max_tokens=16384,
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": "Hello"}],
        )
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
        verbose: bool = False,
    ):
        self._client = anthropic.Anthropic()
        self._max_retries = max_retries
        self._retry_base_delay = retry_base_delay
        self._verbose = verbose

    def call(
        self,
        model: str,
        max_tokens: int,
        system: str,
        messages: List[Dict[str, str]],
    ) -> tuple:
        """Call the LLM and return (response_text, input_tokens, output_tokens).

        Implements the LLMClient protocol.
        """
        response = self._call_with_retry(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return (
            response.content[0].text,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )

    def _call_with_retry(self, **kwargs) -> Any:
        """Make an API call with exponential backoff retry."""
        last_error = None
        for attempt in range(self._max_retries):
            try:
                return self._client.messages.create(**kwargs)
            except anthropic.RateLimitError as e:
                last_error = e
                delay = self._retry_base_delay * (2 ** attempt)
                if self._verbose:
                    print(
                        f"[RLM] Rate limited, retrying in {delay}s "
                        f"(attempt {attempt + 1})"
                    )
                time.sleep(delay)
            except anthropic.APIError as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    delay = self._retry_base_delay * (2 ** attempt)
                    if self._verbose:
                        print(f"[RLM] API error, retrying in {delay}s: {e}")
                    time.sleep(delay)
                else:
                    raise
        raise last_error  # type: ignore[misc]


class AsyncAnthropicClient:
    """Async Anthropic API client implementing the AsyncLLMClient protocol.

    Same retry logic as AnthropicClient but uses asyncio.sleep() and
    anthropic.AsyncAnthropic() for non-blocking calls.

    Usage:
        client = AsyncAnthropicClient(max_retries=3)
        text, in_tok, out_tok = await client.call(
            model="claude-sonnet-4-5-20250929",
            max_tokens=16384,
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": "Hello"}],
        )
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
        verbose: bool = False,
    ):
        self._client = anthropic.AsyncAnthropic()
        self._max_retries = max_retries
        self._retry_base_delay = retry_base_delay
        self._verbose = verbose

    async def call(
        self,
        model: str,
        max_tokens: int,
        system: str,
        messages: List[Dict[str, str]],
    ) -> tuple:
        """Call the LLM asynchronously and return (text, input_tokens, output_tokens)."""
        response = await self._call_with_retry(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return (
            response.content[0].text,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )

    async def _call_with_retry(self, **kwargs) -> Any:
        """Make an async API call with exponential backoff retry."""
        last_error = None
        for attempt in range(self._max_retries):
            try:
                return await self._client.messages.create(**kwargs)
            except anthropic.RateLimitError as e:
                last_error = e
                delay = self._retry_base_delay * (2 ** attempt)
                if self._verbose:
                    print(
                        f"[RLM] Rate limited, retrying in {delay}s "
                        f"(attempt {attempt + 1})"
                    )
                await asyncio.sleep(delay)
            except anthropic.APIError as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    delay = self._retry_base_delay * (2 ** attempt)
                    if self._verbose:
                        print(f"[RLM] API error, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    raise
        raise last_error  # type: ignore[misc]
