# RLM (Recursive Language Model) for Document Analysis

You use the RLM paradigm for document analysis. Based on arXiv:2512.24601v1.

## Core Rules

1. **NEVER read entire large documents (>50KB) into your context in one pass.** This causes "context rot" where accuracy drops from ~95% to ~50%. Treat documents as external data to query with tools.
2. **ALWAYS examine the document with tools before answering.** You must run at least one Read or Grep command on the document before providing any answer. Never answer from the query alone.

## Tool Mapping

| Task | Tool | Example |
|------|------|---------|
| Probe document structure | `Read` with `limit: 50` | Read first/last 50 lines |
| Search for keywords/patterns | `Grep` with regex | Find all occurrences of "revenue" |
| Extract specific sections | `Read` with `offset` + `limit` | Read lines 200-250 |
| Focused sub-analysis | `Task` (subagent, model: haiku) | "Extract the revenue figure from this text: ..." |
| Counting / aggregation | `Bash` with python3 | `python3 -c "..."` for programmatic counting |
| Store intermediate findings | Keep in conversation context | Summarize findings between tool calls |
| Cross-check findings | `Task` (subagent, model: haiku) | "Verify that Q3 revenue is $1.8M given: ..." |

## Mandatory Workflow for Document Queries

1. **PROBE** -- Read first 50 lines + last 20 lines to understand structure and format
2. **LOCATE** -- Use Grep to find relevant sections by keyword/pattern
3. **EXTRACT** -- Read targeted line ranges around matches (use offset/limit)
4. **ANALYZE** -- For complex extraction, delegate to a Task subagent with the specific text snippet
5. **VERIFY** -- Cross-check findings with a second Grep or Task subagent against source
6. **RESPOND** -- Output structured answer

## Anti-Patterns

- NEVER read a file >50KB without using offset/limit to target specific sections
- NEVER answer document questions without first using Read or Grep on the document
- NEVER answer document questions from memory alone -- always verify against source text
- NEVER trust yourself to count items -- use `Bash` with `python3 -c "len(...)"` or `wc -l`
- NEVER make 50+ sub-agent calls -- refine your Grep patterns instead
- NEVER give up on a tool error -- if Grep or Read fails, adjust the pattern or offset and retry

## Output Format for Document Analysis

```
FINAL_ANSWER: [precise answer]
SOURCE_EVIDENCE: [exact quote from the document]
CONFIDENCE: [high/medium/low]
VERIFICATION_METHOD: [which tools verified this]
```

## Detailed Strategies

See `.claude/skills/rlm-analysis.md` for task-specific patterns (finding values, comparisons, multi-hop questions, table extraction).
