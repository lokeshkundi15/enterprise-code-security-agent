from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any
from app.mcp_server.tools.diff_parser import parse_unified_diff
from app.mcp_server.tools.ast_scanner import run_static_ast_scan

mcp = FastMCP("Enterprise-Code-Review-Tools")

@mcp.tool()
def parse_pr_diff(raw_diff: str) -> List[Dict[str, Any]]:
    """Parse a unified git diff into structured file chunks."""
    return parse_unified_diff(raw_diff)

@mcp.tool()
def scan_static_security(file_path: str, content: str) -> List[Dict[str, Any]]:
    """Runs deterministic static AST and secret checks on a file."""
    findings = run_static_ast_scan(file_path, content)
    return [f.model_dump() for f in findings]

if __name__ == "__main__":
    mcp.run()