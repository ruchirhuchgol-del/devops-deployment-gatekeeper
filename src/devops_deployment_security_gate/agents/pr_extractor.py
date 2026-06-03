"""
PR Metadata Extraction Specialist Agent for the DevSecOps Deployment Gatekeeper.
"""

from typing import Dict, Any, List
from crewai import Agent
from ..config.settings import settings
from ..utils.logger import get_logger
from ..utils.validators import validate_github_repo_format, validate_pr_number
from ..utils.exceptions import ValidationError

logger = get_logger(__name__)


class PRMetadataExtractionSpecialist(Agent):
    """Agent specialized in extracting and validating GitHub PR metadata."""

    def __init__(self, **kwargs):
        super().__init__(
            role="PR Metadata Extraction Specialist",
            goal="Extract and validate pull request metadata from GitHub",
            backstory=(
                "You are a CI/CD integration expert specialized in GitHub workflow automation. "
                "You understand the critical metadata required for security scanning and have extensive "
                "experience in parsing PR data to ensure accurate security analysis."
            ),
            allow_delegation=False,
            **kwargs,
        )

    def extract_pr_context(
        self, pr_number: str, repository: str, branch_name: str
    ) -> Dict[str, Any]:
        """Extract and validate PR context information."""
        try:
            if not validate_pr_number(str(pr_number)):
                raise ValidationError(f"Invalid PR number: '{pr_number}'.")
            if not validate_github_repo_format(repository):
                raise ValidationError(
                    f"Invalid repository format '{repository}'. Must be 'owner/repo'."
                )
            if not branch_name:
                raise ValidationError("Branch name is required")

            logger.info(f"Extracting PR context for PR #{pr_number} in {repository}")

            # Use the GitHub tool to get actual PR data
            # Find the GitHub tool in the agent's tools
            github_tool = None
            if hasattr(self, "tools"):
                for tool in self.tools or []:
                    if hasattr(tool, "name") and tool.name == "GitHub PR Tool":
                        github_tool = tool
                        break

            if github_tool:
                # Call the GitHub tool to get actual PR data
                pr_data = github_tool._run(pr_number=pr_number, repository=repository)
                pr_context = {
                    "pr_number": pr_data.get("pr_number"),
                    "repository": pr_data.get("repository"),
                    "branch_name": pr_data.get("branch_name"),
                    "commit_sha": pr_data.get("commit_sha"),
                    "changed_files": pr_data.get("changed_files", []),
                    "author": pr_data.get("author"),
                    "title": pr_data.get("title"),
                    "description": pr_data.get("description"),
                    "status": pr_data.get("status"),
                }
            else:
                # Fallback to mock data if tool not available
                logger.error("GitHub PR tool not wired correctly")
                raise RuntimeError("GitHub PR tool not wired correctly")

            logger.info(f"PR context extracted successfully for PR #{pr_number}")
            return pr_context
        except Exception as e:
            error_message = f"Error extracting PR context: {str(e)}"
            logger.error(error_message)
            raise
