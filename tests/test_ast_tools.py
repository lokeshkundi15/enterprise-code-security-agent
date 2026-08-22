from app.mcp_server.tools.ast_scanner import run_static_ast_scan
from app.mcp_server.tools.diff_parser import parse_unified_diff

def test_ast_detects_sql_injection():
    vulnerable_code = """
def get_user_records(user_id):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
"""
    findings = run_static_ast_scan("db/users.py", vulnerable_code)
    assert len(findings) >= 1
    assert any(f.rule_id == "CWE-89" for f in findings)
    assert any(f.severity == "CRITICAL" for f in findings)

def test_ast_detects_hardcoded_secret():
    secret_code = 'OPENAI_API_KEY = "sk-proj-1234567890abcdef1234567890"'
    findings = run_static_ast_scan("config.py", secret_code)
    assert len(findings) >= 1
    assert any(f.rule_id == "CWE-798" for f in findings)

def test_diff_parser_structured_output():
    diff_text = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,3 +1,4 @@
+import os
"""
    parsed = parse_unified_diff(diff_text)
    assert len(parsed) == 1
    assert parsed[0]["file_path"] == "app.py"