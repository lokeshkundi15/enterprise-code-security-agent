import pytest
from app.core.graph import review_pipeline
from app.schemas.findings import FindingSeverity

def test_full_graph_execution():
    sample_diff = """diff --git a/src/auth.py b/src/auth.py
--- a/src/auth.py
+++ b/src/auth.py
@@ -1,5 +1,6 @@
+API_KEY = "ghp_123456789012345678901234567890123456"
+def login(user):
+    cursor.execute(f"SELECT * FROM users WHERE name = '{user}'")
"""
    initial_state = {
        "pr_id": "PR-501",
        "raw_diff": sample_diff,
        "changed_files": [],
        "static_findings": [],
        "security_findings": [],
        "quality_findings": [],
        "aggregated_findings": [],
        "final_report": None,
        "error": None
    }
    
    final_output = review_pipeline.invoke(initial_state)
    report = final_output["final_report"]
    
    assert report is not None
    assert report.total_findings >= 2
    assert report.critical_count >= 1
    assert any(f.severity == FindingSeverity.CRITICAL for f in report.findings)
    assert any(f.title == "Hardcoded API Secret/Token" or f.rule_id == "CWE-798" for f in report.findings)