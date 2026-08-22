import re
from typing import List, Dict, Any

def parse_unified_diff(raw_diff: str) -> List[Dict[str, Any]]:
    """
    Parses a unified git diff into structured file chunks with line numbers.
    """
    files = []
    current_file = None
    current_lines = []
    
    file_header_pattern = re.compile(r"^diff --git a/(.*) b/(.*)$")
    hunk_header_pattern = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
    
    for line in raw_diff.splitlines():
        file_match = file_header_pattern.match(line)
        if file_match:
            if current_file:
                current_file["changes"] = "\n".join(current_lines)
                files.append(current_file)
            current_file = {
                "file_path": file_match.group(2),
                "hunks": []
            }
            current_lines = []
            continue
            
        hunk_match = hunk_header_pattern.match(line)
        if hunk_match and current_file:
            current_file["hunks"].append({
                "old_start": int(hunk_match.group(1)),
                "new_start": int(hunk_match.group(2))
            })
            
        if current_file:
            current_lines.append(line)
            
    if current_file:
        current_file["changes"] = "\n".join(current_lines)
        files.append(current_file)
        
    return files