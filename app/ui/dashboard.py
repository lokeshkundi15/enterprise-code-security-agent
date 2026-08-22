import sys
from pathlib import Path

# Add project root directory to sys.path so Streamlit can locate the 'app' module
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import json
from app.core.graph import review_pipeline
from app.schemas.findings import FindingSeverity

st.set_page_config(
    page_title="Enterprise Code Review & Security Agent",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Enterprise Code Review & Security Agent")
st.caption("Deterministic Static AST + Specialized Multi-Agent Code Governance & Security Analysis")

# Sample Pull Request Diffs for Quick Testing
SAMPLE_DIFFS = {
    "PR #101: Insecure SQL & Hardcoded Secret (High Risk)": """diff --git a/src/auth.py b/src/auth.py
--- a/src/auth.py
+++ b/src/auth.py
@@ -1,6 +1,8 @@
 import os
+API_KEY = "ghp_123456789012345678901234567890123456"
 
 def login_user(username, password):
-    # Safe query placeholder
-    pass
+    query = f"SELECT * FROM users WHERE user = '{username}' AND pass = '{password}'"
+    cursor.execute(query)
""",
    "PR #102: Resource Leak & Missing Error Handling (Medium Risk)": """diff --git a/src/processor.py b/src/processor.py
--- a/src/processor.py
+++ b/src/processor.py
@@ -10,4 +10,8 @@
 def process_large_payload(file_path):
+    f = open(file_path, "r")
+    data = f.read()
+    return json.loads(data)
""",
    "PR #103: Clean Refactor (Low/No Risk)": """diff --git a/src/utils.py b/src/utils.py
--- a/src/utils.py
+++ b/src/utils.py
@@ -5,3 +5,4 @@
 def format_timestamp(ts):
-    return str(ts)
+    from datetime import datetime
+    return datetime.fromtimestamp(ts).isoformat()
"""
}

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Review Configuration")
    selected_sample = st.selectbox("Choose a Sample PR Diff:", list(SAMPLE_DIFFS.keys()))
    pr_identifier = st.text_input("PR ID / Branch Name:", value="PR-402")
    st.markdown("---")
    st.markdown("**Core Capabilities:**")
    st.markdown("• FastMCP Decoupled Git & AST Tools\n• OWASP Top 10 Security Agent\n• Quality & Error Handling Agent\n• Human-in-the-Loop Gatekeeper")

# Main Input Section
diff_input = st.text_area("Unified Git Diff Content:", value=SAMPLE_DIFFS[selected_sample], height=220)

if st.button("🚀 Analyze Pull Request", type="primary", use_container_width=True):
    with st.spinner("Executing Static AST Scanners + Multi-Agent LangGraph Pipeline..."):
        initial_state = {
            "pr_id": pr_identifier,
            "raw_diff": diff_input,
            "changed_files": [],
            "static_findings": [],
            "security_findings": [],
            "quality_findings": [],
            "aggregated_findings": [],
            "final_report": None,
            "error": None
        }
        
        result_state = review_pipeline.invoke(initial_state)
        report = result_state.get("final_report")
        
        if report:
            st.session_state["latest_report"] = report

if "latest_report" in st.session_state:
    report = st.session_state["latest_report"]
    
    st.markdown("---")
    st.subheader(f"📊 Review Report Summary for `{report.pr_id}`")
    
    # KPI Metrics
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Findings", report.total_findings)
    kpi2.metric("Critical", report.critical_count, delta_color="inverse")
    kpi3.metric("High", report.high_count, delta_color="inverse")
    kpi4.metric("Medium", report.medium_count)
    kpi5.metric("Low / Info", report.low_count)
    
    st.info(report.summary)
    
    # Detailed Findings Tabulation
    if report.findings:
        st.subheader("🔍 Identified Code Issues & Vulnerabilities")
        for idx, finding in enumerate(report.findings, start=1):
            sev_badge = {
                FindingSeverity.CRITICAL: "🔴 CRITICAL",
                FindingSeverity.HIGH: "🟠 HIGH",
                FindingSeverity.MEDIUM: "🟡 MEDIUM",
                FindingSeverity.LOW: "🔵 LOW",
                FindingSeverity.INFO: "⚪ INFO"
            }.get(finding.severity, "⚪ INFO")
            
            with st.expander(f"{sev_badge} | {finding.title} ({finding.file_path}: Lines {finding.line_start}-{finding.line_end})", expanded=True):
                st.markdown(f"**Category:** `{finding.category}` | **Rule ID:** `{finding.rule_id or 'N/A'}`")
                st.markdown(f"**Description:** {finding.description}")
                st.markdown(f"**Recommended Patch:**\n```python\n{finding.recommendation}\n```")
    else:
        st.success("✅ Clean Diff: No security vulnerabilities or critical code quality issues detected!")

    # Human in the Loop Authorization Block
    st.markdown("---")
    st.subheader("🛑 Human-in-the-Loop Gateway (Approval Before Action)")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        st.write("Review recommendations above. Publishing comments or marking PR checks requires explicit operator authorization.")
    with c2:
        if st.button("✅ Approve & Post Review", use_container_width=True):
            st.success(f"Audit Logged: Review for {report.pr_id} successfully authorized by human reviewer!")