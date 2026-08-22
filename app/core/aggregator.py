from typing import List, Dict, Any
from app.schemas.findings import CodeFinding, FindingSeverity, ReviewReport

SEVERITY_ORDER = {
    FindingSeverity.CRITICAL: 4,
    FindingSeverity.HIGH: 3,
    FindingSeverity.MEDIUM: 2,
    FindingSeverity.LOW: 1,
    FindingSeverity.INFO: 0
}

def aggregate_and_deduplicate(findings_raw: List[Dict[str, Any]]) -> List[CodeFinding]:
    """
    Deduplicates findings by (file_path, line_start, category)
    and sorts them by Severity (CRITICAL -> INFO).
    """
    seen = set()
    validated_findings: List[CodeFinding] = []

    for f in findings_raw:
        try:
            finding_obj = CodeFinding.model_validate(f) if isinstance(f, dict) else f
            unique_key = (finding_obj.file_path, finding_obj.line_start, finding_obj.category, finding_obj.title)
            
            if unique_key not in seen:
                seen.add(unique_key)
                validated_findings.append(finding_obj)
        except Exception:
            continue

    # Sort deterministically by severity
    validated_findings.sort(
        key=lambda x: SEVERITY_ORDER.get(x.severity, 0),
        reverse=True
    )
    return validated_findings

def build_review_summary(pr_id: str, findings: List[CodeFinding]) -> ReviewReport:
    """Calculates finding counts and constructs the final ReviewReport."""
    crit = sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL)
    high = sum(1 for f in findings if f.severity == FindingSeverity.HIGH)
    med = sum(1 for f in findings if f.severity == FindingSeverity.MEDIUM)
    low = sum(1 for f in findings if f.severity == FindingSeverity.LOW)

    summary_text = (
        f"Automated Code Review completed for {pr_id}. "
        f"Identified {len(findings)} total issue(s): {crit} Critical, {high} High, {med} Medium, {low} Low."
    )

    return ReviewReport(
        pr_id=pr_id,
        summary=summary_text,
        total_findings=len(findings),
        critical_count=crit,
        high_count=high,
        medium_count=med,
        low_count=low,
        findings=findings,
        approved_for_post=False
    )