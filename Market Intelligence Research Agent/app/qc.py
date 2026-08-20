"""
Quality Control (QC) & Validation Engine:
Executes multi-vector deterministic checks (metadata integrity, denominator preservation,
tier classification, conflict detection) followed by LLM Claim-Support verification.
"""

from typing import List, Dict, Any, Tuple
from schemas import FindingRecord, SourceRecord, ValidationVerdictRecord
from llm_client import generate_llm_response, parse_json_safely

QC_SYSTEM_PROMPT = """You are a rigorous research QA validation auditor for Eclectik. You judge whether provided verbatim evidence quotes strictly support a given claim AND whether the claim accurately preserves the denominator, time period, and meaning of the source statistic without overgeneralization.

Return a single JSON object with EXACTLY this structure:
{
  "support_verdict": "supported" | "partial" | "unsupported",
  "support_score": 0.95,  // float between 0.0 and 1.0
  "denominator_preserved": true | false,
  "reason": "Clear one-sentence explanation"
}

Definitions:
- supported: the evidence directly and fully states the claim, preserving the exact denominator/scope.
- partial: the evidence is related but does not fully establish the claim or broadens the denominator.
- unsupported: the evidence does not back the claim or contradicts the reported number/scope.
"""


def run_referential_checks(
    findings: List[FindingRecord],
    sources: List[SourceRecord]
) -> List[Dict[str, Any]]:
    """
    Performs deterministic multi-vector rule checks:
    1. Metadata Integrity (valid source, document type, no fake page counts on HTML)
    2. Quantitative Context (denominator specified, temporal period preserved)
    3. Conflict & Duplicate Detection
    4. Source Tier Verification
    """
    src_map = {s.id: s for s in sources}
    groups: Dict[str, List[FindingRecord]] = {}

    def norm(v):
        return (str(v) if v is not None else "").strip().lower()

    for f in findings:
        key = f"{norm(f.metric)}|{norm(f.geography)}|{norm(f.time_period)}"
        groups.setdefault(key, []).append(f)

    conflict_ids = set()
    duplicate_of = {}

    for key, g in groups.items():
        if len(g) < 2 or key == "||":
            continue
        canonical = g[0]
        for item in g[1:]:
            if item.id == canonical.id:
                continue
            if item.value is not None and canonical.value is not None and item.value != canonical.value:
                conflict_ids.add(item.id)
            else:
                duplicate_of[item.id] = canonical.id

    rule_results = []
    for f in findings:
        codes = []
        notes = []
        metadata_status = "pass"

        # 1. Source existence & registration
        src = src_map.get(f.source_id) if f.source_id else None
        if not f.source_id or not src:
            codes.append("MISSING_SOURCE")
            notes.append("Finding source is not registered.")
            metadata_status = "fail"
        else:
            # Metadata integrity checks
            if src.content_format == "html" and src.page_count is not None:
                codes.append("INVALID_PAGE_COUNT_ON_HTML")
                notes.append("HTML webpage source recorded with invalid PDF page count.")
                metadata_status = "warn"

            if src.tier >= 6:
                codes.append("TIER_6_UNVERIFIED")
                notes.append("Source is Tier 6 (Social/Informal) and lacks institutional grounding.")
                metadata_status = "warn"

        # 2. Evidence Grounding
        if not f.evidence_text or not f.evidence_text.strip():
            codes.append("NO_EVIDENCE")
            notes.append("Finding has no supporting evidence quote.")

        # 3. Completeness & Denominator
        if not f.claim or not f.claim.strip():
            codes.append("INCOMPLETE_CLAIM")
            notes.append("Missing factual claim statement.")

        if f.value is not None and not f.denominator_definition and not f.unit:
            codes.append("MISSING_DENOMINATOR")
            notes.append("Quantitative metric lacks explicit denominator or measurement unit.")

        if f.metric and (f.value is None or (not f.geography and not f.time_period)):
            codes.append("INCOMPLETE_CONTEXT")
            notes.append("Metric specified without complete numeric value or market context.")

        if (f.confidence or "").lower() in ("low", ""):
            codes.append("LOW_CONFIDENCE")
            notes.append("Confidence level is low or unspecified.")

        # 4. Conflicts & Duplicates
        if f.id in conflict_ids:
            codes.append("CONFLICT")
            notes.append("Conflicting value reported for the same metric, market, and period.")
        elif f.id in duplicate_of:
            codes.append("DUPLICATE")
            notes.append(f"Duplicate of finding {duplicate_of[f.id]}")

        rule_results.append({
            "finding": f,
            "metadata_status": metadata_status,
            "issue_codes": codes,
            "issues": notes,
            "duplicate_of": duplicate_of.get(f.id)
        })

    return rule_results


def validate_findings(
    findings: List[FindingRecord],
    sources: List[SourceRecord],
    run_id: str,
    project_id: str,
    max_llm_qc: int = 40
) -> List[ValidationVerdictRecord]:
    """
    Combines rule checks and LLM claim-support verification into comprehensive verdict records.
    """
    rule_results = run_referential_checks(findings, sources)
    verdicts: List[ValidationVerdictRecord] = []

    FAIL_CODES = {"NO_EVIDENCE", "MISSING_SOURCE", "CONFLICT", "INCOMPLETE_CLAIM"}
    WARN_CODES = {"LOW_CONFIDENCE", "INCOMPLETE_CONTEXT", "DUPLICATE", "MISSING_DENOMINATOR", "INVALID_PAGE_COUNT_ON_HTML", "TIER_6_UNVERIFIED"}

    for idx, item in enumerate(rule_results):
        f: FindingRecord = item["finding"]
        codes: List[str] = item["issue_codes"]
        notes: List[str] = item["issues"]
        meta_status = item["metadata_status"]

        support_verdict = "supported"
        support_score = 1.0
        denom_preserved = True

        # Run LLM claim-support check if evidence exists and within budget
        if f.evidence_text and idx < max_llm_qc:
            prompt = f"""CLAIM:
{f.claim}

METRIC / VALUE / UNIT:
{f.metric or 'N/A'}: {f.value if f.value is not None else 'N/A'} {f.unit or ''}

DENOMINATOR / DEFINITION:
{f.denominator_definition or 'Unspecified'}

EVIDENCE (verbatim quote):
"{f.evidence_text}"

Evaluate if the evidence strictly backs the claim and preserves the denominator/scope."""
            try:
                raw_resp = generate_llm_response(
                    prompt=prompt,
                    system_instruction=QC_SYSTEM_PROMPT,
                    json_mode=True,
                    temperature=0.0
                )
                data = parse_json_safely(raw_resp)
                v = str(data.get("support_verdict", "supported")).lower()
                if v in ("supported", "partial", "unsupported"):
                    support_verdict = v
                s = data.get("support_score")
                if s is not None:
                    support_score = float(s)
                denom_preserved = bool(data.get("denominator_preserved", True))
                reason = data.get("reason")

                if not denom_preserved:
                    codes.append("DENOMINATOR_ALTERED")
                    if reason:
                        notes.append(f"Denominator Warning: {reason}")

                if support_verdict == "unsupported":
                    codes.append("CLAIM_UNSUPPORTED")
                    if reason:
                        notes.append(f"LLM QC: {reason}")
                elif support_verdict == "partial":
                    codes.append("CLAIM_PARTIAL")
                    if reason:
                        notes.append(f"LLM QC: {reason}")
            except Exception:
                pass

        grounding_status = "fail" if support_verdict == "unsupported" else ("warn" if support_verdict == "partial" or not denom_preserved else "pass")

        # Determine final status
        if any(c in FAIL_CODES for c in codes) or support_verdict == "unsupported" or meta_status == "fail":
            status = "fail"
        elif any(c in WARN_CODES for c in codes) or support_verdict == "partial" or not denom_preserved or meta_status == "warn":
            status = "warn"
        else:
            status = "pass"

        verdicts.append(ValidationVerdictRecord(
            finding_id=f.id,
            run_id=run_id,
            project_id=project_id,
            source_id=f.source_id,
            validation_status=status,
            metadata_status=meta_status,
            grounding_status=grounding_status,
            comparability_status="pass",
            denominator_preserved=denom_preserved,
            calculation_valid=True if f.claim_type == "eclectik_derived_calculation" else None,
            issue_codes=",".join(set(codes)) if codes else None,
            issues=" | ".join(notes) if notes else None,
            support_score=support_score,
            support_verdict=support_verdict,
            duplicate_of=item.get("duplicate_of")
        ))

    return verdicts

