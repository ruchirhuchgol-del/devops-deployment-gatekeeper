"""
Unit tests for main functionality.
"""

import unittest
import json
from unittest.mock import patch, MagicMock

from devops_deployment_security_gate.main import (
    setup_argument_parser,
    handle_run_command,
    handle_train_command,
    handle_replay_command,
    handle_test_command,
    handle_config_command,
)


class TestMainFunctionality(unittest.TestCase):
    """Test cases for main functionality."""

    def test_setup_argument_parser(self):
        """Test argument parser setup."""
        parser = setup_argument_parser()

        # Test that parser has the expected commands
        self.assertIsNotNone(parser)

        # Test run command
        args = parser.parse_args(
            [
                "run",
                "--pr-number",
                "123",
                "--repository",
                "test-org/test-repo",
                "--branch",
                "main",
            ]
        )
        self.assertEqual(args.command, "run")
        self.assertEqual(args.pr_number, "123")
        self.assertEqual(args.repository, "test-org/test-repo")
        self.assertEqual(args.branch, "main")

        # Test train command
        args = parser.parse_args(
            ["train", "--iterations", "5", "--data-path", "./data"]
        )
        self.assertEqual(args.command, "train")
        self.assertEqual(args.iterations, 5)
        self.assertEqual(args.data_path, "./data")

        # Test replay command
        args = parser.parse_args(["replay", "--task-id", "task123"])
        self.assertEqual(args.command, "replay")
        self.assertEqual(args.task_id, "task123")

        # Test test command
        args = parser.parse_args(["test", "--iterations", "3"])
        self.assertEqual(args.command, "test")
        self.assertEqual(args.iterations, 3)

        # Test config validate command
        args = parser.parse_args(["config", "validate"])
        self.assertEqual(args.command, "config")
        self.assertEqual(args.config_command, "validate")

    @patch("devops_deployment_security_gate.main.SecurityGateOrchestrator")
    def test_handle_run_command_success(self, mock_orchestrator_class):
        """Test successful handling of run command."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.run_security_check.return_value = {
            "status": "completed",
            "pr_number": "123",
            "repository": "test-org/test-repo",
        }
        mock_orchestrator_class.return_value = mock_orchestrator

        # Create mock args
        mock_args = MagicMock()
        mock_args.pr_number = "123"
        mock_args.repository = "test-org/test-repo"
        mock_args.branch = "main"
        mock_args.project_key = None
        mock_args.slack_channel = None
        mock_args.sonarqube_url = None
        mock_args.output = None

        # Test the function
        handle_run_command(mock_args)

        mock_orchestrator_class.assert_called_once_with(start_health_server=True)
        mock_orchestrator.run_security_check.assert_called_once()

    def test_handle_run_command_validation(self):
        """Test validation in run command handling."""
        # Test with invalid PR number
        mock_args = MagicMock()
        mock_args.pr_number = "abc"

        with self.assertRaises(ValueError) as context:
            handle_run_command(mock_args)
        self.assertTrue("Invalid PR number" in str(context.exception))

        # Test with missing repository
        mock_args.pr_number = "123"
        mock_args.repository = ""

        with self.assertRaises(ValueError) as context:
            handle_run_command(mock_args)
        self.assertTrue("Invalid repository format" in str(context.exception))

        # Test with missing branch
        mock_args.repository = "test-org/test-repo"
        mock_args.branch = ""

        with self.assertRaises(ValueError) as context:
            handle_run_command(mock_args)
        self.assertTrue("Branch name is required" in str(context.exception))

    @patch("devops_deployment_security_gate.main.open")
    @patch("devops_deployment_security_gate.main.os.path.exists")
    def test_handle_train_command_success(self, mock_exists, mock_open):
        """Test successful handling of train command."""
        # Mock file existence and content
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = (
            '{"test": "data"}'
        )

        # Create mock args
        mock_args = MagicMock()
        mock_args.iterations = 5
        mock_args.data_path = "./data"
        mock_args.output = None

        # Test the function (should not raise exception)
        handle_train_command(mock_args)

    def test_handle_train_command_validation(self):
        """Test validation in train command handling."""
        # Test with invalid iterations
        mock_args = MagicMock()
        mock_args.iterations = 0
        mock_args.data_path = "./data"

        with self.assertRaises(ValueError) as context:
            handle_train_command(mock_args)
        self.assertTrue(
            "Iterations must be a positive integer" in str(context.exception)
        )

        # Test with missing data path
        mock_args.iterations = 5
        mock_args.data_path = ""

        with self.assertRaises(ValueError) as context:
            handle_train_command(mock_args)
        self.assertTrue("Data path is required" in str(context.exception))

        # Test with non-existent data path
        mock_args.data_path = "./nonexistent"
        with patch(
            "devops_deployment_security_gate.main.os.path.exists", return_value=False
        ):
            with self.assertRaises(FileNotFoundError) as context:
                handle_train_command(mock_args)
            self.assertTrue("Data path does not exist" in str(context.exception))

    def test_handle_replay_command_success(self):
        """Test successful handling of replay command."""
        # Create mock args
        mock_args = MagicMock()
        mock_args.task_id = "task123"
        mock_args.output = None

        # Test the function (should not raise exception)
        handle_replay_command(mock_args)

    def test_handle_replay_command_validation(self):
        """Test validation in replay command handling."""
        # Test with missing task ID
        mock_args = MagicMock()
        mock_args.task_id = ""

        with self.assertRaises(ValueError) as context:
            handle_replay_command(mock_args)
        self.assertTrue("Task ID is required" in str(context.exception))

    @patch("devops_deployment_security_gate.main.os.path.exists")
    def test_handle_test_command_success(self, mock_exists):
        """Test successful handling of test command."""
        # Mock file existence
        mock_exists.return_value = False

        # Create mock args
        mock_args = MagicMock()
        mock_args.iterations = 3
        mock_args.model = "gpt-4"
        mock_args.data_path = None
        mock_args.output = None

        # Test the function (should not raise exception)
        handle_test_command(mock_args)

    def test_handle_test_command_validation(self):
        """Test validation in test command handling."""
        # Test with invalid iterations
        mock_args = MagicMock()
        mock_args.iterations = 0

        with self.assertRaises(ValueError) as context:
            handle_test_command(mock_args)
        self.assertTrue(
            "Iterations must be a positive integer" in str(context.exception)
        )

    @patch("devops_deployment_security_gate.main.os.path.exists")
    def test_handle_config_command_success(self, mock_exists):
        """Test successful handling of config command."""
        # Mock file existence
        mock_exists.return_value = True

        # Create mock args
        mock_args = MagicMock()
        mock_args.config_command = "validate"
        mock_args.env_file = ".env"

        # Test the function (should not raise exception)
        handle_config_command(mock_args)

    @patch("devops_deployment_security_gate.main.os.path.exists")
    def test_handle_config_command_validation(self, mock_exists):
        """Test validation in config command handling."""
        # Mock file non-existence
        mock_exists.return_value = False

        # Create mock args
        mock_args = MagicMock()
        mock_args.config_command = "validate"
        mock_args.env_file = "./nonexistent.env"

        with self.assertRaises(FileNotFoundError) as context:
            handle_config_command(mock_args)
        self.assertTrue("Environment file not found" in str(context.exception))


if __name__ == "__main__":
    unittest.main()
