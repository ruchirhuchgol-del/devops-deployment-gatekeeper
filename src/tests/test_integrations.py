"""
Unit tests for integrations.
"""

import unittest
from unittest.mock import patch, MagicMock

from devops_deployment_security_gate.integrations.github import GitHubIntegration
from devops_deployment_security_gate.integrations.sonarqube import SonarQubeIntegration
from devops_deployment_security_gate.integrations.slack import SlackIntegration
from devops_deployment_security_gate.utils.exceptions import ValidationError


class TestGitHubIntegration(unittest.TestCase):
    """Test cases for GitHubIntegration."""

    def setUp(self):
        """Set up test fixtures."""
        self.github = GitHubIntegration(
            token="test-token", base_url="https://api.github.com"
        )

    def test_initialization(self):
        """Test GitHub integration initialization."""
        self.assertEqual(self.github.token, "test-token")
        self.assertEqual(self.github.base_url, "https://api.github.com")

    @patch("devops_deployment_security_gate.integrations.github.requests.get")
    def test_get_pull_request_success(self, mock_get):
        """Test successful retrieval of pull request."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 123, "title": "Test PR"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test the method
        result = self.github.get_pull_request("test-org/test-repo", "123")

        self.assertEqual(result["id"], 123)
        self.assertEqual(result["title"], "Test PR")
        mock_get.assert_called_once()

    def test_get_pull_request_validation(self):
        """Test validation in pull request retrieval."""
        # Test with invalid repository format
        with self.assertRaises(ValidationError) as context:
            self.github.get_pull_request("test-repo", "123")
        self.assertTrue("Invalid repository format" in str(context.exception))

        with self.assertRaises(ValidationError) as context:
            self.github.get_pull_request("test-org/test-repo", "")
        self.assertTrue("Invalid PR number" in str(context.exception))

    @patch("devops_deployment_security_gate.integrations.github.requests.get")
    def test_get_pull_request_files_success(self, mock_get):
        """Test successful retrieval of pull request files."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"filename": "src/main.py"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test the method
        result = self.github.get_pull_request_files("test-org/test-repo", "123")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["filename"], "src/main.py")
        mock_get.assert_called_once()

    def test_get_pull_request_files_validation(self):
        """Test validation in pull request files retrieval."""
        # Test with invalid repository format
        with self.assertRaises(ValidationError) as context:
            self.github.get_pull_request_files("test-repo", "123")
        self.assertTrue("Invalid repository format" in str(context.exception))

        with self.assertRaises(ValidationError) as context:
            self.github.get_pull_request_files("test-org/test-repo", "")
        self.assertTrue("Invalid PR number" in str(context.exception))

    @patch("devops_deployment_security_gate.integrations.github.requests.post")
    def test_update_pull_request_status_success(self, mock_post):
        """Test successful update of pull request status."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 123, "state": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test the method
        result = self.github.update_pull_request_status(
            repository="test-org/test-repo",
            sha="abc123def456",
            state="success",
            target_url="https://example.com",
            description="Test description",
            context="test-context",
        )

        self.assertEqual(result["id"], 123)
        self.assertEqual(result["state"], "success")
        mock_post.assert_called_once()

    def test_update_pull_request_status_validation(self):
        """Test validation in pull request status update."""
        # Test with invalid repository format
        with self.assertRaises(ValidationError) as context:
            self.github.update_pull_request_status(
                repository="test-repo",
                sha="abc123def456",
                state="success",
                target_url="https://example.com",
                description="Test description",
                context="test-context",
            )
        self.assertTrue("Invalid repository format" in str(context.exception))

        # Test with missing SHA
        with self.assertRaises(ValidationError) as context:
            self.github.update_pull_request_status(
                repository="test-org/test-repo",
                sha="",
                state="success",
                target_url="https://example.com",
                description="Test description",
                context="test-context",
            )
        self.assertTrue("Commit SHA is required" in str(context.exception))

        # Test with missing state
        with self.assertRaises(ValidationError) as context:
            self.github.update_pull_request_status(
                repository="test-org/test-repo",
                sha="abc123def456",
                state="",
                target_url="https://example.com",
                description="Test description",
                context="test-context",
            )
        self.assertTrue("State is required" in str(context.exception))

        # Test with missing context
        with self.assertRaises(ValidationError) as context:
            self.github.update_pull_request_status(
                repository="test-org/test-repo",
                sha="abc123def456",
                state="success",
                target_url="https://example.com",
                description="Test description",
                context="",
            )
        self.assertTrue("Context is required" in str(context.exception))

    @patch("devops_deployment_security_gate.integrations.github.requests.post")
    def test_create_pull_request_comment_success(self, mock_post):
        """Test successful creation of pull request comment."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 123, "body": "Test comment"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test the method
        result = self.github.create_pull_request_comment(
            repository="test-org/test-repo", pr_number="123", body="Test comment"
        )

        self.assertEqual(result["id"], 123)
        self.assertEqual(result["body"], "Test comment")
        mock_post.assert_called_once()

    def test_create_pull_request_comment_validation(self):
        """Test validation in pull request comment creation."""
        # Test with invalid repository format
        with self.assertRaises(ValidationError) as context:
            self.github.create_pull_request_comment(
                repository="test-repo", pr_number="123", body="Test comment"
            )
        self.assertTrue("Invalid repository format" in str(context.exception))

        with self.assertRaises(ValidationError) as context:
            self.github.create_pull_request_comment(
                repository="test-org/test-repo", pr_number="", body="Test comment"
            )
        self.assertTrue("Invalid PR number" in str(context.exception))

        with self.assertRaises(ValidationError) as context:
            self.github.create_pull_request_comment(
                repository="test-org/test-repo", pr_number="123", body=""
            )
        self.assertTrue("Comment body is required" in str(context.exception))


class TestSonarQubeIntegration(unittest.TestCase):
    """Test cases for SonarQubeIntegration."""

    def setUp(self):
        """Set up test fixtures."""
        self.sonarqube = SonarQubeIntegration(
            url="https://sonarqube.example.com", token="test-token"
        )

    def test_initialization(self):
        """Test SonarQube integration initialization."""
        self.assertEqual(self.sonarqube.url, "https://sonarqube.example.com")
        self.assertEqual(self.sonarqube.token, "test-token")

    @patch("subprocess.run")
    def test_trigger_analysis_success(self, mock_run):
        """Test successful triggering of analysis via sonar-scanner."""
        mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")

        result = self.sonarqube.trigger_analysis("test-project", "main")

        self.assertEqual(result, "simulated_task_id")
        mock_run.assert_called_once()

    def test_trigger_analysis_validation(self):
        """Test validation in analysis triggering."""
        # Test with missing project key
        with self.assertRaises(ValueError) as context:
            self.sonarqube.trigger_analysis("", "main")
        self.assertTrue("Project key is required" in str(context.exception))

        # Test with missing branch name
        with self.assertRaises(ValueError) as context:
            self.sonarqube.trigger_analysis("test-project", "")
        self.assertTrue("Branch name is required" in str(context.exception))

    @patch("devops_deployment_security_gate.integrations.sonarqube.requests.get")
    def test_get_task_status_success(self, mock_get):
        """Test successful retrieval of task status."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"task": {"status": "SUCCESS"}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test the method
        result = self.sonarqube.get_task_status("task123")

        self.assertEqual(result, "SUCCESS")
        mock_get.assert_called_once()

    def test_get_task_status_validation(self):
        """Test validation in task status retrieval."""
        # Test with missing task ID
        with self.assertRaises(ValueError) as context:
            self.sonarqube.get_task_status("")
        self.assertTrue("Task ID is required" in str(context.exception))

    @patch(
        "devops_deployment_security_gate.integrations.sonarqube.SonarQubeIntegration.get_task_status"
    )
    def test_wait_for_analysis_completion_success(self, mock_get_status):
        """Test successful waiting for analysis completion."""
        # Mock the status progression
        mock_get_status.side_effect = ["PENDING", "IN_PROGRESS", "SUCCESS"]

        # Test the method (should not raise exception)
        self.sonarqube.wait_for_analysis_completion(
            "task123", max_wait_time=30, poll_interval=1
        )

        # Verify the method was called multiple times
        self.assertEqual(mock_get_status.call_count, 3)

    @patch(
        "devops_deployment_security_gate.integrations.sonarqube.SonarQubeIntegration.get_task_status"
    )
    def test_wait_for_analysis_completion_failure(self, mock_get_status):
        """Test waiting for analysis completion with failure."""
        # Mock the status progression
        mock_get_status.side_effect = ["PENDING", "FAILED"]

        with self.assertRaises(Exception) as context:
            self.sonarqube.wait_for_analysis_completion(
                "task123", max_wait_time=30, poll_interval=1
            )
        self.assertTrue("Analysis failed" in str(context.exception))

    @patch(
        "devops_deployment_security_gate.integrations.sonarqube.SonarQubeIntegration.get_task_status"
    )
    def test_wait_for_analysis_completion_timeout(self, mock_get_status):
        """Test waiting for analysis completion with timeout."""
        # Mock the status to always be in progress
        mock_get_status.return_value = "IN_PROGRESS"

        with self.assertRaises(Exception) as context:
            self.sonarqube.wait_for_analysis_completion(
                "task123", max_wait_time=2, poll_interval=1
            )
        self.assertTrue("Analysis timed out" in str(context.exception))

    def test_wait_for_analysis_completion_validation(self):
        """Test validation in waiting for analysis completion."""
        # Test with missing task ID
        with self.assertRaises(ValueError) as context:
            self.sonarqube.wait_for_analysis_completion("")
        self.assertTrue("Task ID is required" in str(context.exception))


class TestSlackIntegration(unittest.TestCase):
    """Test cases for SlackIntegration."""

    def setUp(self):
        """Set up test fixtures."""
        self.slack = SlackIntegration(token="test-token")

    def test_initialization(self):
        """Test Slack integration initialization."""
        self.assertEqual(self.slack.token, "test-token")

    @patch("devops_deployment_security_gate.integrations.slack.requests.post")
    def test_send_message_success(self, mock_post):
        """Test successful sending of message."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True, "ts": "1234567890.001200"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test the method
        result = self.slack.send_message(channel="#test-channel", text="Test message")

        self.assertTrue(result["ok"])
        self.assertEqual(result["ts"], "1234567890.001200")
        mock_post.assert_called_once()

    def test_send_message_validation(self):
        """Test validation in message sending."""
        # Test with missing channel
        with self.assertRaises(ValueError) as context:
            self.slack.send_message("", "Test message")
        self.assertTrue("Channel is required" in str(context.exception))

        # Test with missing text
        with self.assertRaises(ValueError) as context:
            self.slack.send_message("#test-channel", "")
        self.assertTrue("Message text is required" in str(context.exception))

    def test_send_security_alert_success(self):
        """Test successful sending of security alert."""
        # Mock the send_message method
        with patch.object(self.slack, "send_message") as mock_send:
            mock_send.return_value = {"ok": True, "ts": "1234567890.001200"}

            # Test BLOCK decision
            result = self.slack.send_security_alert(
                channel="#test-channel",
                pr_number="123",
                repository="test-org/test-repo",
                decision="BLOCK",
                critical_issues=2,
            )

            self.assertTrue(result["ok"])
            mock_send.assert_called_once()

            # Reset mock
            mock_send.reset_mock()

            # Test ALLOW decision
            result = self.slack.send_security_alert(
                channel="#test-channel",
                pr_number="123",
                repository="test-org/test-repo",
                decision="ALLOW",
            )

            self.assertTrue(result["ok"])
            mock_send.assert_called_once()

    def test_send_security_alert_validation(self):
        """Test validation in security alert sending."""
        # Test with missing channel
        with self.assertRaises(ValueError) as context:
            self.slack.send_security_alert("", "123", "test-org/test-repo", "BLOCK")
        self.assertTrue("Channel is required" in str(context.exception))

        # Test with missing PR number
        with self.assertRaises(ValueError) as context:
            self.slack.send_security_alert(
                "#test-channel", "", "test-org/test-repo", "BLOCK"
            )
        self.assertTrue("PR number is required" in str(context.exception))

        # Test with missing repository
        with self.assertRaises(ValueError) as context:
            self.slack.send_security_alert("#test-channel", "123", "", "BLOCK")
        self.assertTrue("Repository is required" in str(context.exception))

        # Test with missing decision
        with self.assertRaises(ValueError) as context:
            self.slack.send_security_alert(
                "#test-channel", "123", "test-org/test-repo", ""
            )
        self.assertTrue("Decision is required" in str(context.exception))

        # Test with invalid decision
        with self.assertRaises(ValueError) as context:
            self.slack.send_security_alert(
                "#test-channel", "123", "test-org/test-repo", "INVALID"
            )
        self.assertTrue(
            "Decision must be either 'ALLOW' or 'BLOCK'" in str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
