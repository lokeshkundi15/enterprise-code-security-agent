import ast
import re
from typing import List, Set
from app.schemas.findings import CodeFinding, FindingSeverity, FindingCategory

SECRET_PATTERNS = [
    (r"(?i)(api[_-]?key|secret|token|password)\s*=\s*['\"][A-Za-z0-9_\-\.]{12,}['\"]", "Hardcoded API Secret/Token", "CWE-798"),
    (r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}", "Hardcoded Bearer Token", "CWE-798"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub Personal Access Token", "CWE-798")
]

class ASTSecurityVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.findings: List[CodeFinding] = []
        self.dynamic_sql_vars: Set[str] = set()

    def visit_Assign(self, node: ast.Assign):
        if isinstance(node.value, ast.JoinedStr):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.dynamic_sql_vars.add(target.id)
        elif isinstance(node.value, ast.BinOp) and isinstance(node.value.op, (ast.Add, ast.Mod)):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.dynamic_sql_vars.add(target.id)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # 1. SQL Injection Check
        if isinstance(node.func, ast.Attribute) and node.func.attr == "execute":
            if node.args:
                first_arg = node.args[0]
                is_vulnerable = False
                if isinstance(first_arg, (ast.JoinedStr, ast.BinOp)):
                    is_vulnerable = True
                elif isinstance(first_arg, ast.Name) and first_arg.id in self.dynamic_sql_vars:
                    is_vulnerable = True
                elif isinstance(first_arg, ast.Call) and isinstance(first_arg.func, ast.Attribute) and first_arg.func.attr == "format":
                    is_vulnerable = True

                if is_vulnerable:
                    self.findings.append(
                        CodeFinding(
                            file_path=self.file_path,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            severity=FindingSeverity.CRITICAL,
                            category=FindingCategory.SECURITY,
                            title="SQL Injection Vulnerability",
                            description="Detected dynamic SQL string formatting/concatenation passed into database execute() call.",
                            recommendation="Use parameterized queries with placeholders instead of string interpolation.",
                            rule_id="CWE-89"
                        )
                    )
                    
        # 2. Quality Check: Unmanaged open() call
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            self.findings.append(
                CodeFinding(
                    file_path=self.file_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    severity=FindingSeverity.MEDIUM,
                    category=FindingCategory.ERROR_HANDLING,
                    title="Unmanaged File Descriptor / Resource Leak",
                    description="File opened without a context manager ('with' statement), risking unclosed file descriptors.",
                    recommendation="Use context manager: 'with open(...) as f:' to guarantee proper cleanup.",
                    rule_id="CODE-001"
                )
            )
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # 3. Quality Check: Bare except
        if node.type is None:
            self.findings.append(
                CodeFinding(
                    file_path=self.file_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    severity=FindingSeverity.HIGH,
                    category=FindingCategory.ERROR_HANDLING,
                    title="Bare Except Clause",
                    description="Bare except catches all exceptions including SystemExit and KeyboardInterrupt, hiding bugs.",
                    recommendation="Catch specific exceptions like 'except Exception:' or target specific error types.",
                    rule_id="CODE-002"
                )
            )
        self.generic_visit(node)

def clean_diff_to_valid_python(diff_content: str) -> str:
    cleaned_lines = []
    for line in diff_content.splitlines():
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        if line.startswith("+") or line.startswith(" "):
            cleaned_lines.append(line[1:])
        elif not line.startswith("-"):
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def run_static_ast_scan(file_path: str, code_content: str) -> List[CodeFinding]:
    findings: List[CodeFinding] = []
    
    # 1. Secret Scanning
    for idx, line in enumerate(code_content.splitlines(), start=1):
        for pattern, title, cwe in SECRET_PATTERNS:
            if re.search(pattern, line):
                findings.append(
                    CodeFinding(
                        file_path=file_path,
                        line_start=idx,
                        line_end=idx,
                        severity=FindingSeverity.HIGH,
                        category=FindingCategory.SECURITY,
                        title=title,
                        description=f"Potential hardcoded secret discovered on line {idx}.",
                        recommendation="Move sensitive credentials to external environment variables or a Secret Vault.",
                        rule_id=cwe
                    )
                )

    # 2. AST Parsing
    if file_path.endswith(".py"):
        cleaned_code = clean_diff_to_valid_python(code_content)
        try:
            tree = ast.parse(cleaned_code)
            visitor = ASTSecurityVisitor(file_path)
            visitor.visit(tree)
            findings.extend(visitor.findings)
        except SyntaxError:
            if re.search(r"cursor\.execute\s*\(\s*f[\"']", code_content):
                findings.append(
                    CodeFinding(
                        file_path=file_path,
                        line_start=1,
                        line_end=1,
                        severity=FindingSeverity.CRITICAL,
                        category=FindingCategory.SECURITY,
                        title="SQL Injection Vulnerability",
                        description="Detected dynamic SQL string formatting inside execute() call.",
                        recommendation="Use parameterized queries instead.",
                        rule_id="CWE-89"
                    )
                )

    return findings