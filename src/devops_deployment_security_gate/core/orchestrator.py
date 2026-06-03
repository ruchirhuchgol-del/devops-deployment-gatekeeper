"""
Orchestrator for the DevSecOps Deployment Gatekeeper.
This module coordinates the execution of the security gate workflow.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from .crew import DevopsDeploymentSecurityGateCrew
from ..config.settings import settings
from ..utils.logger import get_logger
from ..web import start_health_server

logger = get_logger(__name__)


class SecurityGateOrchestrator:
    """Orchestrator for managing the DevSecOps security gate workflow."""

    def __init__(self, start_health_server: bool = False):
        """Initialize the orchestrator."""
        self.security_gate: Optional[DevopsDeploymentSecurityGateCrew] = None
        self.health_server: Any = None
        self._initialize_crew()
        if start_health_server:
            self._start_health_server()

    def _initialize_crew(self) -> None:
        """Initialize the security gate crew."""
        try:
            self.security_gate = DevopsDeploymentSecurityGateCrew()
            logger.info("Security gate crew initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize security gate crew: {str(e)}")
            raise

    def _start_health_server(self) -> None:
        """Start the health check server."""
        try:
            self.health_server = start_health_server()
            if self.health_server:
                logger.info("Health check server started")
            else:
                logger.info("Health check server not started (disabled or failed)")
        except Exception as e:
            logger.error(f"Failed to start health check server: {str(e)}")

    def run_security_check(
        self,
        pr_number: str,
        repository: str,
        branch_name: str,
        project_key: Optional[str] = None,
        slack_channel: Optional[str] = None,
        sonarqube_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a security check on a pull request.

        Args:
            pr_number: The pull request number
            repository: The repository in format 'owner/repo'
            branch_name: The branch name to scan
            project_key: SonarQube project key (optional)
            slack_channel: Slack channel for notifications (optional)
            sonarqube_url: SonarQube URL (optional)

        Returns:
            Dict containing the security check results
        """
        try:
            # Prepare inputs
            inputs = {
                "pr_number": pr_number,
                "repository": repository,
                "branch_name": branch_name,
                "project_key": project_key
                or f"{repository.replace('/', '_')}_{branch_name}",
                "slack_channel": slack_channel or settings.slack_notification_channel,
                "sonarqube_url": sonarqube_url or settings.sonarqube_url,
            }

            logger.info(f"Starting security check for PR #{pr_number} in {repository}")

            if self.security_gate is None:
                raise RuntimeError("Security gate crew is not initialized")

            result = self.security_gate.run_security_gate(inputs)

            logger.info(f"Security check completed for PR #{pr_number}")
            return result

        except Exception as e:
            logger.error(f"Error running security check: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "pr_number": pr_number,
                "repository": repository,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def run_batch_security_checks(self, pr_list: list) -> Dict[str, Any]:
        """
        Run security checks on multiple pull requests.

        Args:
            pr_list: List of PR dictionaries with keys: pr_number, repository, branch_name

        Returns:
            Dict containing results for all security checks
        """
        results: Dict[str, Any] = {
            "status": "completed",
            "total_checks": len(pr_list),
            "successful_checks": 0,
            "failed_checks": 0,
            "results": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        for pr_info in pr_list:
            try:
                result = self.run_security_check(
                    pr_info["pr_number"],
                    pr_info["repository"],
                    pr_info["branch_name"],
                    pr_info.get("project_key"),
                    pr_info.get("slack_channel"),
                    pr_info.get("sonarqube_url"),
                )

                results["results"].append(result)

                if result.get("status") == "completed":
                    results["successful_checks"] += 1
                else:
                    results["failed_checks"] += 1

            except Exception as e:
                logger.error(f"Error running batch security check: {str(e)}")
                results["failed_checks"] += 1
                results["results"].append(
                    {
                        "status": "failed",
                        "error": str(e),
                        "pr_number": pr_info.get("pr_number"),
                        "repository": pr_info.get("repository"),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        return results

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current status of the security gate system.

        Returns:
            Dict containing system status information
        """
        return {
            "status": "operational",
            "version": settings.app_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "integrations": {
                "github": bool(settings.github_token),
                "sonarqube": bool(settings.sonarqube_token),
                "slack": bool(settings.slack_bot_token),
            },
        }


def main():
    """Main entry point for the orchestrator."""
    # Set up logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    orchestrator = SecurityGateOrchestrator()

    # If running as a script, check system status
    if len(sys.argv) == 1:
        status = orchestrator.get_system_status()
        print(json.dumps(status, indent=2))
        return

    # Handle command line arguments for running security checks
    if len(sys.argv) >= 4:
        pr_number = sys.argv[1]
        repository = sys.argv[2]
        branch_name = sys.argv[3]

        result = orchestrator.run_security_check(pr_number, repository, branch_name)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("status") == "completed" else 1)

    print("Usage: python orchestrator.py <pr_number> <repository> <branch_name>")
    sys.exit(1)


if __name__ == "__main__":
    main()
