"""
Insurance domain plugin for RLM document analysis.

Covers the FULL spectrum of insurance lines and document types:

Property & Casualty (P&C): CGL, property, inland marine, crime, umbrella/excess
Auto / Motor Vehicle: personal auto, commercial auto, fleet, no-fault
Workers' Compensation: employers liability, experience mods, loss runs
Professional Liability: E&O, D&O, cyber liability, EPL, malpractice
Health Insurance: group health plans, EOBs, SPDs, utilization reviews
Life & Annuities: term life, whole life, universal life, annuity contracts
Surety / Bonds: performance bonds, payment bonds, bid bonds, fidelity
Reinsurance: treaties, facultative placements, loss portfolios, retrocession

Built from the perspective of claims adjusters, underwriters, and policy
analysts who spend 40%+ of their time on administrative document tasks.

The RLM approach is uniquely suited because insurance documents require
CROSS-VERIFICATION: a claim's validity depends on matching the loss
description against coverage terms, exclusions, endorsements, and
declarations — exactly the multi-section verification that Algorithm 1 enforces.
"""

from .base import BaseDomain


class InsuranceDomain(BaseDomain):
    """Insurance domain: P&C, auto, workers comp, professional, health, life, reinsurance."""

    name = "insurance"
    description = (
        "Insurance document analysis (P&C, auto, workers comp, professional "
        "liability, health, life, surety, reinsurance)"
    )

    synonyms = {
        # === Core Policy Terms (all lines) ===
        "coverage": [
            "coverage", "covered", "insuring agreement", "policy coverage",
            "covered loss", "covered peril", "named peril",
            "all-risk", "all risk", "special form", "broad form",
            "basic form", "blanket coverage", "scheduled coverage",
            # Line-specific coverage
            "bodily injury", "BI", "property damage", "PD",
            "personal injury", "advertising injury",
            "medical payments", "med pay",
            "uninsured motorist", "UM", "underinsured motorist", "UIM",
            "collision", "comprehensive", "other than collision",
        ],
        "exclusion": [
            "exclusion", "excluded", "not covered", "does not apply",
            "this policy does not cover", "this insurance does not apply",
            "limitation", "restriction", "war exclusion",
            "pollution exclusion", "flood exclusion", "mold exclusion",
            "acts of God", "force majeure",
            "intentional act", "criminal act", "punitive damages exclusion",
            "employment-related practices", "professional services",
            "cyber exclusion", "nuclear exclusion", "terrorism exclusion",
        ],
        "premium": [
            "premium", "annual premium", "written premium",
            "earned premium", "deposit premium", "minimum premium",
            "additional premium", "return premium", "audit premium",
            "premium adjustment", "rate", "rating",
            "premium base", "payroll", "gross receipts",
            "class code", "classification", "territory",
            "experience modification", "EMR", "mod factor",
            "schedule credit", "schedule debit",
        ],
        "deductible": [
            "deductible", "self-insured retention", "SIR",
            "retention", "copay", "copayment", "coinsurance",
            "waiting period", "elimination period",
            "aggregate deductible", "per-occurrence deductible",
            "each claim deductible", "corridor deductible",
            "franchise deductible", "disappearing deductible",
        ],
        "claim": [
            "claim", "loss", "occurrence", "incident", "accident",
            "loss event", "claim number", "claim amount",
            "date of loss", "reported date", "loss date",
            "first notice of loss", "FNOL", "proof of loss",
            "loss description", "claimant", "third party claim",
            "reserved amount", "incurred", "paid loss",
            "allocated loss adjustment expense", "ALAE",
            "unallocated loss adjustment expense", "ULAE",
        ],
        "insured": [
            "insured", "named insured", "additional insured",
            "policyholder", "certificate holder", "loss payee",
            "first named insured", "omnibus insured",
            "mortgagee", "beneficiary",
            "spouse", "family member", "household member",
            "employee", "volunteer", "permissive user",
        ],
        "limit": [
            "limit", "policy limit", "limit of liability",
            "aggregate limit", "per-occurrence limit",
            "sublimit", "sub-limit", "combined single limit",
            "each occurrence", "general aggregate",
            "products-completed operations aggregate",
            "personal and advertising injury limit",
            "fire damage limit", "medical expense limit",
            "umbrella limit", "excess limit",
            "split limits", "single limit",
        ],
        "endorsement": [
            "endorsement", "rider", "amendment", "addendum",
            "policy change", "modification", "supplemental",
            "additional coverage", "coverage extension",
            "blanket additional insured", "waiver of subrogation",
            "primary and noncontributory", "notice of cancellation",
        ],
        "subrogation": [
            "subrogation", "recovery", "salvage",
            "right of recovery", "waiver of subrogation",
            "transfer of rights", "reimbursement",
            "contribution", "other insurance clause",
        ],
        "underwriting": [
            "underwriting", "risk assessment", "risk evaluation",
            "loss history", "loss run", "experience modification",
            "EMR", "loss ratio", "combined ratio",
            "risk selection", "risk classification",
            "schedule rating", "classification code",
            "NCCI", "ISO", "advisory rate", "filed rate",
            "binding authority", "submission", "quote",
        ],
        # === Professional Liability ===
        "professional_liability": [
            "errors and omissions", "E&O",
            "directors and officers", "D&O",
            "employment practices liability", "EPL", "EPLI",
            "fiduciary liability", "cyber liability",
            "technology errors and omissions", "tech E&O",
            "media liability", "professional indemnity",
            "malpractice", "medical malpractice",
            "claims-made", "occurrence form",
            "retroactive date", "extended reporting period", "tail",
            "prior acts", "hammer clause", "consent to settle",
        ],
        # === Workers' Compensation ===
        "workers_comp": [
            "workers compensation", "workers comp", "WC",
            "employers liability", "EL",
            "statutory benefits", "medical benefits",
            "indemnity benefits", "temporary total disability", "TTD",
            "permanent partial disability", "PPD",
            "permanent total disability", "PTD",
            "vocational rehabilitation", "return to work",
            "experience modification rate", "EMR", "x-mod",
            "monopolistic state", "assigned risk",
            "NCCI class code", "payroll audit",
        ],
        # === Health Insurance ===
        "health_insurance": [
            "summary plan description", "SPD",
            "explanation of benefits", "EOB",
            "formulary", "prior authorization",
            "network", "in-network", "out-of-network",
            "preferred provider", "PPO", "HMO", "EPO", "POS",
            "out-of-pocket maximum", "MOOP",
            "annual deductible", "family deductible",
            "covered benefit", "excluded benefit",
            "utilization review", "precertification",
            "ERISA", "COBRA", "ACA", "essential health benefit",
        ],
        # === Life & Annuity ===
        "life_annuity": [
            "death benefit", "face amount", "sum insured",
            "term life", "whole life", "universal life",
            "variable life", "cash value", "surrender value",
            "beneficiary", "contingent beneficiary",
            "annuity", "annuitant", "accumulation period",
            "payout period", "guaranteed minimum",
            "mortality charge", "cost of insurance",
            "incontestability", "grace period",
            "suicide clause", "contestability period",
        ],
        # === Reinsurance ===
        "reinsurance": [
            "reinsurance", "reinsurer", "ceding company", "cedant",
            "treaty", "facultative", "retrocession",
            "quota share", "surplus share", "excess of loss",
            "aggregate excess", "stop loss",
            "retention", "cession", "ceded premium",
            "loss portfolio transfer", "LPT",
            "commutation", "cut-through",
            "follow the fortunes", "follow the settlements",
            "inuring", "net retention",
        ],
    }

    document_patterns = [
        # Core policy
        r"DECLARATIONS?\s*(?:PAGE)?",
        r"(?:COMMERCIAL\s+)?GENERAL\s+LIABILITY",
        r"WORKERS.?\s*COMPENSATION",
        r"(?:POLICY|CERTIFICATE)\s+(?:NUMBER|NO|#)",
        r"INSURING\s+AGREEMENT",
        r"(?:THIS|THE)\s+(?:POLICY|INSURANCE)\s+(?:DOES\s+NOT\s+)?(?:COVER|APPL)",
        r"EXCLUSIONS?",
        r"CONDITIONS?\s+(?:OF\s+)?(?:THE\s+)?POLICY",
        r"ENDORSEMENT(?:S|\s+NO)",
        r"(?:PREMIUM|DEDUCTIBLE|LIMIT\s+OF\s+LIABILITY)",
        r"CERTIFICATE\s+OF\s+(?:INSURANCE|LIABILITY)",
        r"(?:LOSS|CLAIM)\s+(?:RUN|REPORT|HISTORY)",
        # Auto
        r"(?:PERSONAL|COMMERCIAL)\s+AUTO",
        r"(?:COLLISION|COMPREHENSIVE|UNINSURED\s+MOTORIST)",
        # Professional
        r"(?:ERRORS\s+AND\s+OMISSIONS|E&O|D&O)",
        r"(?:CLAIMS.MADE|RETROACTIVE\s+DATE)",
        r"(?:CYBER|TECHNOLOGY)\s+(?:LIABILITY|INSURANCE)",
        # Health
        r"(?:SUMMARY\s+PLAN\s+DESCRIPTION|SPD)",
        r"(?:EXPLANATION\s+OF\s+BENEFITS|EOB)",
        r"(?:PPO|HMO|NETWORK\s+PROVIDER)",
        # Life
        r"(?:DEATH\s+BENEFIT|FACE\s+AMOUNT|CASH\s+VALUE)",
        r"(?:TERM\s+LIFE|WHOLE\s+LIFE|UNIVERSAL\s+LIFE)",
        # Reinsurance
        r"(?:REINSURANCE|TREATY|FACULTATIVE)",
        r"(?:CEDING\s+COMPANY|QUOTA\s+SHARE|EXCESS\s+OF\s+LOSS)",
        # Surety
        r"(?:PERFORMANCE|PAYMENT|BID)\s+BOND",
        r"(?:SURETY|PRINCIPAL|OBLIGEE)",
    ]

    chunking_strategy = "sections"

    query_templates = {
        # Core policy
        "coverage": (
            "What coverages does this policy provide? "
            "Look for: {synonyms}. "
            "List each coverage type with its limit, deductible, and any special conditions."
        ),
        "exclusions": (
            "What exclusions or limitations apply to this policy? "
            "Look for: {synonyms}. "
            "List each exclusion and what specific losses or perils are not covered."
        ),
        "limits": (
            "What are the policy limits? "
            "Look for: {synonyms}. "
            "Include per-occurrence, aggregate, and any sublimits."
        ),
        "insured_parties": (
            "Who is insured under this policy? "
            "Look for: {synonyms}. "
            "Include named insured, additional insureds, and any certificate holders."
        ),
        "claims": (
            "What claim or loss information is documented? "
            "Look for: {synonyms}. "
            "Include date of loss, description, claim amount, and status."
        ),
        "endorsements": (
            "What endorsements or riders modify this policy? "
            "Look for: {synonyms}. "
            "List each endorsement with its effective date and what it changes."
        ),
        "premium_deductible": (
            "What are the premium and deductible amounts? "
            "Look for: {synonyms}. "
            "Include any premium adjustments or payment schedules."
        ),
        # Professional liability sub-sector
        "professional_coverage": (
            "What professional liability coverages are provided? "
            "Look for: {synonyms}. "
            "Include claims-made vs occurrence, retro date, and extended reporting."
        ),
        # Workers comp sub-sector
        "workers_comp_terms": (
            "What workers compensation terms and benefits apply? "
            "Look for: {synonyms}. "
            "Include statutory state, classification codes, EMR, and benefit levels."
        ),
        # Health sub-sector
        "health_benefits": (
            "What health insurance benefits and cost-sharing apply? "
            "Look for: {synonyms}. "
            "Include plan type, deductible, copays, coinsurance, and OOP maximum."
        ),
        # Reinsurance sub-sector
        "reinsurance_terms": (
            "What are the reinsurance terms and structure? "
            "Look for: {synonyms}. "
            "Include type (treaty/fac), retention, cession, and any special conditions."
        ),
    }

    def _filename_keywords(self):
        return [
            # Core
            "policy", "insurance", "claim", "endorsement",
            "certificate", "coi", "loss", "underwriting",
            "declarations", "schedule", "binder",
            # Line-specific
            "auto", "vehicle", "fleet",
            "workers comp", "wc", "employers liability",
            "professional", "e&o", "d&o", "cyber", "epl",
            "health", "medical", "dental", "vision",
            "life", "annuity", "beneficiary",
            "surety", "bond", "fidelity",
            "reinsurance", "treaty", "facultative",
            "umbrella", "excess", "inland marine",
        ]
