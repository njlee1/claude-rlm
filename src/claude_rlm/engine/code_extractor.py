"""
Code block extraction from LLM responses.

Extracts ```repl fenced code blocks from model output.
Only ```repl blocks are executed — ```python blocks are treated as
illustrative and ignored (this is a deliberate safety boundary).
"""

import re
from typing import List


def extract_repl_blocks(response: str) -> List[str]:
    """Extract ```repl code blocks from an LLM response.

    Args:
        response: Raw text from the LLM.

    Returns:
        List of code strings (may be empty if no ```repl blocks found).
    """
    code_pattern = r"```repl\s*\n(.*?)\n```"
    return re.findall(code_pattern, response, re.DOTALL)
