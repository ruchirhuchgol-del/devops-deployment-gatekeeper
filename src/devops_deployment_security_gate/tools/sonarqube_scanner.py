"""
SonarQube Scanner Tool for the DevSecOps Deployment Gatekeeper.
"""

from typing import Dict, Any, Optional
from ..config.settings import settings
from ..utils.logger import get_logger
from ..integrations.sonarqube import get_sonarqube_integration
from .base_tool import DevSecOpsBaseTool

logger = get_logger(__name__)


class SonarQubeSecurityScannerTool(DevSecOpsBaseTool):
    """Tool for executing SonarQube security scans."""

    def __init__(self, **kwargs):
        """Initialize the SonarQube scanner tool."""
        super().__init__(
            name="SonarQube Security Scanner",
            description="Tool for executing security scans using SonarQube",
            **kwargs,
        )

    def _run(
        self,
        branch_name: str,
        project_key: str,
        sonarqube_url: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a security scan using SonarQube."""
        url = sonarqube_url or settings.sonarqube_url
        logger.info(
            f"Executing security scan on {url} for project {project_key}, branch {branch_name}"
        )

        try:
            # Validate required parameters
            self._validate_required_params(
                {"branch_name": branch_name, "project_key": project_key},
                ["branch_name", "project_key"],
            )

            # Get SonarQube integration
            sonarqube = get_sonarqube_integration(url)

            # Trigger the analysis
            analysis_task_id = sonarqube.trigger_analysis(project_key, branch_name)

            # Poll for completion
            sonarqube.wait_for_analysis_completion(analysis_task_id)

            # Get the security report
            security_report = sonarqube.get_security_report(project_key, branch_name)

            logger.info(f"Security scan completed for project {project_key}")
            return security_report.model_dump()
        except Exception as e:
            error_message = (
                f"Error executing security scan for project {project_key}: {str(e)}"
            )
            self._handle_error(e, error_message)
