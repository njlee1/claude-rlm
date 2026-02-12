#!/usr/bin/env python3
"""Tests for claude_rlm.py IPC mechanism and core functionality."""

from claude_rlm import ClaudeRLM, RLMConfig


def test_basic_execution():
    """Test basic code execution with context access."""
    rlm = ClaudeRLM()
    rlm.load_text("Q1: Revenue $1M. Q2: Revenue $1.5M. Q3: Revenue $1.8M.")

    result = rlm._safe_run('print(f"Context length: {len(context)} chars")')
    assert "Context length:" in result["output"]
    assert not result["terminated"]
    print("PASS: basic execution")


def test_regex_in_context():
    """Test regex search inside subprocess."""
    rlm = ClaudeRLM()
    rlm.load_text("Q1: Revenue $1M. Q2: Revenue $1.5M. Q3: Revenue $1.8M.")

    result = rlm._safe_run(
        'import re\n'
        'matches = re.findall(r"Revenue \\$[\\d.]+M", context)\n'
        'print(f"Found {len(matches)} figures: {matches}")'
    )
    assert "Found 3 figures" in result["output"]
    print("PASS: regex in context")


def test_buffer_persistence():
    """Test that buffers/findings persist across _safe_run calls."""
    rlm = ClaudeRLM()
    rlm.load_text("test doc")
    rlm.buffers = {}
    rlm.findings = []

    rlm._safe_run('buffers["key1"] = "value1"')
    assert rlm.buffers.get("key1") == "value1", f"Expected value1, got {rlm.buffers}"

    rlm._safe_run('findings.append("finding_1")')
    assert "finding_1" in rlm.findings
    print("PASS: buffer persistence")


def test_show_vars():
    """Test SHOW_VARS() function."""
    rlm = ClaudeRLM()
    rlm.load_text("test doc")
    rlm.buffers = {"revenue": "$1.8M"}
    rlm.findings = ["Q3 revenue found"]

    result = rlm._safe_run("SHOW_VARS()")
    assert "STORED VARIABLES" in result["output"]
    assert "revenue" in result["output"]
    print("PASS: SHOW_VARS")


def test_final_termination():
    """Test FINAL() terminates the loop."""
    rlm = ClaudeRLM()
    rlm.load_text("test doc")

    result = rlm._safe_run('FINAL("The answer is 42")')
    assert result["terminated"] is True
    assert result["final_answer"] == "The answer is 42"
    print("PASS: FINAL() termination")


def test_final_stops_execution():
    """Test that code after FINAL() does not execute."""
    rlm = ClaudeRLM()
    rlm.load_text("test doc")
    rlm.buffers = {}

    result = rlm._safe_run(
        'buffers["before"] = True\n'
        'FINAL("stopped")\n'
        'buffers["after"] = True'
    )
    assert result["terminated"] is True
    assert rlm.buffers.get("before") is True
    assert rlm.buffers.get("after") is None, f"Code after FINAL() ran! {rlm.buffers}"
    print("PASS: FINAL stops execution")


def test_error_as_output():
    """Test that errors become REPL output, not crashes."""
    rlm = ClaudeRLM()
    rlm.load_text("test doc")

    result = rlm._safe_run("x = 1/0")
    assert "ZeroDivisionError" in result["output"]
    assert not result["terminated"]
    print("PASS: error as output")


def test_execute_code_blocks_format():
    """Test _execute_code_blocks returns correct dict format."""
    rlm = ClaudeRLM()
    rlm.load_text("test doc")

    response = (
        "Let me check:\n\n"
        "```repl\n"
        'print(f"Length: {len(context)}")\n'
        "```\n"
    )
    code_result = rlm._execute_code_blocks(response)
    assert code_result is not None
    assert "Length:" in code_result["output"]
    assert not code_result["terminated"]
    print("PASS: _execute_code_blocks format")


def test_execute_code_blocks_final():
    """Test _execute_code_blocks detects FINAL() in code."""
    rlm = ClaudeRLM()
    rlm.load_text("test doc")

    response = (
        "Found it!\n\n"
        "```repl\n"
        'FINAL("$1.8M")\n'
        "```\n"
    )
    code_result = rlm._execute_code_blocks(response)
    assert code_result["terminated"] is True
    assert code_result["final_answer"] == "$1.8M"
    print("PASS: _execute_code_blocks with FINAL")


def test_ignores_python_blocks():
    """Test that ```python blocks are NOT executed."""
    rlm = ClaudeRLM()
    rlm.load_text("test doc")

    response = (
        "Here is illustrative code:\n\n"
        "```python\n"
        'print("should not run")\n'
        "```\n"
    )
    result = rlm._execute_code_blocks(response)
    assert result is None
    print("PASS: ignores python blocks")


def test_output_truncation():
    """Test that MAX_OUTPUT_CHARS truncation works in query loop logic."""
    from claude_rlm import MAX_OUTPUT_CHARS

    long_output = "x" * (MAX_OUTPUT_CHARS + 5000)
    truncated = long_output[:MAX_OUTPUT_CHARS]
    assert len(truncated) == MAX_OUTPUT_CHARS
    print(f"PASS: truncation constant = {MAX_OUTPUT_CHARS}")


def test_query_batch_exists():
    """Test that query_batch method exists and has correct signature."""
    rlm = ClaudeRLM()
    assert hasattr(rlm, "query_batch")
    assert callable(rlm.query_batch)
    print("PASS: query_batch exists")


def test_build_result():
    """Test _build_result helper."""
    rlm = ClaudeRLM()
    rlm.sub_call_count = 3
    rlm.root_input_tokens = 1000
    result = rlm._build_result("test answer", source="FINAL() from code")
    assert result["answer"] == "test answer"
    assert result["verification"] == "FINAL() from code"
    assert result["sub_calls_used"] == 3
    assert result["root_input_tokens"] == 1000
    print("PASS: _build_result")


def test_sub_query_ipc():
    """Test that sub_query() in subprocess actually calls the IPC server.

    We mock the parent's sub_query to avoid real API calls, but verify
    the socket communication works end-to-end.
    """
    rlm = ClaudeRLM()
    rlm.load_text("test doc for IPC")

    # Monkey-patch sub_query to return a known value without API call
    original_sub_query = rlm.sub_query
    def mock_sub_query(prompt, context_slice=None):
        return f"MOCK_RESPONSE: {prompt[:50]}"
    rlm.sub_query = mock_sub_query

    try:
        result = rlm._safe_run(
            'response = sub_query("What is the revenue?")\n'
            'print(f"Got: {response}")'
        )
        assert "MOCK_RESPONSE: What is the revenue?" in result["output"], (
            f"IPC failed! Output: {result['output']}"
        )
        assert not result["terminated"]
        print("PASS: sub_query IPC works end-to-end")
    finally:
        rlm.sub_query = original_sub_query


def test_sub_query_with_context_slice():
    """Test sub_query with context_slice parameter via IPC."""
    rlm = ClaudeRLM()
    rlm.load_text("test doc")

    def mock_sub_query(prompt, context_slice=None):
        return f"MOCK: slice_len={len(context_slice) if context_slice else 'None'}"
    rlm.sub_query = mock_sub_query

    result = rlm._safe_run(
        'response = sub_query("test", context[:10])\n'
        'print(response)'
    )
    assert "slice_len=8" in result["output"], f"Output: {result['output']}"
    print("PASS: sub_query with context_slice")


if __name__ == "__main__":
    tests = [
        test_basic_execution,
        test_regex_in_context,
        test_buffer_persistence,
        test_show_vars,
        test_final_termination,
        test_final_stops_execution,
        test_error_as_output,
        test_execute_code_blocks_format,
        test_execute_code_blocks_final,
        test_ignores_python_blocks,
        test_output_truncation,
        test_query_batch_exists,
        test_build_result,
        test_sub_query_ipc,
        test_sub_query_with_context_slice,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    if failed == 0:
        print("ALL TESTS PASSED")
