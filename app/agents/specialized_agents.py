import json
from typing import List, Dict, Any
from groq import Groq
from app.core.config import settings

def call_llm_json(prompt: str, system_prompt: str) -> List[Dict[str, Any]]:
    """Safe helper to call Groq Llama-3.3-70B with JSON output."""
    if not settings.GROQ_API_KEY:
        return []
    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model=settings.DEFAULT_MODEL,
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=800
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("findings", [])
    except Exception:
        return []

def run_security_analysis(file_path: str, diff_content: str) -> List[Dict[str, Any]]:
    """Security Agent: Focuses on AuthZ, Path Traversal, and Injection."""
    system_prompt = (
        "You are a Lead Application Security Engineer. Analyze the given code diff for security vulnerabilities "
        "(OWASP Top 10, CWE-22 Path Traversal, CWE-89 SQLi, CWE-502 Deserialization, Insecure Auth).\n"
        "Return a JSON object with key 'findings' containing a list of objects with fields:\n"
        "file_path, line_start, line_end, severity (CRITICAL/HIGH/MEDIUM/LOW/INFO), category (SECURITY), "
        "title, description, recommendation, rule_id."
    )
    prompt = f"FILE: {file_path}\nDIFF CHUNK:\n{diff_content}\n\nReturn findings JSON:"
    findings = call_llm_json(prompt, system_prompt)
    for f in findings:
        f["file_path"] = file_path
        f["category"] = "SECURITY"
    return findings

def run_quality_analysis(file_path: str, diff_content: str) -> List[Dict[str, Any]]:
    """Quality Agent: Focuses on Error Handling, Edge Cases, Resource Leaks."""
    system_prompt = (
        "You are a Principal Software Engineer. Analyze the given code diff specifically for:\n"
        "1. Resource leaks (e.g., using open() without 'with' statement or close()).\n"
        "2. Bare except clauses (e.g., 'except: pass' silencing all errors).\n"
        "3. Missing null checks or unhandled exceptions.\n\n"
        "Return a JSON object with key 'findings' containing a list of objects with fields:\n"
        "file_path, line_start, line_end, severity (HIGH/MEDIUM/LOW/INFO), category (ERROR_HANDLING), "
        "title, description, recommendation, rule_id."
    )
    prompt = f"FILE: {file_path}\nDIFF CHUNK:\n{diff_content}\n\nReturn findings JSON:"
    findings = call_llm_json(prompt, system_prompt)
    for f in findings:
        f["file_path"] = file_path
        f["category"] = "ERROR_HANDLING"
    return findings