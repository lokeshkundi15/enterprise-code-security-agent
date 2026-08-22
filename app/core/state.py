from typing import TypedDict, List, Dict, Any, Optional
from app.schemas.findings import CodeFinding, ReviewReport

class ReviewState(TypedDict):
    pr_id: str
    raw_diff: str
    changed_files: List[Dict[str, Any]]
    static_findings: List[Dict[str, Any]]
    security_findings: List[Dict[str, Any]]
    quality_findings: List[Dict[str, Any]]
    aggregated_findings: List[CodeFinding]
    final_report: Optional[ReviewReport]
    error: Optional[str]