"""
Slack Tool for the DevSecOps Deployment Gatekeeper.
"""

from typing import Dict, Any, Optional
from ..utils.logger import get_logger
from ..integrations.slack import get_slack_integration
from .base_tool import DevSecOpsBaseTool

logger = get_logger(__name__)


class SlackNotificationTool(DevSecOpsBaseTool):
    """Tool for sending notifications to Slack."""

    def __init__(self, **kwargs):
        """Initialize the Slack notification tool."""
        super().__init__(
            name="Slack Notification Tool",
            description="Tool for sending security alerts to Slack channels",
            **kwargs,
        )

    def _run(self, message: str, channel: str, **kwargs) -> Dict[str, Any]:
        """Send notification to Slack channel."""
        logger.info(f"Sending notification to Slack channel {channel}")

        try:
            # Validate required parameters
            self._validate_required_params(
                {"message": message, "channel": channel}, ["message", "channel"]
            )

            # Get Slack integration
            slack = get_slack_integration()

            # Send message
            response = slack.send_message(channel, message)

            result = {
                "channel": channel,
                "message": message,
                "timestamp": response.get("ts", ""),
                "status": "sent" if response.get("ok") else "failed",
                "recipient_count": 1,  # Slack doesn't provide this directly
            }

            logger.info(f"Successfully sent notification to {channel}")
            return result
        except Exception as e:
            error_message = f"Error sending notification to {channel}: {str(e)}"
            self._handle_error(e, error_message)
