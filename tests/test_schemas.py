import pytest
from app.schemas.findings import CodeFinding, FindingSeverity, FindingCategory, ReviewReport

def test_code_finding_valid_schema():
    finding = CodeFinding(
        file_path="auth/jwt.py",
        line_start=45,
        line_end=48,
        severity=FindingSeverity.HIGH,
        category=FindingCategory.SECURITY,
        title="Hardcoded JWT Secret Token",
        description="Found literal string passed as signature verification key.",
        recommendation="Load JWT secret securely from environment variables.",
        rule_id="CWE-798"
    )
    assert finding.severity == "HIGH"
    assert finding.category == "SECURITY"

def test_review_report_aggregation():
    finding = CodeFinding(
        file_path="db/query.py",
        line_start=12,
        line_end=15,
        severity=FindingSeverity.CRITICAL,
        category=FindingCategory.SECURITY,
        title="SQL Injection Vulnerability",
        description="Raw f-string passed directly into cursor.execute()",
        recommendation="Use parameterized query placeholders instead."
    )
    report = ReviewReport(
        pr_id="PR-104",
        summary="Security scan identified critical SQL injection vulnerabilities.",
        total_findings=1,
        critical_count=1,
        findings=[finding]
    )
    assert report.total_findings == 1
    assert report.critical_count == 1
    assert report.approved_for_post is False