"""
Finance domain plugin for RLM document analysis.

Covers SEC filings, annual reports, and financial statements.
Demonstrates the domain plugin pattern — extend with your own
sub-sector synonym groups as needed.
"""

from .base import BaseDomain


class FinanceDomain(BaseDomain):
    """Finance domain: SEC filings, financial statements."""

    name = "finance"
    description = (
        "Financial document analysis (SEC filings, annual reports, "
        "financial statements)"
    )

    synonyms = {
        "revenue": [
            "revenue", "net revenue", "net sales", "sales revenue",
            "total net revenue", "gross revenue", "operating revenue",
            "total sales", "net revenues", "revenues",
            "product revenue", "service revenue",
        ],
        "expenses": [
            "total expenses", "operating expenses", "cost of revenue",
            "cost of sales", "COGS", "cost of goods sold",
            "selling general and administrative", "SG&A",
            "operating costs", "total costs", "total operating expenses",
            "research and development", "R&D expense",
        ],
        "net_income": [
            "net income", "net earnings", "net profit", "net loss",
            "net income attributable", "income from continuing operations",
            "profit after tax", "net income (loss)", "earnings (loss)",
        ],
        "ebitda": [
            "EBITDA", "earnings before interest", "adjusted EBITDA",
            "operating income before depreciation",
            "EBITDA margin",
        ],
        "assets": [
            "total assets", "current assets", "total current assets",
            "noncurrent assets", "non-current assets", "long-term assets",
            "property plant and equipment", "PP&E",
        ],
        "liabilities": [
            "total liabilities", "current liabilities", "long-term debt",
            "total debt", "noncurrent liabilities", "non-current liabilities",
            "total current liabilities", "accounts payable",
        ],
        "cash_flow": [
            "cash from operations", "operating cash flow", "net cash provided",
            "cash flow from operating activities", "free cash flow", "FCF",
            "net cash from operations", "cash provided by operating",
            "capital expenditures", "capex",
        ],
        "eps": [
            "earnings per share", "EPS", "basic EPS", "diluted EPS",
            "basic earnings per share", "diluted earnings per share",
            "net income per share", "net loss per share",
        ],
        "gross_profit": [
            "gross profit", "gross margin", "gross income",
            "total gross profit", "contribution margin",
        ],
        "operating_income": [
            "operating income", "income from operations",
            "operating profit", "operating loss", "operating income (loss)",
        ],
    }

    document_patterns = [
        r"Form\s+10-[KQ]",
        r"UNITED STATES SECURITIES AND EXCHANGE COMMISSION",
        r"Consolidated\s+(Balance\s+Sheet|Statement|Income)",
        r"FINANCIAL\s+STATEMENTS",
        r"Item\s+[178][A-Z]?\.",
        r"MANAGEMENT.S\s+DISCUSSION",
        r"EBITDA|earnings\s+per\s+share",
        r"fiscal\s+year|FY\s*\d{4}",
    ]

    chunking_strategy = "sec_items"

    query_templates = {
        "revenue": (
            "What is the total revenue for each reported period? "
            "The document may use any of these terms: {synonyms}. "
            "Report the exact figure, the term used, and the source line."
        ),
        "expenses": (
            "What are the major expense categories and their amounts? "
            "Look for: {synonyms}. "
            "List each category with its amount and the reporting period."
        ),
        "net_income": (
            "What is the net income for each reported period? "
            "The document may label this as: {synonyms}. "
            "Report the exact figure and any year-over-year change."
        ),
        "risk_factors": (
            "What are the key risk factors mentioned in this document? "
            "Summarize the top 5 most significant risks with brief descriptions."
        ),
        "cash_flow": (
            "What is the cash flow from operations for each period? "
            "Look for: {synonyms}. Report the exact figures."
        ),
        "eps": (
            "What are the basic and diluted earnings per share? "
            "Look for: {synonyms}. Report for each period available."
        ),
    }

    def _filename_keywords(self):
        return [
            "10-k", "10k", "10-q", "10q", "annual", "quarterly",
            "financial", "earnings", "sec", "filing", "proxy", "8-k",
        ]
