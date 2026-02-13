"""
Query orchestrator — the unified REPL loop.

Replaces the duplicated query()/query_batch() logic in ClaudeRLM with
a single `QueryOrchestrator` that works with any LLM client implementing
the `LLMClient` protocol.
"""

from datetime import datetime
from typing import Protocol, Dict, Any, List, Optional, Callable

from ..constants import MAX_OUTPUT_CHARS
from ..engine import Sandbox, IPCServer, extract_repl_blocks
from .result_parser import parse_final_answer, build_result
from .middleware import MiddlewareChain


class LLMClient(Protocol):
    """Protocol for synchronous LLM API clients.

    Any class with a compatible `call()` method satisfies this protocol.
    This enables mocking in tests and swapping providers in the future.
    """

    def call(
        self,
        model: str,
        max_tokens: int,
        system: str,
        messages: List[Dict[str, str]],
    ) -> tuple:
        """Call the LLM and return (response_text, input_tokens, output_tokens)."""
        ...


class AsyncLLMClient(Protocol):
    """Protocol for async LLM API clients (used with arun())."""

    async def call(
        self,
        model: str,
        max_tokens: int,
        system: str,
        messages: List[Dict[str, str]],
    ) -> tuple:
        """Async call returning (response_text, input_tokens, output_tokens)."""
        ...


class QueryOrchestrator:
    """Unified REPL query loop.

    Handles the iterative process of:
    1. Send question to LLM
    2. LLM writes ```repl code
    3. Execute code in sandbox (with IPC for sub_query)
    4. Feed output back to LLM
    5. Repeat until FINAL()/FINAL_ANSWER or iteration limit

    This replaces both query() and query_batch() in ClaudeRLM.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        sub_query_fn: Callable[[str, Optional[str]], str],
        system_prompt: str,
        config_root_model: str = "claude-sonnet-4-5-20250929",
        config_root_max_tokens: int = 16384,
        config_code_timeout: int = 30,
        config_save_trajectory: bool = True,
        config_verbose: bool = False,
        middleware: Optional[MiddlewareChain] = None,
    ):
        self.llm_client = llm_client
        self.sub_query_fn = sub_query_fn
        self.system_prompt = system_prompt
        self.root_model = config_root_model
        self.root_max_tokens = config_root_max_tokens
        self.code_timeout = config_code_timeout
        self.save_trajectory = config_save_trajectory
        self.verbose = config_verbose
        self.middleware = middleware or MiddlewareChain()

    def run(
        self,
        question: str,
        context: str,
        max_iterations: int = 20,
    ) -> Dict[str, Any]:
        """Run a single query through the REPL loop.

        Args:
            question: The question to answer.
            context: The document text.
            max_iterations: Maximum REPL iterations.

        Returns:
            Result dict with answer, evidence, confidence, metadata.
        """
        # Run pre-query middleware
        question, context = self.middleware.run_pre(question, context)

        # State for this query
        buffers: Dict[str, Any] = {}
        findings: List[str] = []
        trajectory: List[Dict] = []
        root_input_tokens = 0
        root_output_tokens = 0

        system = self.system_prompt

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

            response_text, in_tok, out_tok = self.llm_client.call(
                model=self.root_model,
                max_tokens=self.root_max_tokens,
                system=system,
                messages=messages,
            )
            root_input_tokens += in_tok
            root_output_tokens += out_tok

            trajectory.append({
                "iteration": iteration + 1,
                "response": response_text,
                "timestamp": datetime.now().isoformat(),
            })

            # Text-based termination
            if "FINAL_ANSWER:" in response_text:
                result = parse_final_answer(
                    response_text,
                    root_input_tokens=root_input_tokens,
                    root_output_tokens=root_output_tokens,
                    trajectory=trajectory if self.save_trajectory else None,
                )
                return self.middleware.run_post(result)

            # Execute code blocks
            code_blocks = extract_repl_blocks(response_text)

            if code_blocks:
                code_result = self._execute_blocks(
                    code_blocks, context, buffers, findings,
                )
                if code_result["terminated"]:
                    result = build_result(
                        code_result["final_answer"],
                        source="FINAL() from code",
                        root_input_tokens=root_input_tokens,
                        root_output_tokens=root_output_tokens,
                        trajectory=trajectory if self.save_trajectory else None,
                    )
                    return self.middleware.run_post(result)

                code_output = code_result["output"]
                if code_output:
                    truncated = code_output[:MAX_OUTPUT_CHARS]
                    if len(code_output) > MAX_OUTPUT_CHARS:
                        truncated += (
                            f"\n... [OUTPUT TRUNCATED: {len(code_output):,} chars total, "
                            f"showing first {MAX_OUTPUT_CHARS:,}]"
                        )
                    messages.append({"role": "assistant", "content": response_text})
                    messages.append({
                        "role": "user",
                        "content": (
                            f"Code execution output:\n```\n{truncated}\n```\n\n"
                            "Continue your analysis. Use FINAL() or write "
                            "FINAL_ANSWER: when you have your answer."
                        ),
                    })
                else:
                    messages.append({"role": "assistant", "content": response_text})
                    messages.append({
                        "role": "user",
                        "content": (
                            "No code was executed. Write ```repl blocks to "
                            "interact with the document. You must explore the "
                            "context before providing a final answer."
                        ),
                    })
            else:
                messages.append({"role": "assistant", "content": response_text})
                messages.append({
                    "role": "user",
                    "content": (
                        "No code was executed. Write ```repl blocks to "
                        "interact with the document. You must explore the "
                        "context before providing a final answer."
                    ),
                })

        # Iteration limit fallback
        messages.append({
            "role": "user",
            "content": (
                "You've reached the iteration limit. "
                "Please provide your FINAL_ANSWER now based on what you've found."
            ),
        })
        response_text, in_tok, out_tok = self.llm_client.call(
            model=self.root_model,
            max_tokens=self.root_max_tokens,
            system=system,
            messages=messages,
        )
        root_input_tokens += in_tok
        root_output_tokens += out_tok

        result = parse_final_answer(
            response_text,
            root_input_tokens=root_input_tokens,
            root_output_tokens=root_output_tokens,
            trajectory=trajectory if self.save_trajectory else None,
        )
        return self.middleware.run_post(result)

    async def arun(
        self,
        question: str,
        context: str,
        max_iterations: int = 20,
    ) -> Dict[str, Any]:
        """Async version of run() — same REPL loop but awaits LLM calls.

        Requires an AsyncLLMClient (one with `async def call()`).
        """
        question, context = self.middleware.run_pre(question, context)

        buffers: Dict[str, Any] = {}
        findings: List[str] = []
        trajectory: List[Dict] = []
        root_input_tokens = 0
        root_output_tokens = 0

        system = self.system_prompt
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

            response_text, in_tok, out_tok = await self.llm_client.call(
                model=self.root_model,
                max_tokens=self.root_max_tokens,
                system=system,
                messages=messages,
            )
            root_input_tokens += in_tok
            root_output_tokens += out_tok

            trajectory.append({
                "iteration": iteration + 1,
                "response": response_text,
                "timestamp": datetime.now().isoformat(),
            })

            if "FINAL_ANSWER:" in response_text:
                result = parse_final_answer(
                    response_text,
                    root_input_tokens=root_input_tokens,
                    root_output_tokens=root_output_tokens,
                    trajectory=trajectory if self.save_trajectory else None,
                )
                return self.middleware.run_post(result)

            code_blocks = extract_repl_blocks(response_text)

            if code_blocks:
                code_result = self._execute_blocks(
                    code_blocks, context, buffers, findings,
                )
                if code_result["terminated"]:
                    result = build_result(
                        code_result["final_answer"],
                        source="FINAL() from code",
                        root_input_tokens=root_input_tokens,
                        root_output_tokens=root_output_tokens,
                        trajectory=trajectory if self.save_trajectory else None,
                    )
                    return self.middleware.run_post(result)

                code_output = code_result["output"]
                if code_output:
                    truncated = code_output[:MAX_OUTPUT_CHARS]
                    if len(code_output) > MAX_OUTPUT_CHARS:
                        truncated += (
                            f"\n... [OUTPUT TRUNCATED: {len(code_output):,} chars total, "
                            f"showing first {MAX_OUTPUT_CHARS:,}]"
                        )
                    messages.append({"role": "assistant", "content": response_text})
                    messages.append({
                        "role": "user",
                        "content": (
                            f"Code execution output:\n```\n{truncated}\n```\n\n"
                            "Continue your analysis. Use FINAL() or write "
                            "FINAL_ANSWER: when you have your answer."
                        ),
                    })
                else:
                    messages.append({"role": "assistant", "content": response_text})
                    messages.append({
                        "role": "user",
                        "content": (
                            "No code was executed. Write ```repl blocks to "
                            "interact with the document. You must explore the "
                            "context before providing a final answer."
                        ),
                    })
            else:
                messages.append({"role": "assistant", "content": response_text})
                messages.append({
                    "role": "user",
                    "content": (
                        "No code was executed. Write ```repl blocks to "
                        "interact with the document. You must explore the "
                        "context before providing a final answer."
                    ),
                })

        messages.append({
            "role": "user",
            "content": (
                "You've reached the iteration limit. "
                "Please provide your FINAL_ANSWER now based on what you've found."
            ),
        })
        response_text, in_tok, out_tok = await self.llm_client.call(
            model=self.root_model,
            max_tokens=self.root_max_tokens,
            system=system,
            messages=messages,
        )
        root_input_tokens += in_tok
        root_output_tokens += out_tok

        result = parse_final_answer(
            response_text,
            root_input_tokens=root_input_tokens,
            root_output_tokens=root_output_tokens,
            trajectory=trajectory if self.save_trajectory else None,
        )
        return self.middleware.run_post(result)

    def run_batch(
        self,
        questions: List[str],
        context: str,
        max_iterations: int = 20,
    ) -> List[Dict[str, Any]]:
        """Run multiple queries against the same document.

        Args:
            questions: List of questions to answer.
            context: The document text.
            max_iterations: Maximum REPL iterations per question.

        Returns:
            List of result dicts.
        """
        return [
            self.run(q, context, max_iterations)
            for q in questions
        ]

    def _execute_blocks(
        self,
        code_blocks: List[str],
        context: str,
        buffers: Dict[str, Any],
        findings: List[str],
    ) -> Dict[str, Any]:
        """Execute a list of code blocks in the sandbox.

        Returns dict with output, terminated, final_answer.
        """
        outputs = []
        with IPCServer(self.sub_query_fn) as ipc:
            sandbox = Sandbox(timeout=self.code_timeout)
            for code in code_blocks:
                result = sandbox.execute(
                    code=code,
                    context=context,
                    buffers=buffers,
                    findings=findings,
                    ipc_port=ipc.port,
                )
                if result.terminated:
                    return result.to_dict()
                if result.output:
                    outputs.append(result.output)

        return {
            "output": "\n".join(outputs) if outputs else None,
            "terminated": False,
            "final_answer": None,
        }

    def _log(self, message: str) -> None:
        if self.verbose:
            print(f"[RLM] {message}")
