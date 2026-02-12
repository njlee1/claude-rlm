"""
Academic domain plugin for RLM document analysis.

Covers the FULL spectrum of academic and research documents:

STEM Research: CS/ML papers, physics, chemistry, biology, engineering, math
Social Sciences: psychology, economics, sociology, political science
Humanities: history, philosophy, literary criticism, cultural studies
Grant Proposals / Funding: NSF, NIH, ERC proposals, progress reports
Systematic Reviews / Meta-Analysis: Cochrane reviews, PRISMA, forest plots
Theses / Dissertations: undergraduate, master's, doctoral
Technical Reports: whitepapers, standards documents, RFCs
Conference / Workshop: proceedings, extended abstracts, poster papers

The synonym expansion matters because each discipline has its own terminology.
A CS paper says "ablation study" while psychology says "factor analysis" and
economics says "robustness check" — all meaning "systematic tests to validate
the main result."
"""

from .base import BaseDomain


class AcademicDomain(BaseDomain):
    """Academic domain: STEM, social sciences, humanities, grants, reviews."""

    name = "academic"
    description = (
        "Academic document analysis (STEM, social sciences, humanities, "
        "grants, systematic reviews, theses)"
    )

    synonyms = {
        # === Core Research Structure ===
        "methodology": [
            "methodology", "methods", "method", "approach",
            "experimental setup", "experimental design",
            "study design", "research design", "procedure",
            "framework", "technique", "algorithm",
            # Social science
            "qualitative method", "quantitative method", "mixed methods",
            "survey design", "interview protocol", "ethnography",
            "grounded theory", "case study method", "content analysis",
            # STEM
            "computational method", "simulation", "numerical method",
            "analytical framework", "experimental protocol",
        ],
        "findings": [
            "findings", "results", "outcomes", "observations",
            "key findings", "main results", "experimental results",
            "empirical results", "quantitative results",
            # Social science
            "qualitative findings", "themes", "emergent themes",
            "survey results", "interview findings",
            # STEM
            "measurements", "simulation results",
            "experimental outcomes", "computational results",
        ],
        "conclusion": [
            "conclusion", "conclusions", "summary", "discussion",
            "implications", "contribution", "takeaways",
            "concluding remarks", "key takeaways",
            "practical implications", "theoretical implications",
            "policy implications", "future directions",
        ],
        "limitations": [
            "limitation", "limitations", "constraint", "constraints",
            "shortcoming", "weakness", "future work",
            "open question", "open problem", "caveat",
            "threat to validity", "threats to validity",
            "generalizability", "external validity", "internal validity",
            "construct validity", "ecological validity",
            "selection bias", "confounding", "endogeneity",
        ],
        "hypothesis": [
            "hypothesis", "hypotheses", "research question",
            "conjecture", "proposition", "thesis statement",
            "claim", "assertion", "prediction",
            "null hypothesis", "alternative hypothesis",
            "H0", "H1", "research objective",
        ],
        "dataset": [
            "dataset", "data set", "corpus", "benchmark",
            "training data", "test set", "evaluation set",
            "data source", "data collection", "sample",
            "participants", "subjects", "respondents",
            # Specific to disciplines
            "cohort", "panel data", "cross-sectional data",
            "longitudinal data", "time series",
            "survey sample", "convenience sample", "random sample",
            "stratified sample", "population",
        ],
        "metrics": [
            "accuracy", "precision", "recall", "F1",
            "AUC", "BLEU", "ROUGE", "perplexity",
            "baseline", "state of the art", "SOTA",
            "performance", "evaluation metric",
            # Statistics
            "p-value", "significance", "statistical significance",
            "confidence interval", "CI", "effect size",
            "Cohen's d", "r-squared", "R2", "adjusted R2",
            "chi-square", "t-test", "ANOVA", "regression",
            "correlation", "Pearson", "Spearman",
            "odds ratio", "hazard ratio", "relative risk",
        ],
        "prior_work": [
            "related work", "prior work", "previous work",
            "literature review", "background", "state of the art",
            "existing approaches", "prior research",
            "theoretical background", "theoretical framework",
            "conceptual framework", "literature gap",
        ],
        # === Grant Proposals / Funding ===
        "grant": [
            "specific aims", "research plan", "project description",
            "significance", "innovation", "approach",
            "budget", "budget justification", "personnel",
            "principal investigator", "PI", "co-PI",
            "funding period", "project period",
            "broader impacts", "intellectual merit",
            "preliminary data", "preliminary results",
            "NSF", "NIH", "ERC", "DOE", "DARPA",
            "R01", "R21", "R03", "K award", "F award",
        ],
        # === Systematic Review / Meta-Analysis ===
        "systematic_review": [
            "systematic review", "meta-analysis", "meta analysis",
            "PRISMA", "search strategy", "inclusion criteria",
            "exclusion criteria", "quality assessment",
            "risk of bias", "forest plot", "funnel plot",
            "heterogeneity", "I-squared", "I2",
            "pooled estimate", "fixed effects", "random effects",
            "publication bias", "sensitivity analysis",
            "Cochrane", "GRADE", "evidence quality",
        ],
        # === Reproducibility / Ethics ===
        "reproducibility": [
            "reproducibility", "replicability", "replication",
            "code availability", "data availability",
            "supplementary material", "appendix",
            "ethics approval", "IRB approval", "informed consent",
            "conflict of interest", "funding disclosure",
            "pre-registration", "registered report",
        ],
    }

    document_patterns = [
        # Universal academic
        r"Abstract",
        r"Introduction",
        r"Related\s+Work",
        r"(?:Methodology|Methods|Experimental\s+Setup)",
        r"(?:Results|Findings|Experiments)",
        r"(?:Conclusion|Discussion)",
        r"References|Bibliography",
        r"arXiv:\d+\.\d+",
        r"(?:et\s+al\.|doi:|DOI:)",
        r"(?:Table|Figure)\s+\d+",
        # Grant proposals
        r"(?:SPECIFIC\s+AIMS|RESEARCH\s+PLAN|PROJECT\s+DESCRIPTION)",
        r"(?:SIGNIFICANCE|INNOVATION|BROADER\s+IMPACTS)",
        r"(?:BUDGET\s+JUSTIFICATION|PERSONNEL)",
        # Systematic reviews
        r"(?:PRISMA|SYSTEMATIC\s+REVIEW|META-ANALYSIS)",
        r"(?:SEARCH\s+STRATEGY|INCLUSION\s+CRITERIA)",
        r"(?:RISK\s+OF\s+BIAS|FOREST\s+PLOT)",
        # Social science
        r"(?:SURVEY|QUESTIONNAIRE|INTERVIEW\s+PROTOCOL)",
        r"(?:QUALITATIVE|QUANTITATIVE|MIXED\s+METHODS)",
        # Thesis / Dissertation
        r"(?:DISSERTATION|THESIS)\s+(?:SUBMITTED|PRESENTED)",
        r"(?:COMMITTEE|ADVISOR|DEPARTMENT\s+OF)",
    ]

    chunking_strategy = "sections"

    query_templates = {
        # Core research
        "methodology": (
            "What methodology or approach does this paper use? "
            "Look for: {synonyms}. "
            "Describe the research design, data sources, and key techniques."
        ),
        "findings": (
            "What are the key findings or results? "
            "Look for: {synonyms}. "
            "List the main quantitative and qualitative results."
        ),
        "limitations": (
            "What limitations or weaknesses does the paper acknowledge? "
            "Look for: {synonyms}. "
            "Include any mentioned threats to validity."
        ),
        "contributions": (
            "What are the main contributions of this paper? "
            "Look for claims of novelty, improvements over baselines, "
            "and practical implications."
        ),
        "datasets": (
            "What datasets or benchmarks were used for evaluation? "
            "Look for: {synonyms}. "
            "Include size, source, and any preprocessing steps."
        ),
        # Grant proposals sub-sector
        "specific_aims": (
            "What are the specific aims or research objectives? "
            "Look for: {synonyms}. "
            "List each aim with its hypothesis and proposed approach."
        ),
        "significance": (
            "What is the significance and innovation of this research? "
            "Look for: {synonyms}. "
            "Include the knowledge gap, clinical relevance, and novelty claims."
        ),
        # Systematic review sub-sector
        "search_strategy": (
            "What was the systematic search strategy? "
            "Look for: {synonyms}. "
            "Include databases searched, search terms, date range, and filters."
        ),
        "pooled_results": (
            "What are the pooled/meta-analytic results? "
            "Look for: {synonyms}. "
            "Include pooled estimates, confidence intervals, heterogeneity, and quality."
        ),
        # Statistics sub-sector
        "statistical_analysis": (
            "What statistical methods were used and what do the results show? "
            "Look for: {synonyms}. "
            "Include test type, sample size, effect sizes, p-values, and CIs."
        ),
    }

    def _filename_keywords(self):
        return [
            # Core academic
            "paper", "thesis", "dissertation", "report",
            "arxiv", "conference", "journal", "proceedings",
            "research", "study", "survey", "review",
            # Grant proposals
            "proposal", "grant", "nsf", "nih", "specific aims",
            "r01", "r21",
            # Systematic reviews
            "systematic", "meta-analysis", "prisma", "cochrane",
            # Social science
            "qualitative", "quantitative", "mixed methods",
            # Technical
            "whitepaper", "rfc", "standard", "technical",
        ]
