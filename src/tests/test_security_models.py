"""
Unit tests for security models.
"""

import unittest
from datetime import datetime, timezone

from devops_deployment_security_gate.models.security import (
    SecurityIssue,
    SecurityReport,
    SecurityDecision,
    SeverityLevel,
    VulnerabilityType,
)


class TestSecurityModels(unittest.TestCase):
    """Test cases for security models."""

    def test_security_issue_creation(self):
        """Test SecurityIssue model creation."""
        issue = SecurityIssue(
            key="test1",
            rule="python:S3649",
            severity=SeverityLevel.CRITICAL,
            type=VulnerabilityType.VULNERABILITY,
            component="src/main.py",
            message="SQL injection vulnerability detected",
            line=45,
            cwe=89,
            owasp_category="A03:2021-Injection",
        )

        self.assertEqual(issue.key, "test1")
        self.assertEqual(issue.rule, "python:S3649")
        self.assertEqual(issue.severity, SeverityLevel.CRITICAL)
        self.assertEqual(issue.type, VulnerabilityType.VULNERABILITY)
        self.assertEqual(issue.component, "src/main.py")
        self.assertEqual(issue.message, "SQL injection vulnerability detected")
        self.assertEqual(issue.line, 45)
        self.assertEqual(issue.cwe, 89)
        self.assertEqual(issue.owasp_category, "A03:2021-Injection")

    def test_security_report_creation(self):
        """Test SecurityReport model creation."""
        # Create test issues
        issues = [
            SecurityIssue(
                key="issue1",
                rule="python:S3649",
                severity=SeverityLevel.CRITICAL,
                type=VulnerabilityType.VULNERABILITY,
                component="src/main.py",
                message="SQL injection vulnerability detected",
                line=45,
                cwe=89,
            ),
            SecurityIssue(
                key="issue2",
                rule="python:S5542",
                severity=SeverityLevel.MAJOR,
                type=VulnerabilityType.VULNERABILITY,
                component="src/utils.py",
                message="Encryption algorithm is not secure",
                line=120,
                cwe=327,
            ),
        ]

        report = SecurityReport(
            project_key="test-project",
            branch="main",
            scan_id="scan_12345",
            scan_status="SUCCESS",
            total_issues=2,
            critical_count=1,
            major_count=1,
            minor_count=0,
            info_count=0,
            security_hotspots=0,
            issues=issues,
            scan_timestamp=datetime.now(timezone.utc).isoformat(),
            scan_duration=120,
        )

        self.assertEqual(report.project_key, "test-project")
        self.assertEqual(report.branch, "main")
        self.assertEqual(report.scan_id, "scan_12345")
        self.assertEqual(report.scan_status, "SUCCESS")
        self.assertEqual(report.total_issues, 2)
        self.assertEqual(report.critical_count, 1)
        self.assertEqual(report.major_count, 1)
        self.assertEqual(report.has_critical_issues, True)
        self.assertEqual(report.has_major_issues, True)
        self.assertEqual(len(report.issues), 2)

    def test_security_report_security_score(self):
        """Test SecurityReport security score calculation."""
        # Test perfect score with no issues
        report_no_issues = SecurityReport(
            project_key="test-project",
            branch="main",
            scan_id="scan_12345",
            scan_status="SUCCESS",
            total_issues=0,
            critical_count=0,
            major_count=0,
            minor_count=0,
            info_count=0,
            security_hotspots=0,
            issues=[],
            scan_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self.assertEqual(report_no_issues.security_score, 100.0)

        # Test score with issues
        issues = [
            SecurityIssue(
                key="issue1",
                rule="python:S3649",
                severity=SeverityLevel.CRITICAL,
                type=VulnerabilityType.VULNERABILITY,
                component="src/main.py",
                message="SQL injection vulnerability detected",
                line=45,
                cwe=89,
            ),
            SecurityIssue(
                key="issue2",
                rule="python:S5542",
                severity=SeverityLevel.MAJOR,
                type=VulnerabilityType.VULNERABILITY,
                component="src/utils.py",
                message="Encryption algorithm is not secure",
                line=120,
                cwe=327,
            ),
        ]

        report_with_issues = SecurityReport(
            project_key="test-project",
            branch="main",
            scan_id="scan_12345",
            scan_status="SUCCESS",
            total_issues=2,
            critical_count=1,
            major_count=1,
            minor_count=0,
            info_count=0,
            security_hotspots=0,
            issues=issues,
            scan_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Score should be less than 100 but greater than 0
        self.assertLess(report_with_issues.security_score, 100.0)
        self.assertGreater(report_with_issues.security_score, 0.0)

    def test_security_decision_creation(self):
        """Test SecurityDecision model creation."""
        decision = SecurityDecision(
            decision="BLOCK",
            reason="Critical vulnerability threshold exceeded",
            policy_violations=["Critical vulnerability threshold exceeded: 1 > 0"],
            recommendations=[
                "All critical vulnerabilities must be resolved before deployment"
            ],
            override_allowed=False,
            decision_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self.assertEqual(decision.decision, "BLOCK")
        self.assertEqual(decision.reason, "Critical vulnerability threshold exceeded")
        self.assertEqual(len(decision.policy_violations), 1)
        self.assertEqual(len(decision.recommendations), 1)
        self.assertEqual(decision.override_allowed, False)


if __name__ == "__main__":
    unittest.main()
