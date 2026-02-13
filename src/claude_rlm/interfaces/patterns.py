"""
Pre-built query patterns for common document analysis tasks.

Moved from the root-level RLMPatterns class. Each method constructs
a structured prompt and delegates to a ClaudeRLM instance's query().
"""

from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from claude_rlm import ClaudeRLM


class RLMPatterns:
    """Pre-built query patterns for common tasks."""

    @staticmethod
    def find_specific_value(
        rlm: "ClaudeRLM", value_description: str, expected_format: str = "any"
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
        rlm: "ClaudeRLM",
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
        rlm: "ClaudeRLM", pattern_description: str, output_format: str = "list"
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
        rlm: "ClaudeRLM", section_identifier: str, summary_length: str = "medium"
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
