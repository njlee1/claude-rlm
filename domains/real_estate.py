"""
Real estate domain plugin for RLM document analysis.

Covers the FULL spectrum of real estate document types:

Commercial Leasing: office, retail, industrial, NNN, gross, ground leases
Residential: purchase agreements, listing agreements, HOA docs, rental agreements
Construction: AIA contracts, change orders, lien waivers, certificates of occupancy
REIT / Investment: offering memorandums, operating agreements, K-1s, valuations
Appraisal / Valuation: appraisal reports, BPOs, comparable sales, cap rate analysis
Title / Closing: title commitments, surveys, closing statements (HUD-1/CD), deeds
Development: zoning applications, site plans, environmental (Phase I/II), entitlements
Property Management: budgets, rent rolls, aged receivables, maintenance logs

Built from the perspective of asset managers, paralegals, and analysts who
spend 4-8 hours manually abstracting a single complex commercial lease.

The RLM approach excels because real estate documents are LONG (30-100+ pages)
with critical data scattered throughout. The synonym expansion is essential:
"rent" alone misses "base rent", "minimum rent", "annual rent", "fixed rent",
"guaranteed minimum" — all the same concept across different templates.
"""

from .base import BaseDomain


class RealEstateDomain(BaseDomain):
    """Real estate domain: leasing, residential, construction, REIT, appraisal, title."""

    name = "real_estate"
    description = (
        "Real estate document analysis (commercial leasing, residential, "
        "construction, REIT, appraisal, title/closing)"
    )

    synonyms = {
        # === Commercial Leasing ===
        "rent": [
            "rent", "base rent", "minimum rent", "annual rent",
            "fixed rent", "guaranteed minimum rent", "monthly rent",
            "basic rent", "net rent", "gross rent",
            "percentage rent", "overage rent", "additional rent",
            "base rental", "contract rent", "market rent",
            "effective rent", "face rent", "asking rent",
        ],
        "tenant": [
            "tenant", "lessee", "occupant", "renter",
            "subtenant", "sublessee", "assignee",
            "guarantor", "tenant entity",
            "buyer", "purchaser", "grantee",
            "homeowner", "borrower", "mortgagor",
        ],
        "landlord": [
            "landlord", "lessor", "owner", "property owner",
            "management company", "property manager",
            "fee owner", "ground lessor",
            "seller", "grantor", "vendor",
            "developer", "sponsor",
        ],
        "lease_term": [
            "lease term", "term", "commencement date", "start date",
            "expiration date", "end date", "lease expiration",
            "initial term", "primary term", "extended term",
            "lease period", "tenancy period",
            "rent commencement date", "beneficial occupancy",
            "substantial completion", "delivery date",
        ],
        "renewal": [
            "renewal", "renewal option", "option to renew",
            "extension", "extension option", "option to extend",
            "holdover", "renewal term", "extension term",
            "right of renewal", "renewal notice",
            "month-to-month", "automatic renewal",
        ],
        "cam": [
            "CAM", "common area maintenance", "operating expenses",
            "common area", "maintenance charges", "shared expenses",
            "proportionate share", "pro rata share",
            "tenant's share", "operating cost",
            "controllable expenses", "non-controllable",
            "base year", "expense stop", "gross-up",
            "real estate taxes", "property taxes", "insurance",
            "management fee", "capital expenditure",
        ],
        "escalation": [
            "escalation", "rent escalation", "rent increase",
            "annual increase", "CPI adjustment", "CPI escalation",
            "cost of living adjustment", "COLA",
            "fixed increase", "percentage increase", "step-up",
            "rent bump", "annual adjustment", "fair market value",
            "FMV reset", "mark to market",
        ],
        "security_deposit": [
            "security deposit", "deposit", "letter of credit",
            "LOC", "surety bond", "security",
            "damage deposit", "lease deposit",
            "good faith deposit", "earnest money",
            "escrow deposit", "holdback",
        ],
        "square_footage": [
            "square footage", "square feet", "SF", "RSF",
            "rentable square feet", "usable square feet", "USF",
            "gross leasable area", "GLA", "net leasable area",
            "premises area", "demised premises",
            "building area", "lot size", "acreage", "acres",
            "load factor", "add-on factor", "common area factor",
        ],
        "permitted_use": [
            "permitted use", "use clause", "exclusive use",
            "restricted use", "prohibited use",
            "zoning", "intended use", "approved use",
            "co-tenancy", "radius restriction",
            "go-dark", "continuous operation", "operating covenant",
        ],
        "nnn": [
            "NNN", "triple net", "net net net",
            "net lease", "modified gross", "full service",
            "gross lease", "absolute net", "double net",
            "single net", "lease type", "lease structure",
            "modified net", "industrial gross",
        ],
        "termination": [
            "termination", "early termination", "termination option",
            "kick-out clause", "break clause", "cancellation",
            "termination fee", "termination penalty",
            "surrender", "lease termination",
            "recapture", "right of recapture",
        ],
        # === Purchase / Sale ===
        "purchase": [
            "purchase price", "sale price", "contract price",
            "agreed price", "asking price", "offer price",
            "closing price", "adjusted purchase price",
            "earnest money", "good faith deposit",
            "due diligence period", "inspection period",
            "contingency", "financing contingency", "appraisal contingency",
            "closing date", "settlement date",
            "title", "clear title", "marketable title",
            "deed", "warranty deed", "quitclaim deed", "special warranty",
        ],
        # === Construction ===
        "construction": [
            "AIA contract", "construction contract",
            "general contractor", "GC", "subcontractor",
            "scope of work", "plans and specifications",
            "change order", "change directive",
            "substantial completion", "final completion",
            "punch list", "retainage", "retention",
            "lien waiver", "mechanic's lien", "materialman's lien",
            "certificate of occupancy", "CO", "TCO",
            "progress payment", "application for payment",
            "liquidated damages", "delay damages",
            "performance bond", "payment bond",
        ],
        # === REIT / Investment ===
        "investment": [
            "cap rate", "capitalization rate",
            "NOI", "net operating income",
            "cash-on-cash return", "yield",
            "IRR", "internal rate of return",
            "equity multiple", "debt yield",
            "occupancy rate", "vacancy rate",
            "rent roll", "rent roll analysis",
            "offering memorandum", "OM",
            "operating agreement", "partnership agreement",
            "K-1", "distribution", "waterfall",
            "preferred return", "pref",
            "promote", "carried interest",
            "REIT", "real estate investment trust",
            "FFO", "funds from operations",
            "AFFO", "adjusted funds from operations",
        ],
        # === Appraisal / Valuation ===
        "appraisal": [
            "appraisal", "appraisal report", "appraised value",
            "fair market value", "FMV", "as-is value",
            "as-stabilized value", "as-complete value",
            "income approach", "sales comparison approach",
            "cost approach", "comparable sales", "comps",
            "adjustment grid", "highest and best use",
            "discount rate", "terminal cap rate",
            "BPO", "broker price opinion",
            "replacement cost", "reproduction cost",
        ],
        # === Title / Closing ===
        "title": [
            "title commitment", "title insurance", "title policy",
            "title search", "title exception", "title defect",
            "lien", "encumbrance", "easement", "covenant",
            "deed restriction", "encroachment",
            "survey", "plat", "legal description",
            "metes and bounds", "lot and block",
            "closing statement", "settlement statement",
            "HUD-1", "closing disclosure", "CD",
            "proration", "adjustment", "credit",
        ],
        # === Environmental ===
        "environmental": [
            "Phase I", "Phase II", "environmental site assessment",
            "ESA", "recognized environmental condition", "REC",
            "controlled REC", "CREC", "historical REC", "HREC",
            "remediation", "contamination", "underground storage tank",
            "asbestos", "lead paint", "hazardous material",
            "CERCLA", "brownfield", "clean-up",
        ],
    }

    document_patterns = [
        # Commercial leasing
        r"LEASE\s+AGREEMENT",
        r"(?:COMMERCIAL|OFFICE|RETAIL|INDUSTRIAL)\s+LEASE",
        r"LANDLORD|LESSOR",
        r"TENANT|LESSEE",
        r"(?:BASE|MINIMUM|ANNUAL)\s+RENT",
        r"COMMON\s+AREA\s+MAINTENANCE|CAM",
        r"(?:COMMENCEMENT|EXPIRATION)\s+DATE",
        r"(?:PREMISES|DEMISED|LEASED)\s+(?:SPACE|PREMISES|AREA)",
        r"SQUARE\s+(?:FEET|FOOTAGE)",
        r"(?:RENEWAL|EXTENSION)\s+OPTION",
        r"SECURITY\s+DEPOSIT",
        r"TRIPLE\s+NET|NNN",
        # Purchase / Sale
        r"(?:PURCHASE|SALE)\s+(?:AGREEMENT|CONTRACT)",
        r"(?:EARNEST\s+MONEY|GOOD\s+FAITH)\s+DEPOSIT",
        r"(?:CLOSING|SETTLEMENT)\s+(?:DATE|STATEMENT)",
        r"(?:WARRANTY|QUITCLAIM|SPECIAL\s+WARRANTY)\s+DEED",
        # Construction
        r"(?:AIA|CONSTRUCTION)\s+(?:CONTRACT|AGREEMENT)",
        r"(?:CHANGE\s+ORDER|SUBSTANTIAL\s+COMPLETION)",
        r"(?:LIEN\s+WAIVER|MECHANIC.S\s+LIEN)",
        r"(?:CERTIFICATE\s+OF\s+OCCUPANCY|TCO|CO)",
        # REIT / Investment
        r"(?:OFFERING\s+MEMORANDUM|OPERATING\s+AGREEMENT)",
        r"(?:CAP\s+RATE|NET\s+OPERATING\s+INCOME|NOI)",
        r"(?:REIT|FFO|AFFO)",
        # Appraisal
        r"(?:APPRAISAL\s+REPORT|APPRAISED\s+VALUE)",
        r"(?:INCOME\s+APPROACH|SALES\s+COMPARISON|COST\s+APPROACH)",
        # Title
        r"(?:TITLE\s+(?:COMMITMENT|INSURANCE|POLICY))",
        r"(?:LEGAL\s+DESCRIPTION|METES\s+AND\s+BOUNDS)",
        # Environmental
        r"(?:PHASE\s+[I1]\s+|ENVIRONMENTAL\s+SITE\s+ASSESSMENT)",
    ]

    chunking_strategy = "sections"

    query_templates = {
        # Commercial leasing
        "rent": (
            "What is the rent structure for this lease? "
            "Look for: {synonyms}. "
            "Include base rent amount, payment frequency, and any percentage rent provisions."
        ),
        "lease_term": (
            "What is the lease term (start and end dates)? "
            "Look for: {synonyms}. "
            "Include commencement date, expiration date, and total lease duration."
        ),
        "escalation": (
            "What are the rent escalation provisions? "
            "Look for: {synonyms}. "
            "Include the escalation schedule, rate or formula, and effective dates."
        ),
        "cam": (
            "What are the CAM and operating expense provisions? "
            "Look for: {synonyms}. "
            "Include tenant's proportionate share, cap provisions, and exclusions."
        ),
        "renewal": (
            "What renewal or extension options does the tenant have? "
            "Look for: {synonyms}. "
            "Include notice requirements, renewal rent terms, and number of options."
        ),
        "parties": (
            "Who are the parties to this lease? "
            "Look for: {synonyms}. "
            "Include tenant entity, landlord entity, and any guarantors."
        ),
        "termination": (
            "What are the early termination provisions? "
            "Look for: {synonyms}. "
            "Include termination fees, notice periods, and conditions."
        ),
        # Purchase / Sale sub-sector
        "purchase_terms": (
            "What are the purchase price and key deal terms? "
            "Look for: {synonyms}. "
            "Include price, deposit, contingencies, due diligence period, and closing date."
        ),
        # Construction sub-sector
        "construction_terms": (
            "What are the construction contract terms? "
            "Look for: {synonyms}. "
            "Include contract sum, scope, completion dates, retainage, and change order process."
        ),
        # Investment / REIT sub-sector
        "investment_metrics": (
            "What are the key investment metrics? "
            "Look for: {synonyms}. "
            "Include cap rate, NOI, occupancy, IRR, equity multiple, and waterfall structure."
        ),
        # Appraisal sub-sector
        "valuation": (
            "What is the appraised value and methodology? "
            "Look for: {synonyms}. "
            "Include all three approaches (income, sales comparison, cost) and final reconciliation."
        ),
        # Title sub-sector
        "title_issues": (
            "What title exceptions or encumbrances exist? "
            "Look for: {synonyms}. "
            "List all liens, easements, covenants, and restrictions affecting the property."
        ),
    }

    def _filename_keywords(self):
        return [
            # Leasing
            "lease", "rental", "property", "real estate",
            "commercial", "office", "retail", "industrial",
            "estoppel", "snda", "loi",
            # Purchase / Sale
            "purchase", "sale", "deed", "closing",
            "settlement", "hud", "contract",
            # Construction
            "aia", "construction", "change order",
            "lien waiver", "certificate", "punch list",
            # Investment
            "offering", "memorandum", "om", "reit",
            "operating agreement", "k-1",
            # Appraisal
            "appraisal", "bpo", "valuation",
            # Title
            "title", "survey", "commitment",
            "easement", "covenant",
            # Environmental
            "phase i", "phase ii", "environmental", "esa",
            # Residential
            "residential", "condo", "hoa",
            "townhouse", "single family",
        ]
