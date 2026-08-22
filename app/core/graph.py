from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.core.state import ReviewState
from app.mcp_server.tools.diff_parser import parse_unified_diff
from app.mcp_server.tools.ast_scanner import run_static_ast_scan
from app.agents.specialized_agents import run_security_analysis, run_quality_analysis
from app.core.aggregator import aggregate_and_deduplicate, build_review_summary
from app.core.chunker import filter_and_chunk_diff

def parse_diff_node(state: ReviewState) -> Dict[str, Any]:
    raw_files = parse_unified_diff(state["raw_diff"])
    # Filter noise files and chunk large diffs
    chunked_files = filter_and_chunk_diff(raw_files)
    return {"changed_files": chunked_files}

def static_scan_node(state: ReviewState) -> Dict[str, Any]:
    static_findings = []
    for f in state.get("changed_files", []):
        f_path = f["file_path"]
        f_code = f["changes"]
        findings = run_static_ast_scan(f_path, f_code)
        static_findings.extend([item.model_dump() for item in findings])
    return {"static_findings": static_findings}

def security_agent_node(state: ReviewState) -> Dict[str, Any]:
    sec_findings = []
    for f in state.get("changed_files", []):
        res = run_security_analysis(f["file_path"], f["changes"])
        sec_findings.extend(res)
    return {"security_findings": sec_findings}

def quality_agent_node(state: ReviewState) -> Dict[str, Any]:
    qual_findings = []
    for f in state.get("changed_files", []):
        res = run_quality_analysis(f["file_path"], f["changes"])
        qual_findings.extend(res)
    return {"quality_findings": qual_findings}

def aggregator_node(state: ReviewState) -> Dict[str, Any]:
    all_raw = []
    all_raw.extend(state.get("static_findings", []))
    all_raw.extend(state.get("security_findings", []))
    all_raw.extend(state.get("quality_findings", []))
    
    deduped = aggregate_and_deduplicate(all_raw)
    report = build_review_summary(state["pr_id"], deduped)
    return {
        "aggregated_findings": deduped,
        "final_report": report
    }

def build_review_graph():
    workflow = StateGraph(ReviewState)
    workflow.add_node("parse_diff", parse_diff_node)
    workflow.add_node("static_scan", static_scan_node)
    workflow.add_node("security_agent", security_agent_node)
    workflow.add_node("quality_agent", quality_agent_node)
    workflow.add_node("aggregator", aggregator_node)
    
    workflow.set_entry_point("parse_diff")
    workflow.add_edge("parse_diff", "static_scan")
    workflow.add_edge("static_scan", "security_agent")
    workflow.add_edge("security_agent", "quality_agent")
    workflow.add_edge("quality_agent", "aggregator")
    workflow.add_edge("aggregator", END)
    
    return workflow.compile()

review_pipeline = build_review_graph()