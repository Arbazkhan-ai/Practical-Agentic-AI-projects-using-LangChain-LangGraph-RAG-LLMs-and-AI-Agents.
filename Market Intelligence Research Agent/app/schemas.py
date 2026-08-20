"""
Pydantic schemas for the Research Intelligence Agent.
Enforces rigorous source metadata, denominator preservation, 6-tier quality classification,
and cross-market comparability flags.
"""

from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field


class ResearchBrief(BaseModel):
    title: str = Field(description="Research title or topic")
    objective: str = Field(description="Research objective and decision to support")
    questions: List[str] = Field(description="Specific research questions")
    geography: Optional[List[str]] = Field(default=None, description="Target markets/geographies")
    used_caribbean_default: bool = Field(default=False, description="Whether Caribbean fallback was applied")
    date_range: Optional[str] = Field(default="2015-2025", description="Target historical date range")
    report_language: str = Field(default="English", description="Language of the final report")
    priority_themes: Optional[str] = Field(default=None, description="Priority focus areas")
    instructions: Optional[str] = Field(default=None, description="Additional custom instructions")


class SearchQueries(BaseModel):
    en: List[str] = Field(default_factory=list, description="English search queries")
    fr: List[str] = Field(default_factory=list, description="French search queries")
    es: List[str] = Field(default_factory=list, description="Spanish search queries")
    nl: List[str] = Field(default_factory=list, description="Dutch search queries")


class ResearchPlan(BaseModel):
    research_objective: str = Field(description="Core objective restatement")
    key_research_angles: List[str] = Field(default_factory=list, description="Primary investigative angles")
    sub_questions: List[str] = Field(default_factory=list, description="Decomposed research questions")
    markets: List[str] = Field(default_factory=list, description="Markets in scope")
    date_range: str = Field(default="2015-2025", description="Scope time window")
    required_metrics: List[str] = Field(default_factory=list, description="Quantitative indicators required")
    key_concepts: List[str] = Field(default_factory=list, description="Core thematic concepts")
    search_queries: Dict[str, List[str]] = Field(default_factory=dict, description="Multilingual query lists")
    preferred_source_types: List[str] = Field(default_factory=list, description="Preferred source channels")
    priority_domains: List[str] = Field(default_factory=list, description="Authoritative domains targeted")
    required_evidence: List[str] = Field(default_factory=list, description="Required evidence standards")
    expected_comparisons: List[str] = Field(default_factory=list, description="Expected market comparisons")
    search_languages: List[str] = Field(default_factory=list, description="Languages to query")


class SourceRecord(BaseModel):
    id: str
    run_id: str
    project_id: str
    title: Optional[str] = None
    url: str
    publisher: Optional[str] = None
    source_type: str = "web"
    tier: int = Field(default=5, description="Source tier from 1 (Multilateral) to 6 (Social/Informal)")
    institution_category: Optional[str] = Field(
        default="General Web",
        description="Multilateral, National Statistical Office, Academic, Corporate Case Study, Trade Media, Social Media"
    )
    document_type: str = Field(
        default="web_article",
        description="institutional_pdf, national_bulletin, academic_study, corporate_case_study, statistical_api, web_article, social_media"
    )
    publication_date: Optional[str] = Field(default=None, description="Actual publication date (YYYY-MM-DD or YYYY-MM) or date_unspecified")
    page_count: Optional[int] = Field(default=None, description="Document page count for PDFs only; null for HTML/web")
    content_format: str = Field(default="html", description="pdf, html, api_json")
    language: Optional[str] = "en"
    domain: Optional[str] = None


class SourceContentRecord(BaseModel):
    source_id: str
    run_id: str
    project_id: str
    content: Optional[str] = None
    char_count: int = 0
    content_type: str = "html"
    extract_ok: bool = True
    extract_error: Optional[str] = None
    pdf_filename: Optional[str] = None
    extracted_page: Optional[str] = None


class FindingExtractionItem(BaseModel):
    claim: str = Field(description="One-sentence factual statement strictly grounded in text")
    claim_type: Literal["sourced_fact", "eclectik_derived_calculation", "ai_interpretation"] = Field(
        default="sourced_fact",
        description="Distinguishes sourced facts from Eclectik-derived calculations and AI interpretation"
    )
    metric: Optional[str] = Field(default=None, description="Name of the measure")
    value: Optional[float] = Field(default=None, description="Clean numeric value")
    unit: Optional[str] = Field(default=None, description="Unit or currency")
    denominator_definition: Optional[str] = Field(
        default=None,
        description="Exact measurement base or denominator (e.g., % of hotel F&B spend, % of gross imports, daily spend/tourist)"
    )
    market: Optional[str] = Field(default=None, description="Country/market")
    period: Optional[str] = Field(default=None, description="Exact observation year or range (e.g., 2023, 2018-2024)")
    confidence: Literal["high", "medium", "low"] = Field(default="medium", description="Evidence confidence")
    quote: str = Field(description="Verbatim excerpt from source text preserving exact wording")
    location_hint: Optional[str] = Field(default=None, description="Exact page, table, cuadro, or section (e.g. Page 52, Table 4.3)")


class ExtractedFindingsResponse(BaseModel):
    findings: List[FindingExtractionItem] = Field(default_factory=list)


class FindingRecord(BaseModel):
    id: str
    run_id: str
    project_id: str
    source_id: Optional[str] = None
    claim_type: Literal["sourced_fact", "eclectik_derived_calculation", "ai_interpretation"] = "sourced_fact"
    claim: str
    metric: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    denominator_definition: Optional[str] = None
    geography: Optional[str] = None
    time_period: Optional[str] = None
    confidence: Optional[str] = None
    evidence_text: Optional[str] = None
    page_section: Optional[str] = None
    citation_url: Optional[str] = None
    source_tier: Optional[int] = 5
    source_publisher: Optional[str] = None
    document_type: Optional[str] = None
    publication_date: Optional[str] = None


class ValidationVerdictRecord(BaseModel):
    finding_id: str
    run_id: str
    project_id: str
    source_id: Optional[str] = None
    validation_status: Literal["pass", "warn", "fail"]
    metadata_status: Literal["pass", "warn", "fail"] = "pass"
    grounding_status: Literal["pass", "warn", "fail"] = "pass"
    comparability_status: Literal["pass", "divergent_flagged"] = "pass"
    denominator_preserved: bool = True
    calculation_valid: Optional[bool] = None
    issue_codes: Optional[str] = None
    issues: Optional[str] = None
    support_score: Optional[float] = None
    support_verdict: Optional[Literal["supported", "partial", "unsupported"]] = None
    duplicate_of: Optional[str] = None


class TimeSeriesPoint(BaseModel):
    year: int
    value: float
    unit: Optional[str] = None
    finding_id: str


class TrendRecord(BaseModel):
    metric: str
    geography: str
    from_year: int
    to_year: int
    from_value: float
    to_value: float
    unit: Optional[str] = None
    absolute_change: float
    pct_change: Optional[float] = None
    direction: Literal["increasing", "decreasing", "stable"]
    claim_type: Literal["eclectik_derived_calculation"] = "eclectik_derived_calculation"
    points: int
    series: List[TimeSeriesPoint]


class MarketComparisonRow(BaseModel):
    geography: str
    value: float
    unit: Optional[str] = None
    period: Optional[str] = None
    denominator_definition: Optional[str] = None
    finding_id: str
    source: Optional[str] = None
    tier: Optional[int] = None
    comparability_note: Optional[str] = None


class MarketComparisonRecord(BaseModel):
    metric: str
    unit_consistent: bool
    comparability_flag: Literal["directly_comparable", "methodology_divergent", "proxy_comparison", "not_directly_comparable"] = "directly_comparable"
    divergence_notes: Optional[str] = None
    highest: MarketComparisonRow
    lowest: MarketComparisonRow
    spread: float
    markets_compared: int
    values: List[MarketComparisonRow]


class ConflictRecord(BaseModel):
    metric: str
    geography: str
    period: Optional[str] = None
    conflict_type: str
    min_value: float
    max_value: float
    relative_spread: float
    entries: List[Dict[str, Any]]


class AnalysisBundle(BaseModel):
    trends: List[TrendRecord] = Field(default_factory=list)
    comparisons: List[MarketComparisonRecord] = Field(default_factory=list)
    year_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    metric_coverage_gaps: List[str] = Field(default_factory=list)
    market_coverage_gaps: List[str] = Field(default_factory=list)
    conflicts: List[ConflictRecord] = Field(default_factory=list)
    counts: Dict[str, int] = Field(default_factory=dict)


class AnalysisNarrative(BaseModel):
    trends_narrative: str
    comparisons_narrative: str
    gaps_narrative: str
    conflicts_narrative: str
    overall_interpretation: str
