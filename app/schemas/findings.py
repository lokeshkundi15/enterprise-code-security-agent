from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class FindingSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class FindingCategory(str, Enum):
    SECURITY = "SECURITY"
    ERROR_HANDLING = "ERROR_HANDLING"
    PERFORMANCE = "PERFORMANCE"
    CODE_QUALITY = "CODE_QUALITY"
    TESTING = "TESTING"

class CodeFinding(BaseModel):
    file_path: str = Field(description="Path of the file where the issue was found")
    line_start: int = Field(description="Starting line number of the issue")
    line_end: int = Field(description="Ending line number of the issue")
    severity: FindingSeverity = Field(description="Severity level of the finding")
    category: FindingCategory = Field(description="Category of the finding")
    title: str = Field(description="Brief summary of the issue")
    description: str = Field(description="Detailed explanation of why this is a risk")
    recommendation: str = Field(description="Actionable fix or code patch suggestion")
    rule_id: Optional[str] = Field(default=None, description="Static AST rule or CWE identifier")

class ReviewReport(BaseModel):
    pr_id: str = Field(description="Pull request identifier or branch name")
    summary: str = Field(description="High level executive summary of the code review")
    total_findings: int = Field(default=0, description="Total count of unique findings")
    critical_count: int = Field(default=0)
    high_count: int = Field(default=0)
    medium_count: int = Field(default=0)
    low_count: int = Field(default=0)
    findings: List[CodeFinding] = Field(default_factory=list, description="List of validated findings")
    approved_for_post: bool = Field(default=False, description="Human in the loop approval flag")