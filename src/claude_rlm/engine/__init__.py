"""
Execution engine — sandbox, IPC, and code extraction.

Provides the isolated subprocess environment where LLM-generated code
runs safely, with IPC-based sub_query() routing back to the parent.
"""

from .sandbox import Sandbox, SandboxResult
from .ipc import IPCServer
from .code_extractor import extract_repl_blocks

__all__ = [
    "Sandbox",
    "SandboxResult",
    "IPCServer",
    "extract_repl_blocks",
]
