"""
Tests for the Anthropic API client wrapper.

Tests retry logic with mocked anthropic SDK error classes.
No real API calls are made.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import anthropic
from claude_rlm.api.client import AnthropicClient


# =============================================================================
# Helpers
# =============================================================================


def _make_rate_limit_error() -> anthropic.RateLimitError:
    """Create a realistic RateLimitError instance."""
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    response = httpx.Response(
        429,
        json={"error": {"message": "rate limited", "type": "rate_limit_error"}},
        request=request,
    )
    return anthropic.RateLimitError(
        message="rate limited",
        response=response,
        body={"error": {"message": "rate limited", "type": "rate_limit_error"}},
    )


def _make_internal_server_error() -> anthropic.InternalServerError:
    """Create a realistic InternalServerError (APIError subclass) instance."""
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    response = httpx.Response(
        500,
        json={"error": {"message": "internal error", "type": "internal_error"}},
        request=request,
    )
    return anthropic.InternalServerError(
        message="internal error",
        response=response,
        body={"error": {"message": "internal error", "type": "internal_error"}},
    )


def _make_mock_response():
    """Create a mock successful API response."""
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="Hello world")]
    mock_resp.usage = MagicMock(input_tokens=100, output_tokens=50)
    return mock_resp


CALL_KWARGS = dict(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    system="You are a test.",
    messages=[{"role": "user", "content": "Hello"}],
)


# =============================================================================
# Retry Tests
# =============================================================================


def test_client_retries_on_rate_limit():
    """Client retries with exponential backoff on RateLimitError."""
    mock_resp = _make_mock_response()

    client = AnthropicClient(max_retries=3, retry_base_delay=0.01)
    client._client.messages.create = MagicMock(
        side_effect=[
            _make_rate_limit_error(),
            _make_rate_limit_error(),
            mock_resp,
        ]
    )

    text, in_tok, out_tok = client.call(**CALL_KWARGS)

    assert text == "Hello world"
    assert in_tok == 100
    assert out_tok == 50
    assert client._client.messages.create.call_count == 3


def test_client_retries_on_api_error():
    """Client retries on APIError (e.g., InternalServerError)."""
    mock_resp = _make_mock_response()

    client = AnthropicClient(max_retries=3, retry_base_delay=0.01)
    client._client.messages.create = MagicMock(
        side_effect=[
            _make_internal_server_error(),
            mock_resp,
        ]
    )

    text, in_tok, out_tok = client.call(**CALL_KWARGS)

    assert text == "Hello world"
    assert client._client.messages.create.call_count == 2


def test_client_raises_after_max_retries_rate_limit():
    """Client raises RateLimitError after exhausting all retries."""
    client = AnthropicClient(max_retries=3, retry_base_delay=0.01)
    client._client.messages.create = MagicMock(
        side_effect=[
            _make_rate_limit_error(),
            _make_rate_limit_error(),
            _make_rate_limit_error(),
        ]
    )

    with pytest.raises(anthropic.RateLimitError):
        client.call(**CALL_KWARGS)

    assert client._client.messages.create.call_count == 3


def test_client_raises_after_max_retries_api_error():
    """Client raises APIError after exhausting all retries."""
    client = AnthropicClient(max_retries=2, retry_base_delay=0.01)
    client._client.messages.create = MagicMock(
        side_effect=[
            _make_internal_server_error(),
            _make_internal_server_error(),
        ]
    )

    with pytest.raises(anthropic.InternalServerError):
        client.call(**CALL_KWARGS)

    assert client._client.messages.create.call_count == 2


def test_client_no_retry_on_success():
    """Client makes exactly one call on success."""
    mock_resp = _make_mock_response()

    client = AnthropicClient(max_retries=3, retry_base_delay=0.01)
    client._client.messages.create = MagicMock(return_value=mock_resp)

    text, in_tok, out_tok = client.call(**CALL_KWARGS)

    assert text == "Hello world"
    assert client._client.messages.create.call_count == 1


def test_client_single_retry_max():
    """Client with max_retries=1 fails immediately on error."""
    client = AnthropicClient(max_retries=1, retry_base_delay=0.01)
    client._client.messages.create = MagicMock(
        side_effect=_make_rate_limit_error()
    )

    with pytest.raises(anthropic.RateLimitError):
        client.call(**CALL_KWARGS)

    assert client._client.messages.create.call_count == 1


def test_client_verbose_logs_retries(capsys):
    """Verbose mode prints retry messages."""
    mock_resp = _make_mock_response()

    client = AnthropicClient(max_retries=3, retry_base_delay=0.01, verbose=True)
    client._client.messages.create = MagicMock(
        side_effect=[
            _make_rate_limit_error(),
            mock_resp,
        ]
    )

    client.call(**CALL_KWARGS)

    captured = capsys.readouterr()
    assert "Rate limited" in captured.out
    assert "retrying" in captured.out.lower()
    assert "attempt 1" in captured.out


def test_client_verbose_logs_api_error(capsys):
    """Verbose mode prints API error retry messages."""
    mock_resp = _make_mock_response()

    client = AnthropicClient(max_retries=3, retry_base_delay=0.01, verbose=True)
    client._client.messages.create = MagicMock(
        side_effect=[
            _make_internal_server_error(),
            mock_resp,
        ]
    )

    client.call(**CALL_KWARGS)

    captured = capsys.readouterr()
    assert "API error" in captured.out
    assert "retrying" in captured.out.lower()
