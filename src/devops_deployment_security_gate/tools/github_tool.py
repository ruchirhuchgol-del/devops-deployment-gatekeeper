"""
GitHub Tool for the DevSecOps Deployment Gatekeeper.
"""

from typing import Dict, Any, Optional
from ..utils.logger import get_logger
from ..integrations.github import get_github_integration
from .base_tool import DevSecOpsBaseTool

logger = get_logger(__name__)


class GitHubPRTool(DevSecOpsBaseTool):
    """Tool for interacting with GitHub PRs."""

    def __init__(self, **kwargs):
        """Initialize the GitHub PR tool."""
        super().__init__(
            name="GitHub PR Tool",
            description="Tool for extracting metadata from GitHub Pull Requests",
            **kwargs,
        )

    def _run(self, pr_number: str, repository: str, **kwargs) -> Dict[str, Any]:
        """Extract PR metadata from GitHub."""
        logger.info(f"Extracting metadata for PR #{pr_number} in {repository}")

        try:
            # Validate required parameters
            self._validate_required_params(
                {"pr_number": pr_number, "repository": repository},
                ["pr_number", "repository"],
            )

            # Get GitHub integration
            github = get_github_integration()

            # Get PR details
            pr_data = github.get_pull_request(repository, pr_number)

            # Get PR files
            files_data = github.get_pull_request_files(repository, pr_number)

            # Combine data
            result = {
                "pr_number": pr_number,
                "repository": repository,
                "branch_name": pr_data.get("head", {}).get("ref", ""),
                "commit_sha": pr_data.get("head", {}).get("sha", ""),
                "changed_files": [file.get("filename", "") for file in files_data],
                "author": pr_data.get("user", {}).get("login", ""),
                "title": pr_data.get("title", ""),
                "description": pr_data.get("body", ""),
                "status": pr_data.get("state", "open"),
            }

            logger.info(f"Successfully extracted metadata for PR #{pr_number}")
            return result
        except Exception as e:
            error_message = f"Error extracting metadata for PR #{pr_number}: {str(e)}"
            self._handle_error(e, error_message)
