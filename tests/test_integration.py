"""
Integration and async tests for the v2 architecture.

Tests:
- Async orchestrator (arun)
- CLI detect/domains commands (via function calls)
- RLMPatterns import path
- Cross-module imports
"""

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claude_rlm.orchestrator import QueryOrchestrator, AsyncLLMClient
from claude_rlm.orchestrator.result_parser import parse_final_answer
from claude_rlm.interfaces.patterns import RLMPatterns


# =============================================================================
# Async Mock Client
# =============================================================================


class MockAsyncLLMClient:
    """Async LLM client for testing arun()."""

    def __init__(self, responses):
        self._responses = list(responses)
        self._call_count = 0

    async def call(self, model, max_tokens, system, messages):
        idx = min(self._call_count, len(self._responses) - 1)
        text = self._responses[idx]
        self._call_count += 1
        return (text, 100, 50)


def _sync_sub_query(prompt, context_slice=None):
    return f"Mock answer for: {prompt}"


# =============================================================================
# Async Orchestrator Tests
# =============================================================================


def test_async_orchestrator_immediate_answer():
    """arun() returns immediately when LLM gives FINAL_ANSWER."""
    client = MockAsyncLLMClient([
        "FINAL_ANSWER: $1.8M\nSOURCE_EVIDENCE: Q3 revenue\nCONFIDENCE: high"
    ])
    orch = QueryOrchestrator(
        llm_client=client,
        sub_query_fn=_sync_sub_query,
        system_prompt="test",
    )
    result = asyncio.run(orch.arun("What is revenue?", "Q3: $1.8M"))
    assert result["answer"] == "$1.8M"


def test_async_orchestrator_code_then_final():
    """arun() executes code then gets final answer."""
    client = MockAsyncLLMClient([
        '```repl\nprint("Q3 revenue is $1.8M")\n```',
        "FINAL_ANSWER: $1.8M\nCONFIDENCE: high",
    ])
    orch = QueryOrchestrator(
        llm_client=client,
        sub_query_fn=_sync_sub_query,
        system_prompt="test",
    )
    result = asyncio.run(orch.arun("What is revenue?", "Q3: $1.8M"))
    assert result["answer"] == "$1.8M"


def test_async_orchestrator_final_from_code():
    """arun() terminates when code calls FINAL()."""
    client = MockAsyncLLMClient([
        '```repl\nFINAL("Revenue is $1.8M")\n```',
    ])
    orch = QueryOrchestrator(
        llm_client=client,
        sub_query_fn=_sync_sub_query,
        system_prompt="test",
    )
    result = asyncio.run(orch.arun("What is revenue?", "Q3: $1.8M"))
    assert "1.8M" in result["answer"]


# =============================================================================
# CLI Tests (function-level, no subprocess)
# =============================================================================


def test_cli_detect_import():
    """CLI detect module can be imported from interfaces."""
    from claude_rlm.interfaces.cli import cmd_detect
    assert callable(cmd_detect)


def test_cli_domains_import():
    """CLI domains module can be imported from interfaces."""
    from claude_rlm.interfaces.cli import cmd_domains
    assert callable(cmd_domains)


def test_cli_main_import():
    """CLI main entry point can be imported."""
    from claude_rlm.interfaces.cli import main
    assert callable(main)


# =============================================================================
# RLMPatterns Tests
# =============================================================================


def test_patterns_importable():
    """RLMPatterns can be imported from interfaces."""
    assert hasattr(RLMPatterns, "find_specific_value")
    assert hasattr(RLMPatterns, "compare_entities")
    assert hasattr(RLMPatterns, "extract_all_instances")
    assert hasattr(RLMPatterns, "summarize_section")


def test_patterns_from_package():
    """RLMPatterns can be imported from main package."""
    from claude_rlm import RLMPatterns as RP
    assert RP is RLMPatterns


# =============================================================================
# Cross-Module Integration
# =============================================================================


def test_all_subpackages_importable():
    """All v2 subpackages import without errors."""
    from claude_rlm import engine
    from claude_rlm import orchestrator
    from claude_rlm import api
    from claude_rlm import document
    from claude_rlm import interfaces

    assert hasattr(engine, "Sandbox")
    assert hasattr(orchestrator, "QueryOrchestrator")
    assert hasattr(api, "AnthropicClient")
    assert hasattr(document, "DocumentRegistry")
    assert hasattr(interfaces, "RLMPatterns")


def test_async_client_importable():
    """AsyncAnthropicClient can be imported."""
    from claude_rlm.api import AsyncAnthropicClient
    assert AsyncAnthropicClient is not None


def test_async_llm_protocol_importable():
    """AsyncLLMClient protocol can be imported."""
    from claude_rlm.orchestrator import AsyncLLMClient
    assert AsyncLLMClient is not None
