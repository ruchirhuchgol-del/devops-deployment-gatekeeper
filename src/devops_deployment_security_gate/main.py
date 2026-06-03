#!/usr/bin/env python
"""
DevSecOps Deployment Gatekeeper - Automated Security Checks for CI/CD
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, Any
from dotenv import load_dotenv

from .core.crew import DevopsDeploymentSecurityGateCrew
from .core.orchestrator import SecurityGateOrchestrator
from .config.settings import settings

# Load environment variables
load_dotenv()


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="DevSecOps Deployment Gatekeeper - Automated Security Checks for CI/CD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run security gate on a pull request
  python -m devops_deployment_security_gate run --pr-number 123 --repository myorg/myrepo --branch feature-branch

  # Train the crew with custom data
  python -m devops_deployment_security_gate train --iterations 10 --data-path ./training_data/

  # Replay a specific task execution
  python -m devops_deployment_security_gate replay --task-id task_12345

  # Test the system with sample data
  python -m devops_deployment_security_gate test --iterations 5 --model gpt-4
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the security gate workflow")
    run_parser.add_argument("--pr-number", required=True, help="Pull request number")
    run_parser.add_argument(
        "--repository", required=True, help="Repository name (owner/repo)"
    )
    run_parser.add_argument("--branch", required=True, help="Branch name")
    run_parser.add_argument("--project-key", help="SonarQube project key")
    run_parser.add_argument("--slack-channel", help="Slack channel for notifications")
    run_parser.add_argument("--sonarqube-url", help="SonarQube URL override")
    run_parser.add_argument("--output", help="Output file path for results")

    # Train command
    train_parser = subparsers.add_parser(
        "train", help="Train the crew with custom data"
    )
    train_parser.add_argument(
        "--iterations", type=int, required=True, help="Number of training iterations"
    )
    train_parser.add_argument(
        "--data-path", required=True, help="Path to training data"
    )
    train_parser.add_argument("--output", help="Output file path for trained model")

    # Replay command
    replay_parser = subparsers.add_parser(
        "replay", help="Replay a specific task execution"
    )
    replay_parser.add_argument("--task-id", required=True, help="Task ID to replay")
    replay_parser.add_argument("--output", help="Output file path for results")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test the system with sample data")
    test_parser.add_argument(
        "--iterations", type=int, default=1, help="Number of test iterations"
    )
    test_parser.add_argument("--model", default="gpt-4", help="OpenAI model to use")
    test_parser.add_argument("--data-path", help="Path to test data")
    test_parser.add_argument("--output", help="Output file path for test results")

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(
        dest="config_command", required=True
    )

    config_validate = config_subparsers.add_parser(
        "validate", help="Validate configuration"
    )
    config_validate.add_argument("--env-file", help="Environment file to validate")

    return parser


def handle_run_command(args) -> None:
    """Handle the run command."""
    # Validate inputs
    if not args.pr_number or not args.pr_number.isdigit():
        raise ValueError("Invalid PR number. Must be a positive integer.")

    if not args.repository or "/" not in args.repository:
        raise ValueError("Invalid repository format. Must be in 'owner/repo' format.")

    if not args.branch:
        raise ValueError("Branch name is required.")

    # Use orchestrator for running the security gate
    orchestrator = SecurityGateOrchestrator(start_health_server=True)
    result = orchestrator.run_security_check(
        pr_number=args.pr_number,
        repository=args.repository,
        branch_name=args.branch,
        project_key=args.project_key,
        slack_channel=args.slack_channel,
        sonarqube_url=args.sonarqube_url,
    )

    if args.output:
        try:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to {args.output}")
        except Exception as e:
            logging.error(f"Failed to write output to file: {str(e)}")
            print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))


def handle_train_command(args) -> None:
    """Handle the train command."""
    # Validate inputs
    if args.iterations <= 0:
        raise ValueError("Iterations must be a positive integer.")

    if not args.data_path:
        raise ValueError("Data path is required.")

    if not os.path.exists(args.data_path):
        raise FileNotFoundError(f"Data path does not exist: {args.data_path}")

    print(
        f"Training crew with {args.iterations} iterations using data from {args.data_path}"
    )
    # Implementation would go here


def handle_replay_command(args) -> None:
    """Handle the replay command."""
    # Validate inputs
    if not args.task_id:
        raise ValueError("Task ID is required.")

    print(f"Replaying task {args.task_id}")
    # Implementation would go here


def handle_test_command(args) -> None:
    """Handle the test command."""
    # Validate inputs
    if args.iterations <= 0:
        raise ValueError("Iterations must be a positive integer.")

    print(f"Testing system with {args.iterations} iterations using model {args.model}")
    # Implementation would go here


def handle_config_command(args) -> None:
    """Handle the config command."""
    if args.config_command == "validate":
        env_file = args.env_file or ".env"
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"Environment file not found: {env_file}")

        print(f"Validating configuration from {env_file}")
        # Implementation would validate environment variables and settings
        print("Configuration validation completed")


def setup_logging(level: str = "INFO") -> None:
    """Set up basic logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> None:
    """Main entry point."""
    # Set up logging
    setup_logging(level=settings.log_level)

    # Parse arguments
    parser = setup_argument_parser()
    args = parser.parse_args()

    # Handle commands
    try:
        if args.command == "run":
            handle_run_command(args)
        elif args.command == "train":
            handle_train_command(args)
        elif args.command == "replay":
            handle_replay_command(args)
        elif args.command == "test":
            handle_test_command(args)
        elif args.command == "config":
            handle_config_command(args)
        else:
            parser.print_help()
            sys.exit(1)
    except ValueError as e:
        logging.error(f"Validation error: {str(e)}")
        sys.exit(1)
    except FileNotFoundError as e:
        logging.error(f"File not found: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error executing command: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
