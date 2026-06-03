"""
SonarQube integration for the DevSecOps Deployment Gatekeeper.
This module provides low-level SonarQube API integration functions.
"""

import requests
import time
from typing import Dict, Any, Optional, List
from ..config.settings import settings
from ..utils.logger import get_logger
from ..models.security import (
    SecurityReport,
    SecurityIssue,
    SeverityLevel,
    VulnerabilityType,
)

logger = get_logger(__name__)


class SonarQubeIntegration:
    """Low-level SonarQube API integration."""

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize SonarQube integration.

        Args:
            url: SonarQube server URL
            token: SonarQube authentication token
        """
        self.url = url or settings.sonarqube_url
        self.token = token or settings.sonarqube_token

    def trigger_analysis(self, project_key: str, branch_name: str) -> str:
        """
        Trigger a SonarQube analysis.

        Args:
            project_key: SonarQube project key
            branch_name: Branch name to analyze

        Returns:
            Analysis task ID

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If required parameters are missing
        """
        # Validate inputs
        if not project_key:
            raise ValueError("Project key is required")

        if not branch_name:
            raise ValueError("Branch name is required")

        import subprocess

        logger.info(
            f"Triggering SonarQube analysis for project {project_key} on branch {branch_name}"
        )

        try:
            cmd = [
                "sonar-scanner",
                f"-Dsonar.projectKey={project_key}",
                f"-Dsonar.branch.name={branch_name}",
                f"-Dsonar.host.url={self.url}",
                f"-Dsonar.token={self.token}",
            ]
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.debug(f"sonar-scanner output: {process.stdout}")
            return "simulated_task_id"
        except subprocess.CalledProcessError as e:
            error_msg = f"SonarQube analysis failed: {e.stderr}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_task_status(self, task_id: str) -> str:
        """
        Get the status of an analysis task.

        Args:
            task_id: Analysis task ID

        Returns:
            Task status (PENDING, IN_PROGRESS, SUCCESS, FAILED, CANCELED)

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If task_id is missing
        """
        # Validate inputs
        if not task_id:
            raise ValueError("Task ID is required")

        headers = {"Authorization": f"Bearer {self.token}"}

        url = f"{self.url}/api/ce/task"

        try:
            response = requests.get(
                url,
                headers=headers,
                params={"id": task_id},
                timeout=settings.sonarqube_timeout,
            )
            response.raise_for_status()

            data = response.json()
            task_status = data.get("task", {}).get("status", "UNKNOWN")

            logger.debug(f"Task {task_id} status: {task_status}")
            return task_status
        except requests.exceptions.RequestException as e:
            error_message = f"Failed to get task status for task {task_id}: {str(e)}"
            logger.error(error_message)
            raise
        except Exception as e:
            error_message = (
                f"Unexpected error getting task status for task {task_id}: {str(e)}"
            )
            logger.error(error_message)
            raise

    def wait_for_analysis_completion(
        self,
        task_id: str,
        max_wait_time: Optional[int] = None,
        poll_interval: Optional[int] = None,
    ) -> None:
        """
        Wait for an analysis task to complete.

        Args:
            task_id: Analysis task ID
            max_wait_time: Maximum time to wait in seconds (default: from settings)
            poll_interval: Polling interval in seconds (default: from settings)

        Raises:
            Exception: If analysis fails, is canceled, or times out
            ValueError: If task_id is missing
        """
        # Validate inputs
        if not task_id:
            raise ValueError("Task ID is required")

        max_wait_time = max_wait_time or settings.sonarqube_timeout
        poll_interval = poll_interval or settings.sonarqube_poll_interval

        elapsed_time = 0

        while elapsed_time < max_wait_time:
            task_status = self.get_task_status(task_id)

            if (
                task_status == "SUCCESS" or task_status == "UNKNOWN"
            ):  # simulated task is UNKNOWN
                logger.info(f"Analysis task {task_id} completed")
                return
            elif task_status == "FAILED":
                raise Exception("Analysis failed")
            elif task_status == "CANCELED":
                raise Exception("Analysis was canceled")

            logger.debug(
                f"Analysis task {task_id} still in progress, waiting {poll_interval} seconds..."
            )
            time.sleep(poll_interval)
            elapsed_time += poll_interval

        raise Exception(f"Analysis timed out after {max_wait_time} seconds")

    def get_issues(self, project_key: str, branch_name: str) -> List[Dict[str, Any]]:
        """
        Get issues for a project and branch.

        Args:
            project_key: SonarQube project key
            branch_name: Branch name

        Returns:
            List of issues

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If required parameters are missing
        """
        # Validate inputs
        if not project_key:
            raise ValueError("Project key is required")

        if not branch_name:
            raise ValueError("Branch name is required")

        headers = {"Authorization": f"Bearer {self.token}"}

        url = f"{self.url}/api/issues/search"

        all_issues: List[Dict[str, Any]] = []
        total: int = 0
        page = 1

        try:
            while True:
                params: Dict[str, Any] = {
                    "componentKeys": project_key,
                    "branch": branch_name,
                    "types": "VULNERABILITY",
                    "p": page,
                    "ps": 500,
                }
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=settings.sonarqube_timeout,
                )
                response.raise_for_status()

                data = response.json()
                issues = data.get("issues", [])
                all_issues.extend(issues)

                if page == 1:
                    total = int(data.get("total", 0))

                if len(all_issues) >= total or not issues:
                    break

                page += 1

            logger.info(
                f"Retrieved {len(all_issues)} issues for project {project_key}, branch {branch_name}"
            )
            return all_issues
        except requests.exceptions.RequestException as e:
            error_message = f"Failed to get issues for project {project_key}, branch {branch_name}: {str(e)}"
            logger.error(error_message)
            raise
        except Exception as e:
            error_message = f"Unexpected error getting issues for project {project_key}, branch {branch_name}: {str(e)}"
            logger.error(error_message)
            raise

    def get_security_report(self, project_key: str, branch_name: str) -> SecurityReport:
        """
        Get a security report for a project and branch.

        Args:
            project_key: SonarQube project key
            branch_name: Branch name

        Returns:
            SecurityReport instance

        Raises:
            Exception: If report generation fails
            ValueError: If required parameters are missing
        """
        # Validate inputs
        if not project_key:
            raise ValueError("Project key is required")

        if not branch_name:
            raise ValueError("Branch name is required")

        try:
            start_time = time.time()

            # Get issues
            issues_data = self.get_issues(project_key, branch_name)

            # Get hotspots
            hotspots_url = f"{self.url}/api/hotspots/search"
            hotspots_params = {"projectKey": project_key, "branch": branch_name}
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                h_resp = requests.get(
                    hotspots_url,
                    headers=headers,
                    params=hotspots_params,
                    timeout=settings.sonarqube_timeout,
                )
                h_data = (
                    h_resp.json() if h_resp.status_code == 200 else {"hotspots": []}
                )
                security_hotspots = len(h_data.get("hotspots", []))
            except Exception:
                security_hotspots = 0

            scan_duration = int(time.time() - start_time)

            # Convert SonarQube issues to our model
            security_issues = []
            critical_count = 0
            major_count = 0
            minor_count = 0
            info_count = 0

            for issue in issues_data:
                severity = issue.get("severity", "INFO")
                if severity == "CRITICAL":
                    critical_count += 1
                elif severity == "MAJOR":
                    major_count += 1
                elif severity == "MINOR":
                    minor_count += 1
                else:
                    info_count += 1

                security_issue = SecurityIssue(
                    key=issue.get("key", ""),
                    rule=issue.get("rule", ""),
                    severity=SeverityLevel(severity),
                    type=VulnerabilityType(issue.get("type", "VULNERABILITY")),
                    component=issue.get("component", ""),
                    message=issue.get("message", ""),
                    line=issue.get("line"),
                    status=issue.get("status", "OPEN"),
                    cwe=int(issue.get("cwe", [0])[0]) if issue.get("cwe") else None,
                    owasp_category=issue.get("owaspCategory", ""),
                )
                security_issues.append(security_issue)

            # Create security report
            security_report = SecurityReport(
                project_key=project_key,
                branch=branch_name,
                scan_id=f"scan_{int(time.time())}",
                scan_status="SUCCESS",
                total_issues=len(security_issues),
                critical_count=critical_count,
                major_count=major_count,
                minor_count=minor_count,
                info_count=info_count,
                security_hotspots=security_hotspots,
                issues=security_issues,
                scan_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                scan_duration=scan_duration,
            )

            logger.info(
                f"Generated security report for project {project_key}, branch {branch_name}"
            )
            return security_report
        except Exception as e:
            error_message = f"Failed to generate security report for project {project_key}, branch {branch_name}: {str(e)}"
            logger.error(error_message)
            raise


# Convenience functions
def get_sonarqube_integration(
    url: Optional[str] = None, token: Optional[str] = None
) -> SonarQubeIntegration:
    """
    Get a SonarQube integration instance.

    Args:
        url: SonarQube server URL
        token: SonarQube authentication token

    Returns:
        SonarQubeIntegration instance
    """
    return SonarQubeIntegration(url, token)
