"""
Pydantic schemas for the Research Intelligence Agent.
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
    tier: int = 5
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


class FindingExtractionItem(BaseModel):
    claim: str = Field(description="One-sentence factual statement strictly grounded in text")
    metric: Optional[str] = Field(default=None, description="Name of the measure")
    value: Optional[float] = Field(default=None, description="Clean numeric value")
    unit: Optional[str] = Field(default=None, description="Unit or currency")
    market: Optional[str] = Field(default=None, description="Country/market")
    period: Optional[str] = Field(default=None, description="Year or range")
    confidence: Literal["high", "medium", "low"] = Field(default="medium", description="Evidence confidence")
    quote: str = Field(description="Verbatim excerpt from source text")
    location_hint: Optional[str] = Field(default=None, description="Section or page")


class ExtractedFindingsResponse(BaseModel):
    findings: List[FindingExtractionItem] = Field(default_factory=list)


class FindingRecord(BaseModel):
    id: str
    run_id: str
    project_id: str
    source_id: Optional[str] = None
    claim: str
    metric: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    geography: Optional[str] = None
    time_period: Optional[str] = None
    confidence: Optional[str] = None
    evidence_text: Optional[str] = None
    page_section: Optional[str] = None
    citation_url: Optional[str] = None


class ValidationVerdictRecord(BaseModel):
    finding_id: str
    run_id: str
    project_id: str
    source_id: Optional[str] = None
    validation_status: Literal["pass", "warn", "fail"]
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
    points: int
    series: List[TimeSeriesPoint]


class MarketComparisonRow(BaseModel):
    geography: str
    value: float
    unit: Optional[str] = None
    period: Optional[str] = None
    finding_id: str
    source: Optional[str] = None


class MarketComparisonRecord(BaseModel):
    metric: str
    unit_consistent: bool
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
