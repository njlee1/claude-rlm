# Claude RLM v2 — Debugging & Best Practices Audit

Comprehensive review of the v2 layered architecture covering security,
error handling, testing, and maintainability.

---

## Critical Issues

### 1. Command Injection in PDFIngestor

**File:** `src/claude_rlm/document/ingestors.py:41`
**Also:** `claude_rlm.py:347-356`

```python
f"result = converter.convert('{path}'); "
```

If `path` contains a single quote (e.g., `report's_final.pdf`), the
generated Python code breaks or executes unintended code.

**Fix:** Pass path via environment variable or temp file, never via
string interpolation inside subprocess code:

```python
import os
env = {**os.environ, "RLM_DOC_PATH": str(path)}
subprocess.run(
    ["python3", "-c",
     "import os; from docling.document_converter import DocumentConverter; "
     "converter = DocumentConverter(); "
     "result = converter.convert(os.environ['RLM_DOC_PATH']); "
     "print(result.document.export_to_markdown())"],
    capture_output=True, text=True, timeout=120, env=env,
)
```

---

### 2. Unbounded IPC Message Size

**File:** `src/claude_rlm/engine/ipc.py:63-66`

```python
msg_len = struct.unpack("!I", length_bytes)[0]
data = self.rfile.read(msg_len)  # Up to 4GB
```

A buggy subprocess could send a huge length prefix, causing the parent
to allocate gigabytes of memory.

**Fix:** Add a size guard:

```python
MAX_IPC_MSG = 100 * 1024 * 1024  # 100MB
msg_len = struct.unpack("!I", length_bytes)[0]
if msg_len > MAX_IPC_MSG:
    raise ValueError(f"IPC message too large: {msg_len}")
data = self.rfile.read(msg_len)
```

---

## Error Handling Issues

### 3. Silent Exception Swallowing (7 instances)

Every bare `except Exception: pass` is a silent failure that makes
debugging nearly impossible.

| File | Line(s) | Context |
|------|---------|---------|
| `engine/sandbox.py` | 141-142 | State file read failure |
| `engine/sandbox.py` | 154-155 | Termination file read failure |
| `engine/ipc.py` | 86-87 | Error response write failure |
| `document/ingestors.py` | 50-51 | Docling extraction failure |
| `document/ingestors.py` | 63-64 | pdftotext extraction failure |
| `document/ingestors.py` | 87-88 | Pandoc extraction failure |
| `document/ingestors.py` | 132 | Plain text fallback failure |

**Best practice:** Log a warning before swallowing. At minimum:

```python
import logging
logger = logging.getLogger(__name__)

try:
    ...
except Exception:
    logger.debug("State file read failed, using defaults", exc_info=True)
```

For ingestors specifically, collecting the exception context makes the
final `RuntimeError` far more debuggable:

```python
errors = []
try:
    return self._try_docling(path)
except Exception as e:
    errors.append(f"docling: {e}")
try:
    return self._try_pdftotext(path)
except Exception as e:
    errors.append(f"pdftotext: {e}")
raise RuntimeError(f"PDF extraction failed: {'; '.join(errors)}")
```

---

### 4. Missing IPC JSON Validation

**File:** `src/claude_rlm/engine/ipc.py:67-70`

```python
request = json.loads(data.decode("utf-8"))
prompt = request.get("prompt", "")
```

If the subprocess sends `{"foo": "bar"}`, the handler silently processes
an empty prompt. Validate required fields:

```python
request = json.loads(data.decode("utf-8"))
if "prompt" not in request:
    raise ValueError(f"Missing 'prompt' in IPC request: {list(request.keys())}")
```

---

## Architecture & Maintainability

### 5. run() / arun() Duplication (280 lines)

**File:** `src/claude_rlm/orchestrator/query_loop.py`

`run()` (lines 85-231) and `arun()` (lines 233-367) are 95% identical.
The only difference is `await` on LLM calls.

**Fix:** Extract the loop body into a generator or use a strategy
callback:

```python
def _build_loop_state(self, question, context):
    """Shared setup for run() and arun()."""
    question, context = self.middleware.run_pre(question, context)
    return {
        "buffers": {}, "findings": [], "trajectory": [],
        "root_in": 0, "root_out": 0,
        "question": question, "context": context,
        "messages": [{"role": "user", "content": f"Answer: {question}\n\n..."}],
    }

def _process_response(self, state, response_text, in_tok, out_tok):
    """Shared response processing. Returns (result, done) or (None, False)."""
    ...
```

Then `run()` calls `self.llm_client.call(...)` and `arun()` calls
`await self.llm_client.call(...)`, but both share the processing logic.

---

### 6. Loose Tuple Return Types

**File:** `src/claude_rlm/orchestrator/query_loop.py:31, 45`

```python
def call(...) -> tuple:  # What's in the tuple?
```

Python 3.9+ supports `tuple[str, int, int]`. This catches mismatches
at type-check time:

```python
def call(...) -> tuple[str, int, int]:
    """Return (response_text, input_tokens, output_tokens)."""
```

---

## Test Suite Gaps

### 7. Missing Error Path Tests

The test suite covers happy paths well but has zero tests for failure
scenarios. Critical gaps:

**API client retries** — No tests verify retry behavior:
```python
def test_client_retries_on_rate_limit():
    """Client retries with exponential backoff on RateLimitError."""
    mock = Mock(side_effect=[
        anthropic.RateLimitError(...),
        anthropic.RateLimitError(...),
        mock_response,
    ])
    client = AnthropicClient(max_retries=3)
    client._client.messages.create = mock
    result = client.call(...)
    assert mock.call_count == 3
```

**Sandbox timeout** — Timeout path never exercised:
```python
def test_sandbox_timeout():
    sandbox = Sandbox(timeout=1)
    result = sandbox.execute(
        code="import time; time.sleep(5)",
        context="", buffers={}, findings=[], ipc_port=0,
    )
    assert "timed out" in result.output.lower()
    assert result.terminated is False
```

**Middleware exceptions** — No test verifies propagation:
```python
def test_middleware_pre_exception_propagates():
    class Bad:
        def pre_query(self, q, c): raise ValueError("boom")
        def post_query(self, r): return r
    chain = MiddlewareChain([Bad()])
    with pytest.raises(ValueError, match="boom"):
        chain.run_pre("q", "c")
```

**IPC malformed input** — No test for bad JSON:
```python
def test_ipc_malformed_json():
    with IPCServer(lambda p, c: "ok") as server:
        sock = socket.create_connection(("127.0.0.1", server.port))
        bad = b"not json at all"
        sock.sendall(struct.pack("!I", len(bad)))
        sock.sendall(bad)
        # Should get error response, not crash the server
```

---

### 8. Missing Edge Case Tests

**Empty inputs:**
- `DocumentRegistry.load_text("id", "")` — does it work?
- `extract_repl_blocks("")` — returns `[]`? tested?
- `detect_domain("")` — returns BaseDomain?

**Threshold boundaries (domain detection):**
- Score exactly 0.3 — detected or not?
- Score 0.29 — falls back to generic?
- All domains tied — which wins?

**Large inputs:**
- 10MB context through sandbox (temp file I/O)
- 1000-line code block (indentation in wrapper)

---

### 9. Redundant Test File

`test_rlm.py` at root has 15 tests. All 15 are now duplicated in
`tests/test_engine.py`. The root file can be deleted once the v1
monolith is removed. Until then, don't add new tests to it.

---

## Quick Wins Checklist

1. [x] Fix command injection in `ingestors.py:41` (use env var)
2. [x] Add IPC message size guard in `ipc.py:63`
3. [x] Replace `except Exception: pass` with `logger.debug(...)`
4. [x] Add `tuple[str, int, int]` return type to LLMClient protocol
5. [x] Add `test_sandbox_timeout` test
6. [x] Add `test_middleware_exception_propagates` test
7. [x] Add `test_ipc_malformed_json` test
8. [ ] Add `test_client_retries_on_rate_limit` test (requires mocking anthropic SDK)
9. [x] Extract shared loop logic from run()/arun()
10. [x] Validate IPC JSON has required `prompt` field
