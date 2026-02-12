"""
Finance domain plugin for RLM document analysis.

Covers the FULL spectrum of finance, not just SEC filings:

SEC / Public Company: 10-K, 10-Q, proxy statements, S-1 filings, 8-K
Investment Banking / M&A: pitch books, CIMs, fairness opinions, merger proxies
Private Equity / VC: term sheets, PPMs, LP agreements, capital calls, DDQs
Hedge Funds: investor letters, DDQs, performance reports, risk disclosures
Asset Management: fund factsheets, prospectuses, SAIs, holdings reports
Banking: loan agreements, credit memos, call reports, stress test results
Corporate Finance: budgets, forecasts, board presentations, treasury reports
Credit / Fixed Income: bond indentures, credit agreements, rating reports

The synonym expansion is critical because each sub-sector has its own
vocabulary. A 10-K says "net sales" while a PE fund says "net asset value"
and a credit agreement says "total leverage ratio" — all are finance, all
need domain-specific synonym resolution.
"""

from .base import BaseDomain


class FinanceDomain(BaseDomain):
    """Finance domain: SEC filings, M&A, PE/VC, banking, asset management."""

    name = "finance"
    description = (
        "Financial document analysis (SEC filings, M&A, PE/VC, banking, "
        "asset management, credit, corporate finance)"
    )

    synonyms = {
        # === Core Financial Statements (SEC / public company) ===
        "revenue": [
            "revenue", "net revenue", "net sales", "sales revenue",
            "total net revenue", "gross revenue", "operating revenue",
            "total sales", "net revenues", "revenues",
            "product revenue", "service revenue", "total net revenues",
            "net product sales", "subscription revenue",
            "fee income", "interest income", "premium income",
            "commission income", "advisory fees",
        ],
        "expenses": [
            "total expenses", "operating expenses", "cost of revenue",
            "cost of sales", "COGS", "cost of goods sold",
            "selling general and administrative", "SG&A",
            "operating costs", "total costs", "total operating expenses",
            "research and development", "R&D expense",
            "cost of products sold", "cost of services",
            "provision for credit losses", "loan loss provision",
            "management fee", "performance fee", "carried interest expense",
        ],
        "net_income": [
            "net income", "net earnings", "net profit", "net loss",
            "net income attributable", "income from continuing operations",
            "profit after tax", "net income (loss)", "earnings (loss)",
            "net income attributable to common",
            "distributable earnings", "economic net income",
            "fund net income", "net investment income",
        ],
        "ebitda": [
            "EBITDA", "earnings before interest", "adjusted EBITDA",
            "operating income before depreciation",
            "EBITDA margin", "run-rate EBITDA", "pro forma EBITDA",
            "LTM EBITDA", "trailing twelve months EBITDA",
        ],
        "assets": [
            "total assets", "current assets", "total current assets",
            "noncurrent assets", "non-current assets", "long-term assets",
            "property plant and equipment", "PP&E",
            "assets under management", "AUM", "total AUM",
            "net asset value", "NAV", "gross asset value", "GAV",
            "fund assets", "portfolio value",
        ],
        "liabilities": [
            "total liabilities", "current liabilities", "long-term debt",
            "total debt", "noncurrent liabilities", "non-current liabilities",
            "total current liabilities", "accounts payable",
            "total leverage", "net debt", "funded debt",
            "senior debt", "subordinated debt", "mezzanine",
        ],
        "cash_flow": [
            "cash from operations", "operating cash flow", "net cash provided",
            "cash flow from operating activities", "free cash flow", "FCF",
            "net cash from operations", "cash provided by operating",
            "capital expenditures", "capex",
            "distributions", "capital calls", "drawdowns",
            "cash available for distribution", "CAFD",
        ],
        "eps": [
            "earnings per share", "EPS", "basic EPS", "diluted EPS",
            "basic earnings per share", "diluted earnings per share",
            "net income per share", "net loss per share",
            "FFO per share", "AFFO per share",
        ],
        "gross_profit": [
            "gross profit", "gross margin", "gross income",
            "total gross profit", "contribution margin",
            "gross profit margin", "product margin",
        ],
        "operating_income": [
            "operating income", "income from operations",
            "operating profit", "operating loss", "operating income (loss)",
            "segment operating income", "adjusted operating income",
        ],
        # === Investment Banking / M&A ===
        "valuation": [
            "enterprise value", "EV", "equity value", "market cap",
            "market capitalization", "EV/EBITDA", "EV/Revenue",
            "P/E ratio", "price to earnings", "price to book",
            "DCF", "discounted cash flow", "terminal value",
            "comparable companies", "precedent transactions", "comps",
            "implied valuation", "fairness opinion",
            "sum of the parts", "SOTP", "NAV per share",
        ],
        "deal_terms": [
            "purchase price", "acquisition price", "offer price",
            "consideration", "cash consideration", "stock consideration",
            "merger consideration", "exchange ratio",
            "earnout", "escrow", "holdback", "working capital adjustment",
            "break-up fee", "termination fee", "reverse termination fee",
            "material adverse effect", "MAC clause", "MAE",
            "representations and warranties", "closing conditions",
        ],
        "synergy": [
            "synergy", "synergies", "cost synergy", "revenue synergy",
            "run-rate synergies", "integration costs",
            "pro forma", "combined entity", "accretion", "dilution",
            "accretion/dilution", "accretive", "dilutive",
        ],
        # === Private Equity / Venture Capital ===
        "pe_returns": [
            "IRR", "internal rate of return", "net IRR", "gross IRR",
            "MOIC", "multiple on invested capital", "TVPI",
            "DPI", "distributions to paid-in", "RVPI",
            "total value to paid-in", "cash-on-cash return",
            "realized return", "unrealized return",
            "carried interest", "carry", "promote",
            "management fee", "hurdle rate", "preferred return",
            "catch-up", "clawback", "waterfall",
        ],
        "fund_structure": [
            "limited partner", "LP", "general partner", "GP",
            "fund size", "vintage year", "fund term",
            "commitment", "capital commitment", "unfunded commitment",
            "capital call", "drawdown", "distribution",
            "committed capital", "invested capital", "dry powder",
            "PPM", "private placement memorandum",
            "subscription agreement", "side letter",
            "GP commitment", "co-investment",
        ],
        # === Banking / Credit ===
        "credit_metrics": [
            "leverage ratio", "total leverage ratio", "net leverage ratio",
            "debt to EBITDA", "net debt to EBITDA",
            "interest coverage ratio", "fixed charge coverage",
            "debt service coverage ratio", "DSCR",
            "loan to value", "LTV",
            "current ratio", "quick ratio",
            "tier 1 capital", "CET1", "capital adequacy ratio", "CAR",
            "non-performing loans", "NPL", "NPL ratio",
            "net charge-offs", "provision coverage ratio",
        ],
        "loan_terms": [
            "principal", "maturity", "maturity date",
            "interest rate", "SOFR", "LIBOR", "spread", "margin",
            "amortization", "bullet maturity", "revolving credit",
            "term loan", "revolver", "facility",
            "covenants", "financial covenants", "maintenance covenants",
            "incurrence covenants", "negative covenants",
            "events of default", "cross-default",
            "collateral", "security interest", "lien",
            "first lien", "second lien", "unsecured",
        ],
        # === Asset Management / Funds ===
        "fund_performance": [
            "total return", "annualized return", "cumulative return",
            "alpha", "beta", "Sharpe ratio", "Sortino ratio",
            "standard deviation", "volatility", "max drawdown",
            "tracking error", "information ratio",
            "benchmark", "outperformance", "underperformance",
            "net of fees", "gross of fees",
            "yield", "SEC yield", "distribution yield",
            "expense ratio", "total expense ratio", "TER",
        ],
    }

    document_patterns = [
        # SEC filings
        r"Form\s+10-[KQ]",
        r"UNITED STATES SECURITIES AND EXCHANGE COMMISSION",
        r"Consolidated\s+(Balance\s+Sheet|Statement|Income)",
        r"FINANCIAL\s+STATEMENTS",
        r"Item\s+[178][A-Z]?\.",
        r"MANAGEMENT.S\s+DISCUSSION",
        r"EBITDA|earnings\s+per\s+share",
        r"fiscal\s+year|FY\s*\d{4}",
        # M&A / Investment Banking
        r"(?:MERGER|ACQUISITION)\s+AGREEMENT",
        r"FAIRNESS\s+OPINION",
        r"(?:CONFIDENTIAL\s+)?INFORMATION\s+MEMORANDUM",
        r"(?:ENTERPRISE|EQUITY)\s+VALUE",
        # PE / VC
        r"(?:LIMITED|GENERAL)\s+PARTNER",
        r"PRIVATE\s+PLACEMENT\s+MEMORANDUM",
        r"(?:CAPITAL\s+CALL|DISTRIBUTION)\s+NOTICE",
        r"(?:IRR|MOIC|TVPI|DPI)",
        # Banking / Credit
        r"(?:CREDIT|LOAN|FACILITY)\s+AGREEMENT",
        r"(?:LEVERAGE|COVERAGE)\s+RATIO",
        r"(?:FIRST|SECOND)\s+LIEN",
        # Asset Management
        r"(?:FUND|PORTFOLIO)\s+(?:PERFORMANCE|FACTSHEET|REPORT)",
        r"(?:NET\s+ASSET\s+VALUE|NAV)",
        r"(?:PROSPECTUS|STATEMENT\s+OF\s+ADDITIONAL\s+INFORMATION)",
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
        # M&A sub-sector
        "valuation": (
            "What is the valuation or purchase price? "
            "Look for: {synonyms}. "
            "Include methodology (DCF, comps, precedents), multiples, and implied value."
        ),
        "deal_structure": (
            "What is the deal structure and consideration? "
            "Look for: {synonyms}. "
            "Include cash/stock mix, earnouts, escrow, and closing conditions."
        ),
        # PE / VC sub-sector
        "fund_returns": (
            "What are the fund's return metrics? "
            "Look for: {synonyms}. "
            "Include IRR (net and gross), MOIC, TVPI, DPI, and vintage year."
        ),
        "fund_terms": (
            "What are the fund structure and terms? "
            "Look for: {synonyms}. "
            "Include fund size, management fee, carry, hurdle, and GP commitment."
        ),
        # Banking / Credit sub-sector
        "credit_analysis": (
            "What are the key credit metrics and covenant levels? "
            "Look for: {synonyms}. "
            "Include leverage ratio, coverage ratios, and any covenant compliance."
        ),
        "loan_structure": (
            "What are the loan terms and structure? "
            "Look for: {synonyms}. "
            "Include principal, maturity, rate, amortization, and collateral."
        ),
        # Asset Management sub-sector
        "fund_performance": (
            "What is the fund's performance? "
            "Look for: {synonyms}. "
            "Include returns, benchmark comparison, risk metrics, and expense ratio."
        ),
    }

    def _filename_keywords(self):
        return [
            # SEC / Public
            "10-k", "10k", "10-q", "10q", "annual", "quarterly",
            "financial", "earnings", "sec", "filing", "proxy", "8-k",
            # M&A / IB
            "cim", "pitch", "fairness", "merger", "acquisition",
            "teaser", "offering",
            # PE / VC
            "ppm", "term sheet", "termsheet", "lpa", "capital call",
            "distribution", "fund", "vintage",
            # Banking / Credit
            "credit", "loan", "facility", "indenture", "covenant",
            # Asset Management
            "prospectus", "factsheet", "performance", "nav",
            "holdings", "portfolio",
        ]
