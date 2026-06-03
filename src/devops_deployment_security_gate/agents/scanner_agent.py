"""
SonarQube Security Scanner Agent for the DevSecOps Deployment Gatekeeper.
"""

from typing import Dict, Any, List
from crewai import Agent
from ..config.settings import settings
from ..models.security import (
    SecurityReport,
    SecurityIssue,
    SeverityLevel,
    VulnerabilityType,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SonarQubeSecurityScanner(Agent):
    """Agent specialized in executing SonarQube security scans."""

    def __init__(self, **kwargs):
        super().__init__(
            role="SonarQube Security Scanner",
            goal="Execute comprehensive security analysis using SonarQube",
            backstory=(
                "You are a security engineer with extensive experience in static code "
                "analysis and vulnerability detection. You've mastered SonarQube's capabilities "
                "and understand how to interpret security findings to make critical deployment "
                "decisions."
            ),
            allow_delegation=False,
            **kwargs,
        )

    def execute_security_scan(
        self, branch_name: str, project_key: str, sonarqube_url: str
    ) -> SecurityReport:
        """Execute a security scan using SonarQube."""
        try:
            # Validate inputs
            if not branch_name:
                raise ValueError("Branch name is required")

            if not project_key:
                raise ValueError("Project key is required")

            if not sonarqube_url:
                raise ValueError("SonarQube URL is required")

            logger.info(
                f"Executing security scan for branch {branch_name} on project {project_key}"
            )

            # Use the SonarQube tool to get actual scan data
            # Find the SonarQube tool in the agent's tools
            sonarqube_tool = None
            if hasattr(self, "tools"):
                for tool in self.tools or []:
                    if (
                        hasattr(tool, "name")
                        and tool.name == "SonarQube Security Scanner"
                    ):
                        sonarqube_tool = tool
                        break

            if sonarqube_tool:
                # Call the SonarQube tool to get actual scan data
                scan_result = sonarqube_tool._run(
                    branch_name=branch_name,
                    project_key=project_key,
                    sonarqube_url=sonarqube_url,
                )

                # Convert the result to SecurityReport
                security_report = SecurityReport(**scan_result)
            else:
                # Fallback to mock data if tool not available
                logger.error("SonarQube tool not wired correctly")
                raise RuntimeError("SonarQube tool not wired correctly")

            logger.info(f"Security scan completed for branch {branch_name}")
            return security_report
        except Exception as e:
            error_message = f"Error executing security scan: {str(e)}"
            logger.error(error_message)
            raise
