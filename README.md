# Claude RLM — Recursive Language Model for Document Analysis

Adapted from the original RLM repository ([github.com/alexzhang13/rlm](https://github.com/alexzhang13/rlm)) and research paper ["Recursive Language Models" (arXiv:2512.24601v2)](https://arxiv.org/abs/2512.24601v2). The original repository was used as a reference when adapting and transforming the RLM paradigm specifically for Claude.

## The Problem

When you feed large documents directly to an LLM, you experience **"context rot"** — accuracy degrades significantly as document size grows. The RLM paper showed that treating documents as external environments to query programmatically (rather than dumping into context) improves accuracy dramatically on long-document tasks.

## Multi-Domain Support

Claude RLM ships with **7 professional domains**, each with deep sub-sector coverage:

| Domain | Synonym Groups | Terms | Sub-sectors |
|--------|:-:|:-:|---|
| **Finance** | 10 | 83 | SEC/10-K, annual reports, financial statements |
| **Legal** | 14 | 258 | Contracts, litigation, IP, corporate governance, employment, regulatory |
| **Medical** | 13 | 295 | Clinical, pharma, clinical trials, devices, billing, public health |
| **Academic** | 11 | 223 | STEM, social sciences, grants, systematic reviews, theses |
| **Insurance** | 15 | 306 | P&C, auto, workers comp, professional, health, life, reinsurance |
| **Real Estate** | 18 | 328 | Leasing, purchase/sale, construction, REIT, appraisal, title, environmental |
| **Compliance** | 17 | 366 | SOX, GDPR, HIPAA, PCI DSS, AML/KYC, ESG, third-party risk |
| **Total** | **98** | **1,859** | |

Domains are auto-detected from document content and filename. Each domain includes synonym groups (so "revenue" also finds "net sales", "total net revenue", etc.), detection patterns, and pre-built query templates.

## Three Usage Modes

### Mode A: Claude Code Agent (Recommended)

Copy the project files and use Claude Code's built-in tools for document analysis:

```bash
# Copy to your project
cp CLAUDE.md /path/to/your/project/
cp -r .claude /path/to/your/project/
```

Then in Claude Code:
```
> Analyze report.pdf and find the Q3 2024 revenue
> Count all liability clauses in contract.md
> Extract all findings from this SOX audit report
> What coverage exclusions apply in this policy?
```

Claude Code follows the PROBE → LOCATE → EXTRACT → ANALYZE → VERIFY → RESPOND workflow automatically, with domain-specific synonym expansion.

### Mode B: Programmatic API

Use `claude_rlm.py` to build applications that call Claude's API with RLM methodology:

```bash
pip install anthropic

# CLI usage
python claude_rlm.py document.pdf "What is the revenue?"

# With options
python claude_rlm.py document.pdf "Question" \
    --verbose \
    --root-model claude-opus-4-6 \
    --max-iterations 30
```

```python
from claude_rlm import ClaudeRLM

rlm = ClaudeRLM()
rlm.load_document("report.pdf")
result = rlm.query("What was Q3 2024 revenue?")

print(result['answer'])       # The answer
print(result['evidence'])     # Source quote
print(result['confidence'])   # high/medium/low
```

### Mode C: Any LLM (Standalone Prompt)

Copy `STANDALONE_PROMPT.md` as a system prompt into any LLM chat interface (Claude.ai, ChatGPT, etc.). This provides a **reasoning heuristic** — a mental framework for structured document analysis without tools or REPL.

## Domain Plugin Architecture

Each domain is a Python class with:
- **Synonyms**: Term → all equivalent terms (e.g., "revenue" → "net sales", "total net revenue", ...)
- **Detection patterns**: Regex patterns that identify the document type
- **Query templates**: Pre-built extraction queries for common tasks
- **Filename keywords**: Filename patterns for auto-detection

### Adding a Custom Domain

```python
from domains.base import BaseDomain

class TaxDomain(BaseDomain):
    name = "tax"
    description = "Tax document analysis"

    synonyms = {
        "income": ["taxable income", "adjusted gross income", "AGI", ...],
        "deduction": ["deduction", "write-off", "tax credit", ...],
    }

    document_patterns = [r"FORM\s+1040", r"SCHEDULE\s+[A-Z]", ...]
    query_templates = {
        "income": "What taxable income is reported? Look for: {synonyms}.",
    }
```

Register it in `domains/__init__.py`:
```python
from .tax import TaxDomain
DOMAIN_REGISTRY["tax"] = TaxDomain
```

## Quick Start: Domain Detection Demo

```bash
python demo.py 10-K.pdf                    # Auto-detect → finance
python demo.py contract.pdf --domain=legal # Force domain
python demo.py paper.pdf methodology       # Specific topic
python demo.py                             # Show all domains and topics
```

## How It Works

### Traditional Approach
```
Document → Dump into context → LLM reads all at once → Context rot → Wrong answers
```

### RLM Approach
```
Document → Store externally → Probe structure → Target specific sections →
Verify findings → Buffer aggregation → Verified answer
```

### Key Techniques

1. **Targeted reading**: Only examine sections relevant to the query
2. **Synonym expansion**: Domain-specific vocabulary resolution (1,859 terms across 7 domains)
3. **Sub-queries**: Smaller model handles focused verification tasks
4. **Buffer aggregation**: Findings accumulate incrementally
5. **Verification loops**: Always cross-check against source text

## Configuration (Mode B)

```python
from claude_rlm import ClaudeRLM, RLMConfig

# High accuracy
config = RLMConfig(
    root_model="claude-opus-4-6",
    sub_model="claude-sonnet-4-5-20250929",
    max_sub_calls=100,
    verbose=True
)

# Cost optimized (default)
config = RLMConfig(
    root_model="claude-sonnet-4-5-20250929",
    sub_model="claude-haiku-4-5-20251001",
    max_sub_calls=20
)

rlm = ClaudeRLM(config)
```

## Combining with IBM Docling

For complex PDFs, use Docling for extraction + RLM for analysis:

```python
from docling.document_converter import DocumentConverter
from claude_rlm import ClaudeRLM

converter = DocumentConverter()
doc = converter.convert("complex.pdf")
clean_text = doc.document.export_to_markdown()

rlm = ClaudeRLM()
rlm.load_text(clean_text)
result = rlm.query("Your question here")
```

## When to Use RLM

**Use RLM for:**
- Documents > 50K characters
- Information-dense tasks (counting, aggregation)
- Multi-hop reasoning across document sections
- High-accuracy requirements
- Domain-specific vocabulary (finance, legal, medical, etc.)

**Skip RLM for:**
- Short documents (< 10K chars)
- Simple questions with obvious answers
- Speed-critical applications

## Project Structure

```
claude_rlm.py              # Core Python API (Mode B)
agent_sdk_bridge.py        # Platform deployment adapter
domains/                   # Domain plugin package
  __init__.py              # Registry and auto-detection
  base.py                  # Abstract base domain class
  finance.py               # 10 synonym groups, 83 terms
  legal.py                 # 14 synonym groups, 258 terms
  medical.py               # 13 synonym groups, 295 terms
  academic.py              # 11 synonym groups, 223 terms
  insurance.py             # 15 synonym groups, 306 terms
  real_estate.py           # 18 synonym groups, 328 terms
  compliance.py            # 17 synonym groups, 366 terms
demo.py                    # Domain detection demo
test_rlm.py                # Core engine tests (15/15)
examples.py                # Usage examples
CLAUDE.md                  # Claude Code directives (Mode A)
STANDALONE_PROMPT.md       # Copy-paste prompt (Mode C)
pyproject.toml             # Package configuration
```

## Cost Estimates (Mode B)

| Document Size | Typical Cost |
|--------------|--------------|
| 50K chars | $0.02 - $0.10 |
| 500K chars | $0.10 - $0.50 |
| 5M chars | $0.50 - $2.00 |

## Supported Models

| Model | Recommended Role | Cost |
|-------|-----------------|------|
| claude-opus-4-6 | Root (highest accuracy) | $$$ |
| claude-sonnet-4-5-20250929 | Root (default) | $$ |
| claude-haiku-4-5-20251001 | Sub (verification) | $ |

## Citation

Adapted from:
```bibtex
@article{zhang2024rlm,
  title={Recursive Language Models},
  author={Zhang, Alex L. and Kraska, Tim and Khattab, Omar},
  journal={arXiv preprint arXiv:2512.24601},
  year={2024}
}
```

## License

MIT License. Copyright (c) 2026 Na Jung. See [LICENSE](LICENSE) for details.
