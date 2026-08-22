import re
from typing import List, Dict, Any

# Ignore generated, lockfiles, and binary assets
IGNORED_EXTENSIONS = {".lock", ".json", ".min.js", ".min.css", ".map", ".csv", ".svg", ".png", ".jpg"}
IGNORED_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "uv.lock"}

MAX_DIFF_LINES_PER_FILE = 250

def filter_and_chunk_diff(changed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    1. Filters out generated lockfiles and binary assets.
    2. Bounds code diff chunks to prevent LLM context blowups and OOM.
    """
    prioritized_files = []
    
    for f in changed_files:
        f_path = f["file_path"]
        
        # Skip noise files
        if any(f_path.endswith(ext) for ext in IGNORED_EXTENSIONS) or f_path in IGNORED_FILES:
            continue
            
        lines = f["changes"].splitlines()
        
        # If file diff is too large, truncate intelligently with boundary marker
        if len(lines) > MAX_DIFF_LINES_PER_FILE:
            truncated_changes = "\n".join(lines[:MAX_DIFF_LINES_PER_FILE])
            truncated_changes += f"\n\n# ... [TRUNCATED: {len(lines) - MAX_DIFF_LINES_PER_FILE} lines omitted for context boundary] ..."
            f["changes"] = truncated_changes
            f["is_truncated"] = True
        else:
            f["is_truncated"] = False
            
        prioritized_files.append(f)
        
    return prioritized_files