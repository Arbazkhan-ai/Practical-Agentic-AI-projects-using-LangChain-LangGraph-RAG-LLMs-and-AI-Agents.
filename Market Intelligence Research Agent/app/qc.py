"""
Quality Control (QC) & Validation Engine:
Executes deterministic rule-based checks followed by LLM Claim-Support verification
to classify findings into pass, warn, or fail.
"""

from typing import List, Dict, Any, Tuple
from schemas import FindingRecord, SourceRecord, ValidationVerdictRecord
from llm_client import generate_llm_response, parse_json_safely

QC_SYSTEM_PROMPT = """You are a strict research QA checker. You judge only whether provided verbatim evidence quotes support a given claim, using no outside knowledge. You never invent facts. 

Return a single JSON object with EXACTLY this structure:
{
  "support_verdict": "supported" | "partial" | "unsupported",
  "support_score": 0.95,  // float between 0.0 and 1.0
  "reason": "Clear one-sentence explanation"
}

Definitions:
- supported: the evidence directly and fully states the claim.
- partial: the evidence is related but does not fully establish the claim.
- unsupported: the evidence does not back the claim.
"""


def run_referential_checks(
    findings: List[FindingRecord],
    sources: List[SourceRecord]
) -> List[Dict[str, Any]]:
    """
    Performs deterministic rule checks (duplicates, conflicts, completeness, missing source).
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

        if not f.evidence_text or not f.evidence_text.strip():
            codes.append("NO_EVIDENCE")
            notes.append("Finding has no supporting evidence quote.")

        if not f.source_id or f.source_id not in src_map:
            codes.append("MISSING_SOURCE")
            notes.append("Finding source is not registered.")

        if not f.claim or not f.claim.strip():
            codes.append("INCOMPLETE")
            notes.append("Missing factual claim statement.")

        if f.metric and (f.value is None or (not f.geography and not f.time_period)):
            codes.append("INCOMPLETE")
            notes.append("Metric specified without complete numeric value or context.")

        if (f.confidence or "").lower() in ("low", ""):
            codes.append("LOW_CONFIDENCE")
            notes.append("Confidence level is low or unspecified.")

        if f.id in conflict_ids:
            codes.append("CONFLICT")
            notes.append("Conflicting value reported for the same metric, market, and period.")
        elif f.id in duplicate_of:
            codes.append("DUPLICATE")
            notes.append(f"Duplicate of finding {duplicate_of[f.id]}")

        rule_results.append({
            "finding": f,
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
    Combines rule checks and LLM claim-support verification into final verdict records.
    """
    rule_results = run_referential_checks(findings, sources)
    verdicts: List[ValidationVerdictRecord] = []

    FAIL_CODES = {"NO_EVIDENCE", "MISSING_SOURCE", "CONFLICT"}
    WARN_CODES = {"LOW_CONFIDENCE", "INCOMPLETE", "DUPLICATE"}

    for idx, item in enumerate(rule_results):
        f: FindingRecord = item["finding"]
        codes: List[str] = item["issue_codes"]
        notes: List[str] = item["issues"]

        support_verdict = "supported"
        support_score = 1.0

        # Run LLM claim-support check if evidence exists and within budget
        if f.evidence_text and idx < max_llm_qc:
            prompt = f"""CLAIM:
{f.claim}

EVIDENCE (verbatim quote):
"{f.evidence_text}"

Evaluate if the evidence strictly backs the claim."""
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
                reason = data.get("reason")

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

        # Determine final status
        if any(c in FAIL_CODES for c in codes) or support_verdict == "unsupported":
            status = "fail"
        elif any(c in WARN_CODES for c in codes) or support_verdict == "partial":
            status = "warn"
        else:
            status = "pass"

        verdicts.append(ValidationVerdictRecord(
            finding_id=f.id,
            run_id=run_id,
            project_id=project_id,
            source_id=f.source_id,
            validation_status=status,
            issue_codes=",".join(set(codes)) if codes else None,
            issues=" | ".join(notes) if notes else None,
            support_score=support_score,
            support_verdict=support_verdict,
            duplicate_of=item.get("duplicate_of")
        ))

    return verdicts
