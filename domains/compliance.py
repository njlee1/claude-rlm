"""
Compliance / regulatory domain plugin for RLM document analysis.

Covers the FULL spectrum of compliance and regulatory frameworks:

Financial Compliance: SOX, SEC reporting, Dodd-Frank, Basel III/IV, AML/KYC/BSA
Data Privacy: GDPR, CCPA/CPRA, PIPL, data processing agreements (DPAs)
Healthcare Compliance: HIPAA, HITECH, Stark Law, Anti-Kickback, CMS regulations
Information Security: ISO 27001, NIST 800-53, SOC 1/2, PCI DSS, CMMC, CSA STAR
Industry-Specific: FINRA, FDIC, OCC, NRC, EPA, OSHA, FDA, FTC
Corporate Governance: board oversight, risk committees, whistleblower programs
ESG / Sustainability: climate disclosures, ESG reporting, TCFD, SASB, GRI
Third-Party Risk: vendor assessments, supply chain audits, SIG questionnaires

Built from the perspective of compliance officers, internal auditors, and
GRC analysts who face an ever-expanding regulatory landscape. 2/3 of compliance
officers say demands exceed available hours.

The RLM approach is powerful because compliance documents require MULTI-HOP
EXTRACTION: regulation -> control -> evidence -> finding -> remediation. This
chain of cross-references is exactly what Algorithm 1's iterative loop handles.
"""

from .base import BaseDomain


class ComplianceDomain(BaseDomain):
    """Compliance domain: financial, privacy, healthcare, infosec, ESG, third-party."""

    name = "compliance"
    description = (
        "Compliance & regulatory analysis (SOX, GDPR, HIPAA, PCI DSS, "
        "AML/KYC, ESG, third-party risk, industry-specific)"
    )

    synonyms = {
        # === Core Compliance Concepts ===
        "requirement": [
            "requirement", "obligation", "mandate", "regulation",
            "regulatory requirement", "statutory requirement",
            "standard", "rule", "provision", "directive",
            "shall", "must", "is required to",
            "control requirement", "compliance obligation",
            "regulatory expectation", "binding requirement",
        ],
        "control": [
            "control", "internal control", "control activity",
            "safeguard", "measure", "mechanism", "procedure",
            "control objective", "key control", "compensating control",
            "preventive control", "detective control", "corrective control",
            "ITGC", "IT general control", "application control",
            "automated control", "manual control",
            "entity-level control", "process-level control",
            "monitoring control", "access control",
        ],
        "finding": [
            "finding", "observation", "deficiency",
            "material weakness", "significant deficiency",
            "non-compliance", "noncompliance", "exception",
            "gap", "issue", "deviation", "discrepancy",
            "audit finding", "reportable condition",
            "control failure", "weakness",
            "violation", "infraction", "breach",
            "consent order", "enforcement action",
        ],
        "risk": [
            "risk", "risk factor", "threat", "vulnerability",
            "risk level", "risk rating", "inherent risk",
            "residual risk", "risk appetite", "risk tolerance",
            "high risk", "medium risk", "low risk", "critical risk",
            "likelihood", "impact", "probability", "consequence",
            "risk scenario", "key risk indicator", "KRI",
            "emerging risk", "systemic risk",
        ],
        "remediation": [
            "remediation", "corrective action", "action plan",
            "management response", "management action plan",
            "mitigation", "resolution", "fix", "improvement",
            "remediation plan", "corrective action plan", "CAP",
            "target date", "due date", "completion date",
            "remediation owner", "action item",
            "root cause analysis", "preventive action",
        ],
        "assessment": [
            "assessment", "evaluation", "review", "examination",
            "audit", "inspection", "test", "testing",
            "gap analysis", "risk assessment", "control assessment",
            "self-assessment", "independent assessment",
            "walkthrough", "inquiry", "observation", "re-performance",
            "maturity assessment", "readiness assessment",
        ],
        "evidence": [
            "evidence", "documentation", "artifact",
            "supporting documentation", "audit evidence",
            "test results", "sample", "screenshot",
            "log", "record", "proof", "attestation",
            "certificate", "report", "exhibit",
            "audit trail", "chain of custody",
        ],
        "framework": [
            "SOX", "Sarbanes-Oxley", "Section 302", "Section 404",
            "GDPR", "General Data Protection",
            "HIPAA", "Health Insurance Portability",
            "PCI DSS", "PCI", "ISO 27001", "ISO 27002",
            "NIST", "NIST 800-53", "NIST CSF",
            "COBIT", "COSO", "SOC 2", "SOC 1",
            "CCPA", "CPRA", "FERPA", "FISMA",
            "FedRAMP", "CMMC", "CSA STAR", "HITRUST",
            "CIS Controls", "OWASP",
        ],
        "policy": [
            "policy", "procedure", "standard", "guideline",
            "policy document", "policy manual", "SOP",
            "standard operating procedure", "governance",
            "information security policy", "acceptable use",
            "data classification", "data retention",
            "incident response plan", "business continuity plan",
            "disaster recovery plan",
        ],
        "scope": [
            "scope", "in scope", "out of scope",
            "applicability", "covered entity",
            "data subject", "processing activity",
            "system boundary", "audit scope",
            "scope of assessment", "assessment boundary",
            "audit period", "reporting period",
        ],
        # === Financial Compliance ===
        "financial_compliance": [
            "ICFR", "internal control over financial reporting",
            "Section 302 certification", "Section 404 assessment",
            "management assertion", "auditor attestation",
            "Dodd-Frank", "Basel III", "Basel IV",
            "capital adequacy", "liquidity coverage ratio",
            "stress test", "CCAR", "DFAST",
            "SEC reporting", "Regulation S-K", "Regulation S-X",
            "material misstatement", "restatement",
            "whistleblower", "clawback", "insider trading",
        ],
        # === AML / KYC / BSA ===
        "aml_kyc": [
            "anti-money laundering", "AML", "know your customer", "KYC",
            "Bank Secrecy Act", "BSA", "suspicious activity report", "SAR",
            "currency transaction report", "CTR",
            "customer due diligence", "CDD", "enhanced due diligence", "EDD",
            "beneficial ownership", "politically exposed person", "PEP",
            "sanctions", "OFAC", "SDN list",
            "transaction monitoring", "unusual activity",
            "structuring", "smurfing", "layering",
        ],
        # === Data Privacy ===
        "data_privacy": [
            "personal data", "PII", "personally identifiable information",
            "data subject rights", "right to access", "right to erasure",
            "right to be forgotten", "data portability",
            "consent", "legitimate interest", "legal basis",
            "data processing agreement", "DPA",
            "data protection impact assessment", "DPIA",
            "data breach", "breach notification",
            "data controller", "data processor",
            "cross-border transfer", "standard contractual clauses", "SCC",
            "privacy by design", "privacy impact assessment",
            "cookie consent", "opt-in", "opt-out",
        ],
        # === Healthcare Compliance ===
        "healthcare_compliance": [
            "protected health information", "PHI", "ePHI",
            "covered entity", "business associate",
            "business associate agreement", "BAA",
            "minimum necessary", "de-identification",
            "HITECH", "Stark Law", "Anti-Kickback Statute",
            "CMS", "Medicare", "Medicaid",
            "false claims", "qui tam", "OIG",
            "meaningful use", "interoperability",
            "21st Century Cures Act",
        ],
        # === Information Security ===
        "infosec": [
            "vulnerability assessment", "penetration test", "pentest",
            "security incident", "data breach", "cyber attack",
            "access management", "identity management", "IAM",
            "multi-factor authentication", "MFA", "SSO",
            "encryption", "at rest", "in transit",
            "firewall", "IDS", "IPS", "SIEM",
            "patch management", "configuration management",
            "business continuity", "disaster recovery",
            "RTO", "RPO", "BIA",
            "security awareness training",
        ],
        # === ESG / Sustainability ===
        "esg": [
            "ESG", "environmental social governance",
            "sustainability", "sustainability report",
            "climate risk", "carbon emissions", "greenhouse gas", "GHG",
            "Scope 1", "Scope 2", "Scope 3",
            "TCFD", "Task Force on Climate-related Financial Disclosures",
            "SASB", "GRI", "Global Reporting Initiative",
            "CDP", "climate disclosure",
            "DEI", "diversity equity inclusion",
            "social impact", "community engagement",
            "ESG rating", "ESG score", "materiality assessment",
            "net zero", "science-based targets", "SBTi",
        ],
        # === Third-Party Risk ===
        "third_party": [
            "vendor", "third party", "third-party risk",
            "vendor risk assessment", "vendor due diligence",
            "supply chain risk", "subcontractor",
            "SIG", "standardized information gathering",
            "CAIQ", "Consensus Assessments Initiative",
            "vendor management", "vendor onboarding",
            "fourth-party risk", "concentration risk",
            "right to audit", "service level agreement", "SLA",
            "business continuity plan", "subservice organization",
        ],
    }

    document_patterns = [
        # Core compliance
        r"(?:AUDIT|COMPLIANCE|ASSESSMENT)\s+REPORT",
        r"(?:INTERNAL\s+)?CONTROL(?:S|\s+ENVIRONMENT)",
        r"(?:FINDING|OBSERVATION|DEFICIENCY)",
        r"(?:REMEDIATION|CORRECTIVE\s+ACTION)\s+PLAN",
        r"(?:RISK\s+)?(?:ASSESSMENT|REGISTER|MATRIX)",
        r"(?:MATERIAL\s+WEAKNESS|SIGNIFICANT\s+DEFICIENCY)",
        r"(?:MANAGEMENT|AUDITOR).S?\s+(?:RESPONSE|OPINION|REPORT)",
        r"CONTROL\s+(?:OBJECTIVE|ACTIVITY|TEST)",
        r"(?:SCOPE|APPLICABILITY|COVERED\s+ENTITY)",
        r"(?:POLICY|PROCEDURE|GOVERNANCE)\s+(?:DOCUMENT|MANUAL|FRAMEWORK)",
        r"(?:EVIDENCE|ARTIFACT|ATTESTATION)",
        # Frameworks
        r"(?:SOX|SARBANES|GDPR|HIPAA|PCI\s*DSS|ISO\s*27001|NIST|SOC\s*[12])",
        r"(?:CCPA|CPRA|FERPA|FISMA|FedRAMP|CMMC|HITRUST|CIS)",
        # Financial compliance
        r"(?:ICFR|SECTION\s+(?:302|404))",
        r"(?:DODD.FRANK|BASEL\s+[IV]+)",
        # AML / KYC
        r"(?:AML|KYC|BSA|ANTI.MONEY\s+LAUNDERING)",
        r"(?:SAR|CTR|OFAC|SDN)",
        # Data Privacy
        r"(?:DATA\s+PROTECTION|PRIVACY\s+(?:POLICY|IMPACT|NOTICE))",
        r"(?:DATA\s+(?:SUBJECT|CONTROLLER|PROCESSOR|BREACH))",
        r"(?:DPIA|DPA|SCC|STANDARD\s+CONTRACTUAL)",
        # Healthcare
        r"(?:PHI|ePHI|BUSINESS\s+ASSOCIATE)",
        r"(?:HITECH|STARK\s+LAW|ANTI.KICKBACK)",
        # ESG
        r"(?:ESG|SUSTAINABILITY|TCFD|SASB|GRI)",
        r"(?:GREENHOUSE\s+GAS|CARBON|SCOPE\s+[123])",
        # Third-party
        r"(?:VENDOR\s+(?:RISK|ASSESSMENT|MANAGEMENT))",
        r"(?:SIG|CAIQ|THIRD.PARTY\s+RISK)",
    ]

    chunking_strategy = "sections"

    query_templates = {
        # Core compliance
        "findings": (
            "What findings, deficiencies, or observations were identified? "
            "Look for: {synonyms}. "
            "List each finding with its severity, description, affected control, and status."
        ),
        "controls": (
            "What controls are documented or tested? "
            "Look for: {synonyms}. "
            "List each control with its objective, type (preventive/detective), and test result."
        ),
        "requirements": (
            "What regulatory requirements or standards are referenced? "
            "Look for: {synonyms}. "
            "List each requirement with the applicable framework and section."
        ),
        "remediation": (
            "What remediation or corrective actions are planned? "
            "Look for: {synonyms}. "
            "Include responsible party, target date, and current status."
        ),
        "risk_assessment": (
            "What risks are identified and how are they rated? "
            "Look for: {synonyms}. "
            "Include risk description, likelihood, impact, and risk level."
        ),
        "scope": (
            "What is the scope of this assessment or audit? "
            "Look for: {synonyms}. "
            "Include systems, processes, time period, and frameworks covered."
        ),
        "evidence": (
            "What evidence or documentation is referenced? "
            "Look for: {synonyms}. "
            "List each piece of evidence with what control or finding it supports."
        ),
        # Financial compliance sub-sector
        "sox_assessment": (
            "What is the SOX / ICFR assessment status? "
            "Look for: {synonyms}. "
            "Include management assertion, material weaknesses, and auditor opinion."
        ),
        # AML / KYC sub-sector
        "aml_findings": (
            "What AML/KYC findings or suspicious activity is documented? "
            "Look for: {synonyms}. "
            "Include SARs filed, transaction monitoring results, and CDD gaps."
        ),
        # Data Privacy sub-sector
        "privacy_assessment": (
            "What data privacy compliance status is reported? "
            "Look for: {synonyms}. "
            "Include data processing activities, legal bases, DPIA findings, and breach history."
        ),
        # ESG sub-sector
        "esg_disclosure": (
            "What ESG or sustainability metrics are disclosed? "
            "Look for: {synonyms}. "
            "Include emissions (Scope 1/2/3), targets, DEI metrics, and framework alignment."
        ),
        # Third-party risk sub-sector
        "vendor_risk": (
            "What third-party or vendor risks are assessed? "
            "Look for: {synonyms}. "
            "Include vendor tier, risk rating, SLA compliance, and any identified concerns."
        ),
    }

    def _filename_keywords(self):
        return [
            # Core
            "audit", "compliance", "assessment", "governance",
            "regulatory", "control", "finding", "remediation",
            # Frameworks
            "sox", "gdpr", "hipaa", "pci", "nist", "iso",
            "soc", "soc2", "soc1", "fedramp", "cmmc", "hitrust",
            # Financial
            "icfr", "dodd-frank", "basel",
            # AML
            "aml", "kyc", "bsa", "sar", "ofac",
            # Privacy
            "privacy", "dpa", "dpia", "ccpa", "cpra",
            "data protection", "breach notification",
            # Healthcare
            "phi", "baa", "hitech",
            # ESG
            "esg", "sustainability", "tcfd", "sasb", "gri",
            "carbon", "climate",
            # Third-party
            "vendor", "third-party", "sig", "caiq",
            "supply chain",
        ]
