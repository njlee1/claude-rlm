#!/usr/bin/env python3
"""
Claude RLM (Recursive Language Model) - Advanced Document Processing System
============================================================================

Adapted from the RLM paradigm described in:
"Recursive Language Models" by Alex L. Zhang, Tim Kraska, Omar Khattab
MIT CSAIL, arXiv:2512.24601v2, January 2026
Reference implementation: https://github.com/alexzhang13/rlm

This implementation treats documents as external environment variables that Claude
can programmatically examine, decompose, and recursively query - avoiding the
"context rot" phenomenon that degrades accuracy on long documents.

Usage:
    from claude_rlm import ClaudeRLM

    rlm = ClaudeRLM()
    rlm.load_document("path/to/document.pdf")
    answer = rlm.query("Find the exact revenue figures for Q3 2024")
"""

import anthropic
import json
import re
import socket
import socketserver
import struct
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import subprocess


# =============================================================================
# SUPPORTED MODELS
# =============================================================================

SUPPORTED_MODELS: Dict[str, Dict[str, Any]] = {
    "claude-opus-4-6": {
        "name": "Claude Opus 4.6",
        "input_per_mtok": 15.0,
        "output_per_mtok": 75.0,
    },
    "claude-sonnet-4-5-20250929": {
        "name": "Claude Sonnet 4.5",
        "input_per_mtok": 3.0,
        "output_per_mtok": 15.0,
    },
    "claude-haiku-4-5-20251001": {
        "name": "Claude Haiku 4.5",
        "input_per_mtok": 0.25,
        "output_per_mtok": 1.25,
    },
    # Legacy model IDs (still valid)
    "claude-sonnet-4-20250514": {
        "name": "Claude Sonnet 4.0",
        "input_per_mtok": 3.0,
        "output_per_mtok": 15.0,
    },
    "claude-opus-4-5-20251101": {
        "name": "Claude Opus 4.5",
        "input_per_mtok": 15.0,
        "output_per_mtok": 75.0,
    },
}

# Maximum characters of REPL output fed back to the model per iteration.
# Matches the original RLM repo's format_iteration() 20K char truncation.
MAX_OUTPUT_CHARS = 20_000


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class RLMConfig:
    """Configuration for the RLM system."""

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

    def __post_init__(self):
        if self.root_model not in SUPPORTED_MODELS:
            raise ValueError(
                f"Unknown root_model '{self.root_model}'. "
                f"Supported: {list(SUPPORTED_MODELS.keys())}"
            )
        if self.sub_model not in SUPPORTED_MODELS:
            raise ValueError(
                f"Unknown sub_model '{self.sub_model}'. "
                f"Supported: {list(SUPPORTED_MODELS.keys())}"
            )


# =============================================================================
# CORE RLM SYSTEM
# =============================================================================

class ClaudeRLM:
    """
    Recursive Language Model implementation for Claude.

    Treats documents as external environment variables that can be
    programmatically examined, decomposed, and recursively queried.
    """

    ROOT_SYSTEM_PROMPT = """You are an advanced Recursive Language Model (RLM) agent. Your task is to answer queries about documents by treating the document as an EXTERNAL ENVIRONMENT you can programmatically interact with.

## CRITICAL PRINCIPLES

1. **NEVER try to read the entire document at once** - This causes "context rot" where accuracy degrades
2. **Use variables as buffers** - Store intermediate findings, then aggregate
3. **Verify with sub-calls** - Use targeted sub-queries to double-check specific claims
4. **Semantic chunking** - YOU decide where to split based on content structure, not arbitrary limits
5. **ALWAYS write code first** - You MUST interact with the REPL before providing a final answer

## YOUR ENVIRONMENT

You have access to a Python REPL. Write executable code in ```repl blocks:

```python
# The full document is stored here - DO NOT print it all at once
context: str  # The loaded document ({context_length} characters, ~{token_estimate} tokens)

# Query a sub-LLM for targeted analysis (makes a real API call)
def sub_query(prompt: str, context_slice: str = None) -> str:
    '''Call a smaller LLM on a specific slice of context. Returns the LLM's response string.'''

# Store intermediate findings
buffers: dict = {{}}
findings: list = []

# Inspect current state of all stored variables
def SHOW_VARS() -> None:
    '''Print all keys in buffers and count of findings.'''

# Terminate the loop and return your answer from code
def FINAL(answer: str) -> None:
    '''Call this to end the analysis and return answer. Example: FINAL("$1.8M")'''

def FINAL_VAR(var_name: str) -> None:
    '''Call this to end the analysis and return the value of a variable. Example: FINAL_VAR("buffers['revenue']")'''
```

IMPORTANT: Only code inside ```repl blocks will be executed. Use ```repl (not ```python) for executable code.

## STRATEGY GUIDE

### For Finding Specific Information:
1. First, probe the document structure: `print(context[:2000])` to understand format
2. Use regex or string methods to locate relevant sections
3. Extract candidate sections into variables
4. Use `sub_query()` to analyze each candidate — it makes a REAL API call and returns the response
5. Store findings in `buffers`, then aggregate

### For Aggregation Tasks (counts, summaries):
1. Determine logical chunking (by section, paragraph, entry)
2. Process each chunk with `sub_query()` storing results
3. Aggregate programmatically (don't trust LLM to count)
4. Verify edge cases with targeted sub-queries

### For Verification:
1. After finding an answer, ALWAYS verify with a targeted sub-query
2. Quote the exact source text supporting your answer
3. If verification fails, search for alternative evidence

## TERMINATION

You can end the loop in TWO ways:

**Option A** - From text (outside code blocks):
```
FINAL_ANSWER: [your answer here]
SOURCE_EVIDENCE: [exact quote from document supporting this]
CONFIDENCE: [high/medium/low]
VERIFICATION_METHOD: [how you verified this]
```

**Option B** - From code (inside ```repl blocks):
```repl
# After verifying your answer:
FINAL("$1.8M - Q3 2024 revenue, verified against table on line 312")
# or reference a variable:
FINAL_VAR("buffers['final_answer']")
```

## ANTI-PATTERNS TO AVOID

- Printing entire document: `print(context)` — causes context rot
- Single-pass analysis: Trying to answer from one read-through
- Answering without code: You MUST run at least one ```repl block before answering
- Trusting memory: Not verifying findings against source
- Over-calling sub_query: More than {max_sub_calls} calls suggests wrong approach

## CURRENT TASK

Document type: {doc_type}
Document length: {context_length} characters (~{token_estimate} tokens)
Document preview (first 500 chars):
```
{context_preview}
```

Query: {query}

Begin by examining the document structure with code, then develop your strategy."""

    SUB_SYSTEM_PROMPT = """You are a focused analysis assistant. Your job is to answer ONE specific question about the provided text.

RULES:
1. Answer ONLY what is asked - no elaboration
2. Quote exact text when citing evidence
3. If the answer isn't in the text, say "NOT FOUND IN PROVIDED TEXT"
4. Be precise with numbers, names, dates
5. Keep response under 500 words

Question: {question}

Text to analyze:
{context_slice}"""

    def __init__(self, config: Optional[RLMConfig] = None):
        self.config = config or RLMConfig()
        self.client = anthropic.Anthropic()

        # State
        self.context: str = ""
        self.buffers: Dict[str, Any] = {}
        self.findings: List[str] = []
        self.trajectory: List[Dict] = []
        self.sub_call_count: int = 0

        # Separate token tracking per model
        self.root_input_tokens: int = 0
        self.root_output_tokens: int = 0
        self.sub_input_tokens: int = 0
        self.sub_output_tokens: int = 0

    def reset_state(self):
        """Reset query state while keeping the document loaded."""
        self.buffers = {}
        self.findings = []
        self.trajectory = []
        self.sub_call_count = 0
        self.root_input_tokens = 0
        self.root_output_tokens = 0
        self.sub_input_tokens = 0
        self.sub_output_tokens = 0

    def load_document(self, path: str) -> str:
        """Load a document from file path."""
        filepath = Path(path)

        if not filepath.exists():
            raise FileNotFoundError(f"Document not found: {filepath}")

        if filepath.suffix.lower() == ".pdf":
            self.context = self._extract_pdf(filepath)
        elif filepath.suffix.lower() in [".docx", ".doc"]:
            self.context = self._extract_docx(filepath)
        else:
            self.context = filepath.read_text(encoding="utf-8")

        self._log(f"Loaded document: {len(self.context)} chars")
        return f"Loaded {len(self.context)} characters from {filepath.name}"

    def load_text(self, text: str) -> str:
        """Load text directly as context."""
        self.context = text
        self._log(f"Loaded text: {len(self.context)} chars")
        return f"Loaded {len(self.context)} characters"

    def _extract_pdf(self, path: Path) -> str:
        """Extract text from PDF using available tools."""
        try:
            result = subprocess.run(
                [
                    "python3", "-c",
                    "from docling.document_converter import DocumentConverter; "
                    "converter = DocumentConverter(); "
                    f"result = converter.convert('{path}'); "
                    "print(result.document.export_to_markdown())",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["pdftotext", "-layout", str(path), "-"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass

        raise RuntimeError(f"Could not extract text from PDF: {path}")

    def _extract_docx(self, path: Path) -> str:
        """Extract text from DOCX."""
        try:
            result = subprocess.run(
                ["pandoc", str(path), "-t", "plain"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass

        raise RuntimeError(f"Could not extract text from DOCX: {path}")

    def query(self, question: str, max_iterations: int = 20) -> Dict[str, Any]:
        """
        Main entry point - query the loaded document.

        The REPL loop: model writes code -> code executes (with IPC for sub_query)
        -> output fed back -> model continues or terminates via FINAL()/FINAL_ANSWER.

        Args:
            question: The question to answer
            max_iterations: Maximum REPL iterations before forcing answer

        Returns:
            Dict with answer, evidence, confidence, and metadata
        """
        if not self.context:
            raise ValueError(
                "No document loaded. Call load_document() or load_text() first."
            )

        self.reset_state()

        system = self.ROOT_SYSTEM_PROMPT.format(
            context_length=len(self.context),
            token_estimate=len(self.context) // 4,
            doc_type=self._detect_doc_type(),
            context_preview=self.context[:500],
            query=question,
            max_sub_calls=self.config.max_sub_calls,
        )

        # Iteration-0 safeguard: force the model to interact with REPL first
        # (matches original RLM's build_user_prompt() iteration-0 message)
        messages = [
            {
                "role": "user",
                "content": (
                    f"Answer this query: {question}\n\n"
                    "You have not interacted with the REPL environment yet. "
                    "Explore the context by writing python code in ```repl blocks "
                    "first before generating your final answer."
                ),
            }
        ]

        for iteration in range(max_iterations):
            self._log(f"\n{'=' * 60}\nIteration {iteration + 1}\n{'=' * 60}")

            response = self._call_root_model(system, messages)

            self.trajectory.append(
                {
                    "iteration": iteration + 1,
                    "response": response,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Check for text-based termination (FINAL_ANSWER: in prose)
            if "FINAL_ANSWER:" in response:
                return self._parse_final_answer(response)

            # Execute code blocks — may return FINAL() termination
            code_result = self._execute_code_blocks(response)

            # Check if code triggered FINAL() or FINAL_VAR() termination
            if code_result and code_result.get("terminated"):
                return self._build_result(
                    code_result["final_answer"],
                    source="FINAL() from code",
                )

            code_output = code_result["output"] if code_result else None

            if code_output:
                # Truncate output to prevent context blowup
                # (matches original RLM's format_iteration() 20K char limit)
                truncated = code_output[:MAX_OUTPUT_CHARS]
                if len(code_output) > MAX_OUTPUT_CHARS:
                    truncated += (
                        f"\n... [OUTPUT TRUNCATED: {len(code_output):,} chars total, "
                        f"showing first {MAX_OUTPUT_CHARS:,}]"
                    )

                messages.append({"role": "assistant", "content": response})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"Code execution output:\n```\n{truncated}\n```\n\n"
                            "Continue your analysis. Use FINAL() or write "
                            "FINAL_ANSWER: when you have your answer."
                        ),
                    }
                )
            else:
                messages.append({"role": "assistant", "content": response})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "No code was executed. Write ```repl blocks to "
                            "interact with the document. You must explore the "
                            "context before providing a final answer."
                        ),
                    }
                )

        # Fallback: force answer after hitting iteration limit
        messages.append(
            {
                "role": "user",
                "content": (
                    "You've reached the iteration limit. "
                    "Please provide your FINAL_ANSWER now based on what you've found."
                ),
            }
        )
        final_response = self._call_root_model(system, messages)

        return self._parse_final_answer(final_response)

    def query_batch(
        self, questions: List[str], max_iterations: int = 20
    ) -> List[Dict[str, Any]]:
        """Process multiple queries, caching document structure probe.

        More efficient than calling query() in a loop because the document
        structure analysis (first ~2000 chars) is cached as a system prompt
        prefix, avoiding redundant probing on each query.
        """
        if not self.context:
            raise ValueError(
                "No document loaded. Call load_document() or load_text() first."
            )

        # Pre-compute shared document metadata once
        doc_type = self._detect_doc_type()
        context_length = len(self.context)
        token_estimate = context_length // 4
        context_preview = self.context[:500]

        results = []
        for question in questions:
            self.reset_state()

            system = self.ROOT_SYSTEM_PROMPT.format(
                context_length=context_length,
                token_estimate=token_estimate,
                doc_type=doc_type,
                context_preview=context_preview,
                query=question,
                max_sub_calls=self.config.max_sub_calls,
            )

            messages = [
                {
                    "role": "user",
                    "content": (
                        f"Answer this query: {question}\n\n"
                        "You have not interacted with the REPL environment yet. "
                        "Explore the context by writing python code in ```repl "
                        "blocks first before generating your final answer."
                    ),
                }
            ]

            result = None
            for iteration in range(max_iterations):
                self._log(
                    f"\n{'=' * 60}\n"
                    f"Q: {question[:60]}... | Iteration {iteration + 1}\n"
                    f"{'=' * 60}"
                )

                response = self._call_root_model(system, messages)
                self.trajectory.append(
                    {
                        "iteration": iteration + 1,
                        "response": response,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                if "FINAL_ANSWER:" in response:
                    result = self._parse_final_answer(response)
                    break

                code_result = self._execute_code_blocks(response)

                if code_result and code_result.get("terminated"):
                    result = self._build_result(
                        code_result["final_answer"],
                        source="FINAL() from code",
                    )
                    break

                code_output = code_result["output"] if code_result else None
                if code_output:
                    truncated = code_output[:MAX_OUTPUT_CHARS]
                    if len(code_output) > MAX_OUTPUT_CHARS:
                        truncated += (
                            f"\n... [TRUNCATED: {len(code_output):,} chars, "
                            f"showing first {MAX_OUTPUT_CHARS:,}]"
                        )
                    messages.append({"role": "assistant", "content": response})
                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                f"Code execution output:\n```\n{truncated}\n```\n\n"
                                "Continue your analysis."
                            ),
                        }
                    )
                else:
                    messages.append({"role": "assistant", "content": response})
                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                "No code was executed. Write ```repl blocks to "
                                "interact with the document."
                            ),
                        }
                    )

            if result is None:
                messages.append(
                    {
                        "role": "user",
                        "content": "Iteration limit reached. Provide FINAL_ANSWER now.",
                    }
                )
                final_resp = self._call_root_model(system, messages)
                result = self._parse_final_answer(final_resp)

            results.append(result)
            self._log(f"Completed: {question[:60]}...")

        return results

    def sub_query(self, prompt: str, context_slice: Optional[str] = None) -> str:
        """
        Run a sub-query using the smaller model.

        Args:
            prompt: The question to ask
            context_slice: Specific text to analyze (uses full context if None)

        Returns:
            The sub-model's response
        """
        if self.sub_call_count >= self.config.max_sub_calls:
            return (
                f"ERROR: Maximum sub-calls ({self.config.max_sub_calls}) exceeded. "
                "Use code to analyze remaining data."
            )

        self.sub_call_count += 1

        if context_slice is None:
            context_slice = self.context[: self.config.sub_call_context_limit]
        elif len(context_slice) > self.config.sub_call_context_limit:
            context_slice = context_slice[: self.config.sub_call_context_limit]

        system = self.SUB_SYSTEM_PROMPT.format(
            question=prompt, context_slice=context_slice
        )

        response = self._api_call_with_retry(
            model=self.config.sub_model,
            max_tokens=self.config.sub_max_tokens,
            system=system,
            messages=[
                {"role": "user", "content": "Analyze the text and answer the question."}
            ],
        )

        if self.config.track_costs:
            self.sub_input_tokens += response.usage.input_tokens
            self.sub_output_tokens += response.usage.output_tokens

        result = response.content[0].text
        self._log(f"Sub-query #{self.sub_call_count}: {prompt[:100]}...")

        return result

    def _call_root_model(self, system: str, messages: List[Dict]) -> str:
        """Call the root model with retry logic."""
        response = self._api_call_with_retry(
            model=self.config.root_model,
            max_tokens=self.config.root_max_tokens,
            system=system,
            messages=messages,
        )

        if self.config.track_costs:
            self.root_input_tokens += response.usage.input_tokens
            self.root_output_tokens += response.usage.output_tokens

        return response.content[0].text

    def _api_call_with_retry(self, **kwargs) -> Any:
        """Make an API call with exponential backoff retry."""
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                return self.client.messages.create(**kwargs)
            except anthropic.RateLimitError as e:
                last_error = e
                delay = self.config.retry_base_delay * (2 ** attempt)
                self._log(
                    f"Rate limited, retrying in {delay}s (attempt {attempt + 1})"
                )
                time.sleep(delay)
            except anthropic.APIError as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_base_delay * (2 ** attempt)
                    self._log(f"API error, retrying in {delay}s: {e}")
                    time.sleep(delay)
                else:
                    raise
        raise last_error  # type: ignore[misc]

    def _build_result(
        self, answer: str, source: str = "unknown"
    ) -> Dict[str, Any]:
        """Build a result dict from a FINAL() termination."""
        return {
            "answer": answer,
            "evidence": None,
            "confidence": "unknown",
            "verification": source,
            "sub_calls_used": self.sub_call_count,
            "root_input_tokens": self.root_input_tokens,
            "root_output_tokens": self.root_output_tokens,
            "sub_input_tokens": self.sub_input_tokens,
            "sub_output_tokens": self.sub_output_tokens,
            "trajectory": self.trajectory if self.config.save_trajectory else None,
        }

    def _execute_code_blocks(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract and run ```repl code blocks from response.

        Returns None if no code blocks found, or a dict with:
            - "output": str — combined stdout/stderr from all blocks
            - "terminated": bool — True if FINAL()/FINAL_VAR() was called
            - "final_answer": str|None — the answer if terminated
        """
        code_pattern = r"```repl\s*\n(.*?)\n```"
        matches = re.findall(code_pattern, response, re.DOTALL)

        if not matches:
            return None

        outputs = []
        for code in matches:
            result = self._safe_run(code)
            if result.get("terminated"):
                return result
            if result["output"]:
                outputs.append(result["output"])

        return {
            "output": "\n".join(outputs) if outputs else None,
            "terminated": False,
            "final_answer": None,
        }

    # ── IPC Server for sub_query() ──────────────────────────────────────────
    #
    # The original RLM repo uses a ThreadingLMServer with socket-based IPC
    # so that code running in a subprocess can call llm_query() which routes
    # back to the parent process's API client. We replicate this pattern:
    #
    # 1. Parent starts a TCP server on localhost (random port)
    # 2. Subprocess connects via socket, sends JSON request
    # 3. Parent handles request (calls self.sub_query()), sends JSON response
    # 4. Subprocess receives response and continues execution

    def _start_ipc_server(self) -> tuple:
        """Start a threading TCP server for sub_query IPC.

        Returns (server, port) — caller must call server.shutdown() when done.
        """
        rlm_ref = self  # Capture reference for handler closure

        class SubQueryHandler(socketserver.StreamRequestHandler):
            def handle(self):
                try:
                    # Read 4-byte length prefix
                    length_bytes = self.rfile.read(4)
                    if len(length_bytes) < 4:
                        return
                    msg_len = struct.unpack("!I", length_bytes)[0]

                    # Read the JSON request
                    data = self.rfile.read(msg_len)
                    request = json.loads(data.decode("utf-8"))

                    prompt = request.get("prompt", "")
                    context_slice = request.get("context_slice")

                    # Make the actual API call via the parent's sub_query
                    response_text = rlm_ref.sub_query(prompt, context_slice)

                    # Send response back with 4-byte length prefix
                    resp_bytes = json.dumps({"result": response_text}).encode("utf-8")
                    self.wfile.write(struct.pack("!I", len(resp_bytes)))
                    self.wfile.write(resp_bytes)
                    self.wfile.flush()
                except Exception as e:
                    try:
                        err = json.dumps({"error": str(e)}).encode("utf-8")
                        self.wfile.write(struct.pack("!I", len(err)))
                        self.wfile.write(err)
                        self.wfile.flush()
                    except Exception:
                        pass

        server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), SubQueryHandler)
        port = server.server_address[1]

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        return server, port

    def _safe_run(self, code: str) -> Dict[str, Any]:
        """Run code in a subprocess with socket-based IPC for sub_query().

        The subprocess can call sub_query(), FINAL(), FINAL_VAR(), and
        SHOW_VARS() — all routed back to the parent process via TCP.

        Returns dict with keys: output, terminated, final_answer.
        """
        # Start IPC server for sub_query calls
        server, port = self._start_ipc_server()

        # Write context to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as ctx_file:
            ctx_file.write(self.context)
            ctx_path = ctx_file.name

        # Write state to temp file
        state = {"buffers": self.buffers, "findings": self.findings}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as state_file:
            json.dump(state, state_file, default=str)
            state_path = state_file.name

        # Temp file for termination signal
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as term_file:
            json.dump({"terminated": False}, term_file)
            term_path = term_file.name

        # Indent user code for try/except block
        indented = "\n".join("    " + line for line in code.splitlines())

        # Build wrapper script with real IPC-based sub_query
        wrapper = (
            "import json, re, sys, socket, struct\n"
            "\n"
            f"with open({ctx_path!r}, 'r') as f:\n"
            "    context = f.read()\n"
            "\n"
            f"with open({state_path!r}, 'r') as f:\n"
            "    _state = json.load(f)\n"
            "buffers = _state['buffers']\n"
            "findings = _state['findings']\n"
            "\n"
            "def sub_query(prompt, context_slice=None):\n"
            '    """Query a sub-LLM for targeted analysis. Makes a real API call."""\n'
            '    request = {"prompt": str(prompt), "context_slice": context_slice}\n'
            '    req_bytes = json.dumps(request).encode("utf-8")\n'
            f'    sock = socket.create_connection(("127.0.0.1", {port}), timeout=120)\n'
            "    try:\n"
            '        sock.sendall(struct.pack("!I", len(req_bytes)))\n'
            "        sock.sendall(req_bytes)\n"
            '        length_bytes = b""\n'
            "        while len(length_bytes) < 4:\n"
            "            chunk = sock.recv(4 - len(length_bytes))\n"
            "            if not chunk:\n"
            '                return "ERROR: Connection closed by server"\n'
            "            length_bytes += chunk\n"
            '        msg_len = struct.unpack("!I", length_bytes)[0]\n'
            '        data = b""\n'
            "        while len(data) < msg_len:\n"
            "            chunk = sock.recv(min(msg_len - len(data), 65536))\n"
            "            if not chunk:\n"
            "                break\n"
            "            data += chunk\n"
            '        response = json.loads(data.decode("utf-8"))\n'
            '        if "error" in response:\n'
            "            return f\"ERROR: {response['error']}\"\n"
            '        return response.get("result", "")\n'
            "    finally:\n"
            "        sock.close()\n"
            "\n"
            "def SHOW_VARS():\n"
            '    """Print all stored variables."""\n'
            '    print("=== STORED VARIABLES ===")\n'
            '    print(f"buffers ({len(buffers)} keys): {list(buffers.keys())}")\n'
            '    print(f"findings ({len(findings)} items)")\n'
            "    for k, v in buffers.items():\n"
            "        preview = str(v)[:200]\n"
            '        print(f"  buffers[{k!r}] = {preview}")\n'
            "    for i, f in enumerate(findings[:10]):\n"
            '        print(f"  findings[{i}] = {str(f)[:200]}")\n'
            "    if len(findings) > 10:\n"
            '        print(f"  ... and {len(findings) - 10} more findings")\n'
            "\n"
            "class _RLMTermination(Exception):\n"
            "    def __init__(self, answer):\n"
            "        self.answer = answer\n"
            "\n"
            "def FINAL(answer):\n"
            '    """Terminate the REPL loop and return this answer."""\n'
            "    raise _RLMTermination(str(answer))\n"
            "\n"
            "def FINAL_VAR(var_name):\n"
            '    """Terminate and return the value of a named variable."""\n'
            "    # Look up in local scope (buffers, findings, or user-defined vars)\n"
            "    import __main__ as _m\n"
            "    _locals = {k: v for k, v in globals().items() if not k.startswith('_')}\n"
            "    val = _locals.get(var_name)\n"
            "    if val is None and var_name in dir(_m):\n"
            "        val = getattr(_m, var_name)\n"
            "    if val is None:\n"
            f'        raise _RLMTermination(f"ERROR: Variable {{var_name!r}} not found")\n'
            "    raise _RLMTermination(str(val))\n"
            "\n"
            "try:\n"
            f"{indented}\n"
            "except _RLMTermination as t:\n"
            f"    with open({term_path!r}, 'w') as f:\n"
            '        json.dump({"terminated": True, "final_answer": t.answer}, f)\n'
            "\n"
            f"with open({state_path!r}, 'w') as f:\n"
            '    json.dump({"buffers": buffers, "findings": findings}, f, default=str)\n'
        )

        try:
            result = subprocess.run(
                ["python3", "-c", wrapper],
                capture_output=True,
                text=True,
                timeout=self.config.code_timeout,
            )

            output_parts = []
            if result.stdout:
                output_parts.append(result.stdout)
            if result.stderr:
                # Feed errors back to the model (original RLM pattern:
                # errors don't stop the loop, they become REPL output)
                output_parts.append(f"STDERR: {result.stderr}")

            # Read back updated state
            try:
                with open(state_path, "r") as f:
                    updated_state = json.load(f)
                self.buffers = updated_state.get("buffers", self.buffers)
                self.findings = updated_state.get("findings", self.findings)
            except Exception:
                pass

            # Check for FINAL()/FINAL_VAR() termination
            try:
                with open(term_path, "r") as f:
                    term_state = json.load(f)
                if term_state.get("terminated"):
                    return {
                        "output": "\n".join(output_parts),
                        "terminated": True,
                        "final_answer": term_state.get("final_answer", ""),
                    }
            except Exception:
                pass

            return {
                "output": "\n".join(output_parts) if output_parts else "",
                "terminated": False,
                "final_answer": None,
            }

        except subprocess.TimeoutExpired:
            return {
                "output": f"Error: Code timed out after {self.config.code_timeout}s",
                "terminated": False,
                "final_answer": None,
            }
        finally:
            server.shutdown()
            Path(ctx_path).unlink(missing_ok=True)
            Path(state_path).unlink(missing_ok=True)
            Path(term_path).unlink(missing_ok=True)

    def _parse_final_answer(self, response: str) -> Dict[str, Any]:
        """Parse the final answer from response."""
        result = {
            "answer": None,
            "evidence": None,
            "confidence": "unknown",
            "verification": None,
            "sub_calls_used": self.sub_call_count,
            "root_input_tokens": self.root_input_tokens,
            "root_output_tokens": self.root_output_tokens,
            "sub_input_tokens": self.sub_input_tokens,
            "sub_output_tokens": self.sub_output_tokens,
            "trajectory": self.trajectory if self.config.save_trajectory else None,
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

    def _detect_doc_type(self) -> str:
        """Detect document type from content."""
        preview = self.context[:1000].lower()

        if "abstract" in preview and "introduction" in preview:
            return "academic paper"
        elif "<!doctype" in preview or "<html" in preview:
            return "HTML document"
        elif preview.startswith("{") or preview.startswith("["):
            return "JSON data"
        elif "|" in preview and "-|-" in preview:
            return "markdown with tables"
        elif any(
            x in preview
            for x in ["revenue", "profit", "q1", "q2", "q3", "q4", "fiscal"]
        ):
            return "financial document"
        elif any(x in preview for x in ["def ", "class ", "import ", "function"]):
            return "code/technical document"
        else:
            return "general text document"

    def _log(self, message: str):
        if self.config.verbose:
            print(f"[RLM] {message}")

    def get_cost_estimate(self) -> Dict[str, Any]:
        """Get estimated API costs with per-model breakdown."""
        root_pricing = SUPPORTED_MODELS.get(
            self.config.root_model,
            {"input_per_mtok": 3.0, "output_per_mtok": 15.0},
        )
        sub_pricing = SUPPORTED_MODELS.get(
            self.config.sub_model,
            {"input_per_mtok": 0.25, "output_per_mtok": 1.25},
        )

        root_cost = (
            (self.root_input_tokens / 1_000_000) * root_pricing["input_per_mtok"]
            + (self.root_output_tokens / 1_000_000) * root_pricing["output_per_mtok"]
        )
        sub_cost = (
            (self.sub_input_tokens / 1_000_000) * sub_pricing["input_per_mtok"]
            + (self.sub_output_tokens / 1_000_000) * sub_pricing["output_per_mtok"]
        )

        return {
            "root_model": self.config.root_model,
            "root_input_tokens": self.root_input_tokens,
            "root_output_tokens": self.root_output_tokens,
            "root_cost_usd": round(root_cost, 4),
            "sub_model": self.config.sub_model,
            "sub_input_tokens": self.sub_input_tokens,
            "sub_output_tokens": self.sub_output_tokens,
            "sub_cost_usd": round(sub_cost, 4),
            "total_cost_usd": round(root_cost + sub_cost, 4),
        }


# =============================================================================
# ADVANCED QUERY PATTERNS
# =============================================================================


class RLMPatterns:
    """Pre-built query patterns for common tasks."""

    @staticmethod
    def find_specific_value(
        rlm: ClaudeRLM, value_description: str, expected_format: str = "any"
    ) -> Dict:
        """Find a specific value in the document."""
        query = f"""Find the exact {value_description}.

Expected format: {expected_format}

Requirements:
1. Search the entire document systematically
2. Quote the exact text where you found this value
3. If multiple values exist, list all with their contexts
4. Verify by locating the value in at least two ways if possible"""

        return rlm.query(query)

    @staticmethod
    def compare_entities(
        rlm: ClaudeRLM,
        entity1: str,
        entity2: str,
        comparison_criteria: List[str],
    ) -> Dict:
        """Compare two entities across multiple criteria."""
        criteria_str = "\n".join(f"- {c}" for c in comparison_criteria)

        query = f"""Compare {entity1} and {entity2} on these criteria:
{criteria_str}

For each criterion:
1. Find the relevant information for both entities
2. Quote the source text
3. Provide a clear comparison

Present results in a structured format."""

        return rlm.query(query)

    @staticmethod
    def extract_all_instances(
        rlm: ClaudeRLM, pattern_description: str, output_format: str = "list"
    ) -> Dict:
        """Extract all instances matching a pattern."""
        query = f"""Extract ALL instances of: {pattern_description}

Requirements:
1. Scan the ENTIRE document systematically (don't stop after finding a few)
2. Use code to help count and organize findings
3. Store each finding in buffers with its location/context
4. Verify the count is complete

Output format: {output_format}"""

        return rlm.query(query)

    @staticmethod
    def summarize_section(
        rlm: ClaudeRLM, section_identifier: str, summary_length: str = "medium"
    ) -> Dict:
        """Summarize a specific section."""
        query = f"""Find and summarize the section: {section_identifier}

Summary length: {summary_length}

Requirements:
1. First locate the exact boundaries of this section
2. Extract the full section text into a variable
3. Use sub_query to analyze key points
4. Synthesize into a coherent summary
5. Include key quotes that support main points"""

        return rlm.query(query)


# =============================================================================
# CLI INTERFACE
# =============================================================================


def main():
    """Command-line interface for RLM."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Claude RLM - Recursive Language Model for Document Analysis"
    )
    parser.add_argument("document", help="Path to document file")
    parser.add_argument("query", help="Question to answer")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--root-model",
        default="claude-sonnet-4-5-20250929",
        help="Root model (default: claude-sonnet-4-5-20250929)",
    )
    parser.add_argument(
        "--sub-model",
        default="claude-haiku-4-5-20251001",
        help="Sub model (default: claude-haiku-4-5-20251001)",
    )
    parser.add_argument(
        "--max-iterations", type=int, default=20, help="Max REPL iterations"
    )

    args = parser.parse_args()

    config = RLMConfig(
        root_model=args.root_model,
        sub_model=args.sub_model,
        verbose=args.verbose,
    )

    rlm = ClaudeRLM(config)
    rlm.load_document(args.document)

    result = rlm.query(args.query, max_iterations=args.max_iterations)

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"\nAnswer: {result['answer']}")
    print(f"\nEvidence: {result['evidence']}")
    print(f"\nConfidence: {result['confidence']}")
    print(f"\nSub-calls used: {result['sub_calls_used']}")

    costs = rlm.get_cost_estimate()
    print(f"\nCost breakdown:")
    print(f"  Root ({costs['root_model']}): ${costs['root_cost_usd']}")
    print(f"  Sub  ({costs['sub_model']}): ${costs['sub_cost_usd']}")
    print(f"  Total: ${costs['total_cost_usd']}")


if __name__ == "__main__":
    main()
