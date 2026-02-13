"""
Tests for the execution engine (sandbox, IPC, code extraction).

Migrated from the original test_rlm.py + new engine-specific tests.
These test the extracted engine classes directly, without going through ClaudeRLM.
"""

import sys
from pathlib import Path

import pytest

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claude_rlm.engine import Sandbox, SandboxResult, IPCServer, extract_repl_blocks


# =============================================================================
# Code Extractor
# =============================================================================


def test_extract_repl_blocks_single():
    """Extract a single ```repl block."""
    response = (
        "Let me check:\n\n"
        "```repl\n"
        'print("hello")\n'
        "```\n"
    )
    blocks = extract_repl_blocks(response)
    assert len(blocks) == 1
    assert 'print("hello")' in blocks[0]


def test_extract_repl_blocks_multiple():
    """Extract multiple ```repl blocks."""
    response = (
        "First:\n\n```repl\nprint('a')\n```\n\n"
        "Second:\n\n```repl\nprint('b')\n```\n"
    )
    blocks = extract_repl_blocks(response)
    assert len(blocks) == 2


def test_extract_repl_blocks_ignores_python():
    """```python blocks should NOT be extracted."""
    response = (
        "Here is illustrative code:\n\n"
        "```python\n"
        'print("should not run")\n'
        "```\n"
    )
    blocks = extract_repl_blocks(response)
    assert len(blocks) == 0


def test_extract_repl_blocks_no_blocks():
    """No code blocks → empty list."""
    blocks = extract_repl_blocks("Just some text with no code.")
    assert blocks == []


def test_extract_repl_blocks_mixed():
    """Mix of ```repl and ```python — only ```repl extracted."""
    response = (
        "```python\nprint('ignore me')\n```\n"
        "```repl\nprint('run me')\n```\n"
    )
    blocks = extract_repl_blocks(response)
    assert len(blocks) == 1
    assert "run me" in blocks[0]


# =============================================================================
# IPCServer
# =============================================================================


def test_ipc_server_lifecycle():
    """IPCServer starts and stops without errors."""
    def mock_fn(prompt, context_slice=None):
        return "mock"

    server = IPCServer(mock_fn)
    port = server.start()
    assert port > 0
    server.stop()
    assert server.port == 0


def test_ipc_server_context_manager():
    """IPCServer works as a context manager."""
    def mock_fn(prompt, context_slice=None):
        return "mock"

    with IPCServer(mock_fn) as server:
        assert server.port > 0
    # After exit, port should be 0
    assert server.port == 0


def test_ipc_server_communication():
    """Test actual TCP communication with IPCServer."""
    import json
    import socket
    import struct

    def mock_fn(prompt, context_slice=None):
        return f"RESPONSE: {prompt}"

    with IPCServer(mock_fn) as server:
        # Connect and send a request
        sock = socket.create_connection(("127.0.0.1", server.port), timeout=5)
        try:
            request = {"prompt": "test question", "context_slice": None}
            req_bytes = json.dumps(request).encode("utf-8")
            sock.sendall(struct.pack("!I", len(req_bytes)))
            sock.sendall(req_bytes)

            # Read response
            length_bytes = sock.recv(4)
            msg_len = struct.unpack("!I", length_bytes)[0]
            data = sock.recv(msg_len)
            response = json.loads(data.decode("utf-8"))

            assert response["result"] == "RESPONSE: test question"
        finally:
            sock.close()


# =============================================================================
# Sandbox
# =============================================================================


def test_sandbox_basic_execution():
    """Basic code execution with context access."""
    def mock_fn(prompt, context_slice=None):
        return "mock"

    with IPCServer(mock_fn) as ipc:
        sandbox = Sandbox(timeout=30)
        result = sandbox.execute(
            code='print(f"Context length: {len(context)} chars")',
            context="Q1: Revenue $1M. Q2: Revenue $1.5M.",
            buffers={},
            findings=[],
            ipc_port=ipc.port,
        )
        assert "Context length:" in result.output
        assert not result.terminated


def test_sandbox_regex_in_context():
    """Regex search works inside the sandbox."""
    def mock_fn(prompt, context_slice=None):
        return "mock"

    with IPCServer(mock_fn) as ipc:
        sandbox = Sandbox(timeout=30)
        result = sandbox.execute(
            code=(
                'import re\n'
                'matches = re.findall(r"Revenue \\$[\\d.]+M", context)\n'
                'print(f"Found {len(matches)} figures: {matches}")'
            ),
            context="Q1: Revenue $1M. Q2: Revenue $1.5M. Q3: Revenue $1.8M.",
            buffers={},
            findings=[],
            ipc_port=ipc.port,
        )
        assert "Found 3 figures" in result.output


def test_sandbox_buffer_persistence():
    """Buffers and findings persist after execution."""
    def mock_fn(prompt, context_slice=None):
        return "mock"

    buffers = {}
    findings = []

    with IPCServer(mock_fn) as ipc:
        sandbox = Sandbox(timeout=30)

        sandbox.execute(
            code='buffers["key1"] = "value1"',
            context="test",
            buffers=buffers,
            findings=findings,
            ipc_port=ipc.port,
        )
        assert buffers.get("key1") == "value1"

        sandbox.execute(
            code='findings.append("finding_1")',
            context="test",
            buffers=buffers,
            findings=findings,
            ipc_port=ipc.port,
        )
        assert "finding_1" in findings


def test_sandbox_show_vars():
    """SHOW_VARS() prints stored variables."""
    def mock_fn(prompt, context_slice=None):
        return "mock"

    with IPCServer(mock_fn) as ipc:
        sandbox = Sandbox(timeout=30)
        result = sandbox.execute(
            code="SHOW_VARS()",
            context="test",
            buffers={"revenue": "$1.8M"},
            findings=["Q3 revenue found"],
            ipc_port=ipc.port,
        )
        assert "STORED VARIABLES" in result.output
        assert "revenue" in result.output


def test_sandbox_final_terminates():
    """FINAL() sets terminated=True."""
    def mock_fn(prompt, context_slice=None):
        return "mock"

    with IPCServer(mock_fn) as ipc:
        sandbox = Sandbox(timeout=30)
        result = sandbox.execute(
            code='FINAL("The answer is 42")',
            context="test",
            buffers={},
            findings=[],
            ipc_port=ipc.port,
        )
        assert result.terminated is True
        assert result.final_answer == "The answer is 42"


def test_sandbox_final_stops_execution():
    """Code after FINAL() should not execute."""
    def mock_fn(prompt, context_slice=None):
        return "mock"

    buffers = {}
    with IPCServer(mock_fn) as ipc:
        sandbox = Sandbox(timeout=30)
        result = sandbox.execute(
            code=(
                'buffers["before"] = True\n'
                'FINAL("stopped")\n'
                'buffers["after"] = True'
            ),
            context="test",
            buffers=buffers,
            findings=[],
            ipc_port=ipc.port,
        )
        assert result.terminated is True
        assert buffers.get("before") is True
        assert buffers.get("after") is None


def test_sandbox_error_as_output():
    """Errors become REPL output, not crashes."""
    def mock_fn(prompt, context_slice=None):
        return "mock"

    with IPCServer(mock_fn) as ipc:
        sandbox = Sandbox(timeout=30)
        result = sandbox.execute(
            code="x = 1/0",
            context="test",
            buffers={},
            findings=[],
            ipc_port=ipc.port,
        )
        assert "ZeroDivisionError" in result.output
        assert not result.terminated


def test_sandbox_sub_query_ipc():
    """sub_query() in subprocess routes through IPC to parent."""
    def mock_fn(prompt, context_slice=None):
        return f"MOCK_RESPONSE: {prompt[:50]}"

    with IPCServer(mock_fn) as ipc:
        sandbox = Sandbox(timeout=30)
        result = sandbox.execute(
            code=(
                'response = sub_query("What is the revenue?")\n'
                'print(f"Got: {response}")'
            ),
            context="test doc for IPC",
            buffers={},
            findings=[],
            ipc_port=ipc.port,
        )
        assert "MOCK_RESPONSE: What is the revenue?" in result.output
        assert not result.terminated


def test_sandbox_sub_query_with_context_slice():
    """sub_query() with context_slice parameter works via IPC."""
    def mock_fn(prompt, context_slice=None):
        return f"MOCK: slice_len={len(context_slice) if context_slice else 'None'}"

    with IPCServer(mock_fn) as ipc:
        sandbox = Sandbox(timeout=30)
        result = sandbox.execute(
            code=(
                'response = sub_query("test", context[:10])\n'
                'print(response)'
            ),
            context="test doc for slice",
            buffers={},
            findings=[],
            ipc_port=ipc.port,
        )
        assert "slice_len=10" in result.output


def test_sandbox_result_to_dict():
    """SandboxResult.to_dict() matches the v1 dict format."""
    result = SandboxResult(
        output="some output",
        terminated=True,
        final_answer="$1.8M",
    )
    d = result.to_dict()
    assert d["output"] == "some output"
    assert d["terminated"] is True
    assert d["final_answer"] == "$1.8M"
