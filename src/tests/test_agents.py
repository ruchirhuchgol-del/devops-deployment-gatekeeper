"""
Unit tests for agents.
"""

import unittest
from unittest.mock import patch, MagicMock

from devops_deployment_security_gate.agents.pr_extractor import (
    PRMetadataExtractionSpecialist,
)
from devops_deployment_security_gate.agents.scanner_agent import (
    SonarQubeSecurityScanner,
)
from devops_deployment_security_gate.agents.decision_engine import (
    SecurityPolicyDecisionEngine,
)
from devops_deployment_security_gate.agents.notification_manager import (
    SecurityAlertNotificationManager,
)
from devops_deployment_security_gate.models.security import (
    SecurityReport,
    SecurityIssue,
    SecurityDecision,
    SeverityLevel,
    VulnerabilityType,
)


class TestPRMetadataExtractionSpecialist(unittest.TestCase):
    """Test cases for PRMetadataExtractionSpecialist."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = PRMetadataExtractionSpecialist()

    def test_agent_attributes(self):
        """Test agent attributes."""
        self.assertEqual(self.agent.role, "PR Metadata Extraction Specialist")
        self.assertTrue("GitHub workflow automation" in self.agent.backstory)

    def test_extract_pr_context_no_tool_raises(self):
        """CURSOR-21: missing tool must raise RuntimeError, not return mock data."""
        agent = PRMetadataExtractionSpecialist()  # no tools wired
        with self.assertRaises(RuntimeError):
            agent.extract_pr_context("123", "test-org/test-repo", "feature-branch")

    def test_extract_pr_context_with_tool_calls_run(self):
        """CURSOR-21: when tool is provided its _run() method must be called."""
        mock_tool = MagicMock()
        mock_tool.name = "GitHub PR Tool"
        mock_tool._run.return_value = {
            "pr_number": "123",
            "repository": "test-org/test-repo",
            "branch_name": "feature-branch",
            "commit_sha": "abc123",
            "changed_files": ["src/main.py"],
            "author": "dev",
            "title": "Test PR",
            "description": "desc",
            "status": "open",
        }
        agent = PRMetadataExtractionSpecialist()
        object.__setattr__(agent, "tools", [mock_tool])
        result = agent.extract_pr_context("123", "test-org/test-repo", "feature-branch")
        mock_tool._run.assert_called_once()
        self.assertEqual(result["pr_number"], "123")


class TestSonarQubeSecurityScanner(unittest.TestCase):
    """Test cases for SonarQubeSecurityScanner."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = SonarQubeSecurityScanner()

    def test_agent_attributes(self):
        """Test agent attributes."""
        self.assertEqual(self.agent.role, "SonarQube Security Scanner")
        self.assertTrue("static code analysis" in self.agent.backstory)

    def test_execute_security_scan_raises_without_tool(self):
        """Without a wired tool, execute_security_scan should raise RuntimeError."""
        with self.assertRaises(RuntimeError):
            self.agent.execute_security_scan(
                "main", "test-project", "https://sonarqube.example.com"
            )

    def test_execute_security_scan_with_tool_calls_run(self):
        """When tool is provided its _run() method must be called."""
        mock_tool = MagicMock()
        mock_tool.name = "SonarQube Security Scanner"
        mock_tool._run.return_value = {
            "project_key": "test-project",
            "branch": "main",
            "scan_id": "scan_001",
            "scan_status": "SUCCESS",
            "total_issues": 0,
            "critical_count": 0,
            "major_count": 0,
            "minor_count": 0,
            "info_count": 0,
            "security_hotspots": 0,
            "issues": [],
            "scan_timestamp": "2025-01-01T00:00:00Z",
        }
        agent = SonarQubeSecurityScanner()
        object.__setattr__(agent, "tools", [mock_tool])
        result = agent.execute_security_scan(
            "main", "test-project", "https://sonarqube.example.com"
        )
        mock_tool._run.assert_called_once()
        self.assertIsInstance(result, SecurityReport)
        self.assertEqual(result.project_key, "test-project")

    def test_execute_security_scan_validation(self):
        """Test validation in security scan execution."""
        # Test with missing branch name
        with self.assertRaises(ValueError) as context:
            self.agent.execute_security_scan(
                "", "test-project", "https://sonarqube.example.com"
            )
        self.assertTrue("Branch name is required" in str(context.exception))

        # Test with missing project key
        with self.assertRaises(ValueError) as context:
            self.agent.execute_security_scan(
                "main", "", "https://sonarqube.example.com"
            )
        self.assertTrue("Project key is required" in str(context.exception))

        # Test with missing SonarQube URL
        with self.assertRaises(ValueError) as context:
            self.agent.execute_security_scan("main", "test-project", "")
        self.assertTrue("SonarQube URL is required" in str(context.exception))


class TestSecurityPolicyDecisionEngine(unittest.TestCase):
    """Test cases for SecurityPolicyDecisionEngine."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = SecurityPolicyDecisionEngine()

    def test_agent_attributes(self):
        """Test agent attributes."""
        self.assertEqual(self.agent.role, "Security Policy Decision Engine")
        self.assertTrue("threat modeling" in self.agent.backstory)

    def test_evaluate_security_report_allow(self):
        """Test evaluation that allows deployment."""
        issues = [
            SecurityIssue(
                key="issue1",
                rule="python:S1135",
                severity=SeverityLevel.INFO,
                type=VulnerabilityType.CODE_SMELL,
                component="src/utils.py",
                message="Track TODO comment",
                line=120,
            )
        ]

        report = SecurityReport(
            project_key="test-project",
            branch="main",
            scan_id="scan_12345",
            scan_status="SUCCESS",
            total_issues=1,
            critical_count=0,
            major_count=0,
            minor_count=0,
            info_count=1,
            security_hotspots=0,
            issues=issues,
            scan_timestamp="2025-10-06T10:30:00Z",
        )

        decision = self.agent.evaluate_security_report(report)

        self.assertEqual(decision.decision, "ALLOW")
        self.assertEqual(decision.reason, "No policy violations detected")

    def test_evaluate_security_report_block(self):
        """Test evaluation that blocks deployment."""
        # Create a report with critical issues
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
            )
        ]

        report = SecurityReport(
            project_key="test-project",
            branch="main",
            scan_id="scan_12345",
            scan_status="SUCCESS",
            total_issues=1,
            critical_count=1,
            major_count=0,
            minor_count=0,
            info_count=0,
            security_hotspots=0,
            issues=issues,
            scan_timestamp="2025-10-06T10:30:00Z",
        )

        decision = self.agent.evaluate_security_report(report)

        self.assertEqual(decision.decision, "BLOCK")
        self.assertTrue("Critical vulnerability threshold exceeded" in decision.reason)


class TestSecurityAlertNotificationManager(unittest.TestCase):
    """Test cases for SecurityAlertNotificationManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = SecurityAlertNotificationManager()

    def test_agent_attributes(self):
        """Test agent attributes."""
        self.assertEqual(self.agent.role, "Security Alert Notification Manager")
        self.assertTrue("rapid incident response" in self.agent.backstory)

    def test_send_security_notification_raises_without_tool(self):
        """Without a wired tool, send_security_notification should raise RuntimeError."""
        with self.assertRaises(RuntimeError):
            self.agent.send_security_notification(
                decision="BLOCK",
                repository="test-org/test-repo",
                pr_number="123",
                slack_channel="#security-alerts",
            )

    def test_send_security_notification_with_tool_calls_run(self):
        """When Slack tool is provided its _run() method must be called."""
        mock_tool = MagicMock()
        mock_tool.name = "Slack Notification Tool"
        mock_tool._run.return_value = {
            "channel": "#security-alerts",
            "message": "BLOCKED",
            "status": "sent",
        }
        agent = SecurityAlertNotificationManager()
        object.__setattr__(agent, "tools", [mock_tool])
        result = agent.send_security_notification(
            decision="BLOCK",
            repository="test-org/test-repo",
            pr_number="123",
            slack_channel="#security-alerts",
        )
        mock_tool._run.assert_called_once()
        self.assertEqual(result["channel"], "#security-alerts")

    def test_send_security_notification_validation(self):
        """Test validation in sending security notification."""
        # Test with missing decision
        with self.assertRaises(ValueError) as context:
            self.agent.send_security_notification(
                "", "test-org/test-repo", "123", "#security-alerts"
            )
        self.assertTrue("Decision is required" in str(context.exception))

        # Test with missing repository
        with self.assertRaises(ValueError) as context:
            self.agent.send_security_notification(
                "BLOCK", "", "123", "#security-alerts"
            )
        self.assertTrue("Repository is required" in str(context.exception))

        # Test with missing PR number
        with self.assertRaises(ValueError) as context:
            self.agent.send_security_notification(
                "BLOCK", "test-org/test-repo", "", "#security-alerts"
            )
        self.assertTrue("PR number is required" in str(context.exception))

        # Test with missing Slack channel
        with self.assertRaises(ValueError) as context:
            self.agent.send_security_notification(
                "BLOCK", "test-org/test-repo", "123", ""
            )
        self.assertTrue("Slack channel is required" in str(context.exception))


if __name__ == "__main__":
    unittest.main()
