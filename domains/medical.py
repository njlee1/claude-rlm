"""
Medical domain plugin for RLM document analysis.

Covers the FULL spectrum of healthcare and life sciences:

Clinical / Patient Care: discharge summaries, progress notes, H&Ps, op notes
Pharmacology / Drug Development: FDA labels, package inserts, NDA submissions
Clinical Trials: protocols, informed consent, CSRs (clinical study reports)
Medical Devices: 510(k) submissions, PMA applications, device labeling
Health Insurance / Billing: EOBs, claims, prior auth, CPT/ICD coding
Public Health: epidemiological reports, surveillance data, CDC/WHO guidelines
Pathology / Radiology: path reports, radiology reads, cytology reports
Nursing / Allied Health: nursing assessments, PT/OT notes, care plans

The synonym expansion is critical because a "heart attack" is documented
as "myocardial infarction" in the medical record, coded as "I21.9" in
billing, called "acute MI" in radiology, and "STEMI" in the ED — all
the same event, completely different terms.
"""

from .base import BaseDomain


class MedicalDomain(BaseDomain):
    """Medical domain: clinical, pharma, trials, devices, billing, public health."""

    name = "medical"
    description = (
        "Medical document analysis (clinical records, pharma, clinical trials, "
        "devices, billing/coding, public health)"
    )

    synonyms = {
        # === Clinical / Patient Care ===
        "diagnosis": [
            "diagnosis", "diagnoses", "condition", "disorder",
            "disease", "pathology", "clinical finding", "impression",
            "assessment", "presenting complaint", "chief complaint",
            "differential diagnosis", "primary diagnosis",
            "principal diagnosis", "admitting diagnosis",
            "comorbidity", "comorbidities", "secondary diagnosis",
            "etiology", "sequela", "chronic condition",
        ],
        "treatment": [
            "treatment", "therapy", "intervention", "procedure",
            "medication", "drug", "regimen", "protocol",
            "therapeutic", "management", "treatment plan",
            "course of treatment", "standard of care",
            "surgical procedure", "operation", "surgery",
            "radiation therapy", "chemotherapy", "immunotherapy",
            "physical therapy", "rehabilitation",
        ],
        "dosage": [
            "dosage", "dose", "mg", "milligrams",
            "units", "IU", "mcg", "micrograms",
            "daily dose", "maximum dose", "recommended dose",
            "titration", "loading dose", "maintenance dose",
            "route of administration", "oral", "IV", "intravenous",
            "subcutaneous", "intramuscular", "topical", "inhaled",
            "PRN", "BID", "TID", "QID", "QD",
        ],
        "adverse_effects": [
            "adverse effect", "adverse event", "side effect",
            "adverse reaction", "complication", "contraindication",
            "warning", "precaution", "black box warning",
            "drug interaction", "toxicity",
            "serious adverse event", "SAE", "SUSAR",
            "adverse drug reaction", "ADR",
            "dose-limiting toxicity", "DLT",
            "withdrawal", "discontinuation",
        ],
        "lab_results": [
            "lab result", "laboratory", "test result", "blood work",
            "CBC", "complete blood count", "metabolic panel",
            "hemoglobin", "A1C", "creatinine", "BUN",
            "liver function", "lipid panel", "urinalysis",
            "troponin", "BNP", "procalcitonin", "D-dimer",
            "blood culture", "sensitivity", "MIC",
            "pathology report", "biopsy", "cytology",
            "tumor markers", "PSA", "CEA", "CA-125",
        ],
        "vital_signs": [
            "vital signs", "blood pressure", "heart rate",
            "temperature", "respiratory rate", "oxygen saturation",
            "SpO2", "BMI", "body mass index", "weight", "height",
            "pulse", "BP", "MAP", "mean arterial pressure",
            "Glasgow coma scale", "GCS", "pain scale",
        ],
        "patient_history": [
            "history", "medical history", "past medical history",
            "family history", "social history", "surgical history",
            "PMH", "HPI", "history of present illness",
            "review of systems", "ROS", "allergies",
            "medication list", "medication reconciliation",
            "immunization history", "travel history",
        ],
        "prognosis": [
            "prognosis", "outcome", "survival rate", "mortality",
            "morbidity", "recurrence", "remission", "relapse",
            "life expectancy", "five-year survival", "progression",
            "overall survival", "OS", "progression-free survival", "PFS",
            "disease-free survival", "DFS", "objective response rate", "ORR",
            "complete response", "CR", "partial response", "PR",
        ],
        # === Pharmacology / Drug Development ===
        "drug_info": [
            "indication", "indications and usage",
            "mechanism of action", "pharmacokinetics", "pharmacodynamics",
            "half-life", "bioavailability", "clearance",
            "drug class", "therapeutic class",
            "generic name", "brand name", "active ingredient",
            "excipient", "formulation", "strength",
            "NDC", "national drug code",
            "FDA approved", "approval date", "NDA", "ANDA", "BLA",
        ],
        "clinical_trial": [
            "clinical trial", "phase I", "phase II", "phase III", "phase IV",
            "randomized", "double-blind", "placebo-controlled",
            "open-label", "crossover", "parallel group",
            "primary endpoint", "secondary endpoint",
            "inclusion criteria", "exclusion criteria",
            "informed consent", "IRB", "institutional review board",
            "protocol", "study design", "sample size",
            "intent to treat", "ITT", "per protocol", "PP",
            "data safety monitoring board", "DSMB",
            "clinical study report", "CSR",
        ],
        # === Medical Devices ===
        "device": [
            "medical device", "device classification",
            "510(k)", "premarket notification",
            "PMA", "premarket approval",
            "predicate device", "substantial equivalence",
            "device labeling", "IFU", "instructions for use",
            "biocompatibility", "sterilization",
            "recall", "MDR", "medical device report",
        ],
        # === Health Insurance / Billing ===
        "billing": [
            "CPT", "current procedural terminology",
            "ICD-10-CM", "ICD-10-PCS", "diagnosis code",
            "procedure code", "DRG", "diagnosis related group",
            "EOB", "explanation of benefits",
            "prior authorization", "preauthorization",
            "medical necessity", "covered service",
            "allowed amount", "copay", "coinsurance", "deductible",
            "out-of-pocket", "maximum out-of-pocket",
            "claim", "claim denial", "appeal",
            "in-network", "out-of-network",
        ],
        # === Public Health / Epidemiology ===
        "epidemiology": [
            "incidence", "prevalence", "mortality rate",
            "case fatality rate", "CFR", "attack rate",
            "reproductive number", "R0", "Rt",
            "outbreak", "epidemic", "pandemic", "endemic",
            "surveillance", "contact tracing", "quarantine",
            "vaccine", "vaccination", "immunization",
            "efficacy", "effectiveness", "NNT",
            "risk factor", "odds ratio", "relative risk",
            "confidence interval", "CI", "p-value",
        ],
    }

    document_patterns = [
        # Clinical
        r"PATIENT",
        r"DIAGNOSIS|DIAGNOSES",
        r"ICD-(?:10|11)",
        r"PRESCRIPTION|Rx",
        r"(?:chief|presenting)\s+complaint",
        r"(?:vital\s+signs|blood\s+pressure|heart\s+rate)",
        r"(?:medical|surgical|family)\s+history",
        # Pharma / Drug labels
        r"DOSAGE\s+AND\s+ADMINISTRATION",
        r"(?:adverse|side)\s+(?:effect|event|reaction)",
        r"(?:INDICATIONS?\s+AND\s+USAGE|CONTRAINDICATIONS?)",
        r"(?:WARNINGS?\s+AND\s+PRECAUTIONS?|BLACK\s+BOX)",
        r"(?:NDC|NDA|ANDA|BLA)\s*(?:No|Number|#)?",
        # Clinical Trials
        r"(?:clinical|randomized|double-blind)\s+(?:trial|study)",
        r"(?:Phase\s+[I1][I2]?[I3]?[V4]?|PHASE\s+\d)",
        r"(?:primary|secondary)\s+endpoint",
        r"(?:inclusion|exclusion)\s+criteria",
        r"(?:informed\s+consent|IRB\s+approv)",
        # Medical Devices
        r"510\(k\)|(?:PREMARKET|PMA)\s+(?:NOTIFICATION|APPROVAL)",
        r"(?:PREDICATE|SUBSTANTIAL\s+EQUIVALENCE)",
        # Billing
        r"(?:CPT|DRG|HCPCS)\s+(?:code|#)",
        r"EXPLANATION\s+OF\s+BENEFITS",
        # Public Health
        r"(?:INCIDENCE|PREVALENCE|MORTALITY)\s+RATE",
        r"(?:OUTBREAK|EPIDEMIC|PANDEMIC)\s+(?:REPORT|INVESTIGATION)",
    ]

    chunking_strategy = "sections"

    query_templates = {
        # Clinical
        "diagnoses": (
            "What diagnoses or conditions are documented? "
            "Look for: {synonyms}. "
            "List each diagnosis with any associated codes (ICD-10)."
        ),
        "medications": (
            "What medications or treatments are prescribed or discussed? "
            "Look for: {synonyms}. "
            "Include dosage, frequency, and route of administration."
        ),
        "lab_results": (
            "What laboratory results are reported? "
            "Look for: {synonyms}. "
            "List each test with its value, units, and reference range if given."
        ),
        "adverse_effects": (
            "What adverse effects, complications, or warnings are mentioned? "
            "Look for: {synonyms}. "
            "Include severity and frequency if available."
        ),
        "vital_signs": (
            "What vital signs are recorded? "
            "Look for: {synonyms}. "
            "Report each measurement with its value and units."
        ),
        "treatment_plan": (
            "What is the treatment plan or recommended course of action? "
            "Look for: {synonyms}. "
            "Include follow-up instructions and monitoring requirements."
        ),
        # Pharma / Drug Development sub-sector
        "drug_label": (
            "What are the key sections of this drug label? "
            "Look for: {synonyms}. "
            "Extract indications, dosage, contraindications, and black box warnings."
        ),
        "trial_design": (
            "What is the clinical trial design and endpoints? "
            "Look for: {synonyms}. "
            "Include phase, design (randomized/blinded), primary/secondary endpoints, "
            "and inclusion/exclusion criteria."
        ),
        "trial_results": (
            "What are the clinical trial results? "
            "Look for: {synonyms}. "
            "Include efficacy outcomes, safety data, and statistical significance."
        ),
        # Billing sub-sector
        "coding": (
            "What diagnosis and procedure codes are used? "
            "Look for: {synonyms}. "
            "List ICD-10, CPT, and DRG codes with their descriptions."
        ),
        # Public Health sub-sector
        "epi_data": (
            "What epidemiological data is reported? "
            "Look for: {synonyms}. "
            "Include incidence, prevalence, mortality rates, and risk factors."
        ),
    }

    def _filename_keywords(self):
        return [
            # Clinical
            "patient", "clinical", "medical", "diagnosis",
            "prescription", "drug", "label", "guideline",
            "discharge", "progress", "operative",
            # Pharma / Trials
            "trial", "study", "protocol", "csr",
            "nda", "anda", "bla", "fda",
            "phase", "randomized",
            # Devices
            "510k", "pma", "device", "premarket",
            # Billing
            "eob", "claim", "cpt", "icd",
            "prior-auth", "billing",
            # Public Health
            "outbreak", "surveillance", "epidemiology",
            "cdc", "who", "vaccine",
        ]
