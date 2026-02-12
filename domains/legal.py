"""
Legal domain plugin for RLM document analysis.

Covers the FULL spectrum of legal practice areas:

Contracts / Transactions: NDAs, MSAs, purchase agreements, license agreements
Corporate Governance: bylaws, board resolutions, shareholder agreements, proxies
Litigation: complaints, motions, briefs, court orders, discovery, depositions
Intellectual Property: patents, trademark filings, licensing, cease & desist
Employment Law: offer letters, employment agreements, severance, non-competes
Regulatory / Government: regulations, administrative orders, rulemaking, consent decrees
Real Property Law: deeds, easements, title opinions (distinct from real_estate domain's
  lease-focused extraction — this covers the legal analysis angle)

The synonym expansion matters because legal language varies dramatically by
practice area. A contract says "shall" while a court order says "hereby ordered"
and a patent says "claimed invention" — all are legal obligations expressed
differently.
"""

from .base import BaseDomain


class LegalDomain(BaseDomain):
    """Legal domain: contracts, litigation, IP, corporate governance, employment."""

    name = "legal"
    description = (
        "Legal document analysis (contracts, litigation, IP, corporate "
        "governance, employment law, regulatory)"
    )

    synonyms = {
        # === Core Contract Terms ===
        "party": [
            "party", "parties", "plaintiff", "defendant",
            "claimant", "respondent", "petitioner", "appellant",
            "appellee", "counterparty", "contracting party",
            "licensor", "licensee", "lessor", "lessee",
            "employer", "employee", "principal", "agent",
            "grantor", "grantee", "assignor", "assignee",
            "indemnitor", "indemnitee", "obligor", "obligee",
        ],
        "obligation": [
            "shall", "must", "agrees to", "is obligated to",
            "covenant", "undertakes", "warrants", "represents",
            "is required to", "will", "obligation",
            "hereby ordered", "it is ordered", "the court orders",
            "is directed to", "shall comply",
        ],
        "termination": [
            "termination", "cancellation", "expiration",
            "rescission", "revocation", "end of term",
            "termination for cause", "termination for convenience",
            "early termination", "non-renewal",
            "termination without cause", "at-will termination",
            "constructive termination", "material breach",
        ],
        "liability": [
            "liability", "indemnification", "indemnify",
            "hold harmless", "limitation of liability",
            "cap on liability", "consequential damages",
            "direct damages", "liquidated damages",
            "punitive damages", "treble damages",
            "joint and several liability", "vicarious liability",
            "strict liability", "negligence", "gross negligence",
        ],
        "confidentiality": [
            "confidential", "confidentiality", "non-disclosure",
            "NDA", "proprietary information", "trade secret",
            "confidential information", "protected information",
            "privileged", "attorney-client privilege",
            "work product doctrine", "classified",
        ],
        "compensation": [
            "compensation", "payment", "fee", "consideration",
            "price", "royalty", "milestone payment",
            "upfront payment", "annual fee", "license fee",
            "damages", "settlement", "judgment", "award",
            "attorney fees", "costs", "restitution",
        ],
        "governing_law": [
            "governing law", "choice of law", "jurisdiction",
            "venue", "arbitration", "dispute resolution",
            "applicable law", "forum selection",
            "exclusive jurisdiction", "mandatory arbitration",
            "class action waiver", "mediation", "ADR",
        ],
        "intellectual_property": [
            "intellectual property", "IP", "patent", "trademark",
            "copyright", "trade secret", "license grant",
            "ownership", "work product", "invention",
            "prior art", "claims", "patent claims",
            "prosecution", "infringement", "misappropriation",
            "trade dress", "service mark", "utility patent",
            "design patent", "provisional patent",
        ],
        # === Litigation ===
        "litigation": [
            "complaint", "answer", "counterclaim", "cross-claim",
            "motion", "motion to dismiss", "summary judgment",
            "preliminary injunction", "temporary restraining order",
            "discovery", "interrogatories", "deposition",
            "request for production", "subpoena",
            "trial", "verdict", "judgment", "appeal",
            "class action", "class certification",
        ],
        "court_procedure": [
            "cause of action", "statute of limitations",
            "standing", "burden of proof", "standard of review",
            "prima facie", "preponderance of evidence",
            "beyond reasonable doubt", "clear and convincing",
            "res judicata", "collateral estoppel",
            "injunctive relief", "declaratory judgment",
            "writ", "mandamus", "certiorari",
        ],
        # === Corporate Governance ===
        "corporate": [
            "bylaws", "articles of incorporation", "certificate of incorporation",
            "board of directors", "board resolution", "unanimous consent",
            "shareholder", "stockholder", "voting rights",
            "fiduciary duty", "duty of care", "duty of loyalty",
            "business judgment rule", "derivative action",
            "proxy statement", "annual meeting", "special meeting",
            "quorum", "majority vote", "supermajority",
        ],
        "equity": [
            "stock", "shares", "common stock", "preferred stock",
            "stock option", "option grant", "restricted stock",
            "RSU", "vesting", "vesting schedule", "cliff vesting",
            "exercise price", "strike price", "fair market value",
            "dilution", "anti-dilution", "preemptive rights",
            "right of first refusal", "tag-along", "drag-along",
            "conversion", "liquidation preference",
        ],
        # === Employment Law ===
        "employment": [
            "employment agreement", "offer letter", "at-will",
            "non-compete", "non-solicitation", "non-disparagement",
            "restrictive covenant", "garden leave",
            "severance", "separation agreement", "release of claims",
            "WARN Act", "wrongful termination",
            "discrimination", "harassment", "retaliation",
            "EEOC", "Title VII", "ADA", "FMLA", "FLSA",
            "exempt", "non-exempt", "overtime",
        ],
        # === Regulatory ===
        "regulatory": [
            "regulation", "rule", "statute", "ordinance",
            "administrative order", "consent decree", "consent order",
            "rulemaking", "notice and comment",
            "enforcement action", "civil penalty", "fine",
            "cease and desist", "injunction", "prohibition",
            "compliance requirement", "reporting requirement",
            "license", "permit", "authorization",
        ],
    }

    document_patterns = [
        # Contracts
        r"AGREEMENT",
        r"CONTRACT",
        r"WHEREAS",
        r"IN WITNESS WHEREOF",
        r"NOW,?\s+THEREFORE",
        r"ARTICLE\s+[IVX]+",
        r"Section\s+\d+\.\d+",
        r"hereby\s+(?:agree|covenant|represent)",
        r"governing\s+law",
        # Litigation
        r"(?:plaintiff|defendant|respondent)",
        r"(?:COMPLAINT|MOTION|BRIEF|ORDER|JUDGMENT)",
        r"(?:UNITED\s+STATES\s+DISTRICT\s+COURT|SUPERIOR\s+COURT|CIRCUIT\s+COURT)",
        r"(?:Case|Civil\s+Action)\s+(?:No|Number)",
        r"(?:COMES?\s+NOW|RESPECTFULLY\s+SUBMITTED)",
        # Corporate
        r"(?:BYLAWS|ARTICLES\s+OF\s+INCORPORATION|CERTIFICATE\s+OF\s+INCORPORATION)",
        r"(?:BOARD\s+(?:OF\s+DIRECTORS|RESOLUTION))",
        r"(?:STOCKHOLDER|SHAREHOLDER)\s+(?:AGREEMENT|MEETING)",
        # Employment
        r"(?:EMPLOYMENT|SEPARATION|SEVERANCE)\s+AGREEMENT",
        r"(?:NON-COMPETE|NON-SOLICITATION|RESTRICTIVE\s+COVENANT)",
        # IP
        r"(?:PATENT|TRADEMARK|COPYRIGHT)\s+(?:APPLICATION|REGISTRATION)",
        r"(?:LICENSE|LICENSING)\s+AGREEMENT",
    ]

    chunking_strategy = "sections"

    query_templates = {
        # Core contract
        "parties": (
            "Who are the parties to this agreement? "
            "List each party with their role and any defined abbreviations."
        ),
        "key_terms": (
            "What are the key terms and conditions of this agreement? "
            "Include: effective date, term length, renewal provisions."
        ),
        "obligations": (
            "What are the key obligations of each party? "
            "Look for: {synonyms}. List obligations per party."
        ),
        "termination": (
            "What are the termination provisions? "
            "Look for: {synonyms}. Include conditions, notice periods, and consequences."
        ),
        "liability": (
            "What are the liability and indemnification provisions? "
            "Look for: {synonyms}. Include any caps or limitations."
        ),
        "governing_law": (
            "What is the governing law and dispute resolution mechanism? "
            "Look for: {synonyms}."
        ),
        # Litigation sub-sector
        "claims": (
            "What claims or causes of action are alleged? "
            "Look for: {synonyms}. "
            "List each claim with the legal basis and factual allegations."
        ),
        "relief_sought": (
            "What relief or remedies are being sought? "
            "Look for: {synonyms}. "
            "Include monetary damages, injunctive relief, and any specific demands."
        ),
        # Corporate sub-sector
        "governance_rights": (
            "What governance rights are established? "
            "Look for: {synonyms}. "
            "Include voting rights, board composition, consent requirements, and veto powers."
        ),
        "equity_terms": (
            "What are the equity or stock-related terms? "
            "Look for: {synonyms}. "
            "Include share classes, vesting, exercise price, and any transfer restrictions."
        ),
        # Employment sub-sector
        "restrictive_covenants": (
            "What restrictive covenants apply? "
            "Look for: {synonyms}. "
            "Include non-compete scope (geography, duration), non-solicitation, and IP assignment."
        ),
        # IP sub-sector
        "ip_rights": (
            "What intellectual property rights are addressed? "
            "Look for: {synonyms}. "
            "Include scope of license/assignment, field of use, and any retained rights."
        ),
    }

    def _filename_keywords(self):
        return [
            # Contracts
            "contract", "agreement", "nda", "lease", "license",
            "amendment", "addendum", "legal", "msa",
            # Litigation
            "complaint", "motion", "brief", "order", "judgment",
            "court", "filing", "docket", "discovery",
            # Corporate
            "bylaws", "charter", "resolution", "proxy",
            "shareholder", "stockholder", "incorporation",
            # Employment
            "employment", "offer", "severance", "separation",
            "non-compete", "noncompete",
            # IP
            "patent", "trademark", "copyright", "ip",
        ]
