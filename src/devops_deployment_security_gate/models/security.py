"""
Security models for the DevSecOps Deployment Gatekeeper.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any, Literal
from enum import Enum


class SeverityLevel(str, Enum):
    """
    Severity levels for security issues.

    CRITICAL: Critical security vulnerabilities that must be fixed immediately
    MAJOR: Major security vulnerabilities that should be addressed soon
    MINOR: Minor security issues that should be addressed when possible
    INFO: Informational security findings
    """

    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    INFO = "INFO"


class VulnerabilityType(str, Enum):
    """
    Types of security findings.

    VULNERABILITY: Security vulnerabilities in the code
    SECURITY_HOTSPOT: Security-sensitive code that needs review
    CODE_SMELL: Maintainability issues that may impact security
    BUG: Functional bugs that may have security implications
    """

    VULNERABILITY = "VULNERABILITY"
    SECURITY_HOTSPOT = "SECURITY_HOTSPOT"
    CODE_SMELL = "CODE_SMELL"
    BUG = "BUG"


class SecurityIssue(BaseModel):
    """
    Represents a single security issue found during scanning.

    Attributes:
        key: Unique identifier for the issue
        rule: The rule that triggered this issue
        severity: Severity level of the issue
        type: Type of the issue
        component: Component/file where the issue was found
        message: Description of the issue
        line: Line number where the issue was found (optional)
        status: Current status of the issue (default: OPEN)
        effort: Effort required to fix the issue (optional)
        tags: Tags associated with the issue
        cwe: CWE identifier for the issue (optional)
        owasp_category: OWASP category for the issue (optional)
    """

    key: str
    rule: str
    severity: SeverityLevel
    type: VulnerabilityType
    component: str
    message: str
    line: Optional[int] = None
    status: str = "OPEN"
    effort: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    cwe: Optional[int] = None
    owasp_category: Optional[str] = None

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v):
        """Normalize severity values to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return v


class SecurityReport(BaseModel):
    """
    Represents a complete security report from a scan.

    Attributes:
        project_key: Key of the project that was scanned
        branch: Branch that was scanned
        scan_id: Unique identifier for the scan
        scan_status: Status of the scan (SUCCESS, FAILED, etc.)
        total_issues: Total number of issues found
        critical_count: Number of critical issues
        major_count: Number of major issues
        minor_count: Number of minor issues
        info_count: Number of info issues
        security_hotspots: Number of security hotspots
        issues: List of individual security issues
        scan_timestamp: Timestamp when the scan was performed
        scan_duration: Duration of the scan in seconds (optional)
    """

    project_key: str
    branch: str
    scan_id: str
    scan_status: str
    total_issues: int
    critical_count: int
    major_count: int
    minor_count: int
    info_count: int
    security_hotspots: int
    issues: List[SecurityIssue] = Field(default_factory=list)
    scan_timestamp: str
    scan_duration: Optional[int] = None  # in seconds

    @property
    def has_critical_issues(self) -> bool:
        """Check if the report contains critical issues."""
        return self.critical_count > 0

    @property
    def has_major_issues(self) -> bool:
        """Check if the report contains major issues."""
        return self.major_count > 0

    @property
    def security_score(self) -> float:
        """
        Calculate a security score from 0-100.

        Returns:
            float: Security score where 100 is perfect and 0 is completely insecure
        """
        if self.total_issues == 0:
            return 100.0

        # Weight critical issues more heavily
        weighted_issues = (
            self.critical_count * 10
            + self.major_count * 5
            + self.minor_count * 2
            + self.info_count * 1
        )

        # Calculate score (inverse of weighted issues)
        max_possible = self.total_issues * 10
        score = max(0, 100 - (weighted_issues / max_possible * 100))
        return round(score, 2)


class SecurityDecision(BaseModel):
    """
    Represents a security decision made based on a security report.

    Attributes:
        decision: The decision (ALLOW or BLOCK)
        reason: Reason for the decision
        policy_violations: List of policy violations that led to the decision
        recommendations: Recommendations for addressing issues
        override_allowed: Whether manual override is allowed
        override_reason: Reason for manual override (optional)
        decision_timestamp: Timestamp when the decision was made
        reviewer: Person who made the decision (optional)
    """

    decision: Literal["ALLOW", "BLOCK"]
    reason: str
    policy_violations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    override_allowed: bool = False
    override_reason: Optional[str] = None
    decision_timestamp: str
    reviewer: Optional[str] = None
