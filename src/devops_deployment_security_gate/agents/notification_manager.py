"""
Security Alert Notification Manager Agent for the DevSecOps Deployment Gatekeeper.
"""

from typing import Dict, Any, List, Optional
from crewai import Agent
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SecurityAlertNotificationManager(Agent):
    """Agent specialized in sending security alert notifications."""

    def __init__(self, **kwargs):
        super().__init__(
            role="Security Alert Notification Manager",
            goal="Send structured security alerts to notification channels",
            backstory=(
                "You are a security communications specialist who understands the importance "
                "of rapid incident response. You've designed notification systems for enterprise "
                "development teams and know how to craft clear, actionable security alerts that "
                "help developers quickly understand and remediate vulnerabilities."
            ),
            allow_delegation=False,
            **kwargs,
        )

    def send_security_notification(
        self,
        decision: str,
        repository: str,
        pr_number: str,
        slack_channel: str,
        critical_issues: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send security notification to the specified channel."""
        try:
            # Validate inputs
            if not decision:
                raise ValueError("Decision is required")

            if not repository:
                raise ValueError("Repository is required")

            if not pr_number:
                raise ValueError("PR number is required")

            if not slack_channel:
                raise ValueError("Slack channel is required")

            logger.info(
                f"Sending security notification for PR #{pr_number} in {repository}"
            )

            # Use the Slack tool to send actual notification
            # Find the Slack tool in the agent's tools
            slack_tool = None
            if hasattr(self, "tools"):
                for tool in self.tools or []:
                    if hasattr(tool, "name") and tool.name == "Slack Notification Tool":
                        slack_tool = tool
                        break

            # Create message content
            if decision == "BLOCK":
                message = f"❌ Deployment BLOCKED for PR #{pr_number} in {repository}\n"
                message += f"Critical vulnerabilities found: {len(critical_issues) if critical_issues else 0}\n"
                message += (
                    "Please review and fix the critical issues before deployment."
                )
            else:
                message = (
                    f"✅ Deployment APPROVED for PR #{pr_number} in {repository}\n"
                )
                message += "No critical vulnerabilities found. Safe to deploy."

            if slack_tool:
                # Call the Slack tool to send actual notification
                notification_result = slack_tool._run(
                    message=message, channel=slack_channel
                )
            else:
                # Fallback to mock data if tool not available
                logger.error("Slack tool not wired correctly")
                raise RuntimeError("Slack tool not wired correctly")

            logger.info(f"Security notification sent to {slack_channel}")
            return notification_result
        except Exception as e:
            error_message = f"Error sending security notification: {str(e)}"
            logger.error(error_message)
            raise
