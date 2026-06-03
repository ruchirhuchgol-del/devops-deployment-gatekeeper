"""
Slack integration for the DevSecOps Deployment Gatekeeper.
This module provides low-level Slack API integration functions.
"""

import requests
from typing import Dict, Any, Optional
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SlackIntegration:
    """Low-level Slack API integration."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize Slack integration.

        Args:
            token: Slack bot token
        """
        self.token = token or settings.slack_bot_token

    def send_message(
        self,
        channel: str,
        text: str,
        username: str = "DevSecOps Gatekeeper",
        icon_emoji: str = ":shield:",
    ) -> Dict[str, Any]:
        """
        Send a message to a Slack channel.

        Args:
            channel: Slack channel ID or name
            text: Message text
            username: Bot username
            icon_emoji: Bot icon emoji

        Returns:
            Dictionary containing message information

        Raises:
            requests.exceptions.RequestException: If the request fails
            Exception: If the Slack API returns an error
            ValueError: If required parameters are missing
        """
        # Validate inputs
        if not channel:
            raise ValueError("Channel is required")

        if not text:
            raise ValueError("Message text is required")

        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        payload = {
            "channel": channel,
            "text": text,
            "username": username,
            "icon_emoji": icon_emoji,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            if not data.get("ok"):
                raise Exception(f"Slack API error: {data.get('error')}")

            logger.info(f"Sent message to Slack channel {channel}")
            return data
        except requests.exceptions.RequestException as e:
            error_message = (
                f"Failed to send message to Slack channel {channel}: {str(e)}"
            )
            logger.error(error_message)
            raise
        except Exception as e:
            error_message = (
                f"Unexpected error sending message to Slack channel {channel}: {str(e)}"
            )
            logger.error(error_message)
            raise

    def send_security_alert(
        self,
        channel: str,
        pr_number: str,
        repository: str,
        decision: str,
        critical_issues: int = 0,
    ) -> Dict[str, Any]:
        """
        Send a security alert message to a Slack channel.

        Args:
            channel: Slack channel ID or name
            pr_number: Pull request number
            repository: Repository name
            decision: Security decision (ALLOW or BLOCK)
            critical_issues: Number of critical issues found

        Returns:
            Dictionary containing message information

        Raises:
            ValueError: If required parameters are missing
        """
        # Validate inputs
        if not channel:
            raise ValueError("Channel is required")

        if not pr_number:
            raise ValueError("PR number is required")

        if not repository:
            raise ValueError("Repository is required")

        if not decision:
            raise ValueError("Decision is required")

        if decision not in ["ALLOW", "BLOCK"]:
            raise ValueError("Decision must be either 'ALLOW' or 'BLOCK'")

        try:
            if decision == "BLOCK":
                message = (
                    f"❌ *Deployment BLOCKED* for PR #{pr_number} in {repository}\n"
                )
                message += f"• Critical vulnerabilities found: {critical_issues}\n"
                message += (
                    "• Please review and fix the critical issues before deployment."
                )
            else:
                message = (
                    f"✅ *Deployment APPROVED* for PR #{pr_number} in {repository}\n"
                )
                message += "• No critical vulnerabilities found\n"
                message += "• Safe to deploy"

            return self.send_message(
                channel=channel,
                text=message,
                username="DevSecOps Gatekeeper",
                icon_emoji=":shield:" if decision == "ALLOW" else ":no_entry:",
            )
        except Exception as e:
            error_message = (
                f"Failed to send security alert to Slack channel {channel}: {str(e)}"
            )
            logger.error(error_message)
            raise

    def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """
        Get information about a Slack channel.

        Args:
            channel: Slack channel ID or name

        Returns:
            Dictionary containing channel information

        Raises:
            requests.exceptions.RequestException: If the request fails
            Exception: If the Slack API returns an error
            ValueError: If channel is missing
        """
        # Validate inputs
        if not channel:
            raise ValueError("Channel is required")

        url = "https://slack.com/api/conversations.info"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        params = {"channel": channel}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            if not data.get("ok"):
                raise Exception(f"Slack API error: {data.get('error')}")

            logger.info(f"Retrieved info for Slack channel {channel}")
            return data
        except requests.exceptions.RequestException as e:
            error_message = f"Failed to get info for Slack channel {channel}: {str(e)}"
            logger.error(error_message)
            raise
        except Exception as e:
            error_message = f"Unexpected error retrieving info for Slack channel {channel}: {str(e)}"
            logger.error(error_message)
            raise


# Convenience functions
def get_slack_integration(token: Optional[str] = None) -> SlackIntegration:
    """
    Get a Slack integration instance.

    Args:
        token: Slack bot token

    Returns:
        SlackIntegration instance
    """
    return SlackIntegration(token)
