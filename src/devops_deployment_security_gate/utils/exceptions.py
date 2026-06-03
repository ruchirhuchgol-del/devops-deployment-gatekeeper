"""
Custom exceptions for the DevSecOps Deployment Gatekeeper.
"""


class DevSecOpsError(Exception):
    """Base exception for DevSecOps Deployment Gatekeeper."""

    pass


class ConfigurationError(DevSecOpsError):
    """Raised when there's a configuration error."""

    pass


class ValidationError(DevSecOpsError):
    """Raised when validation fails."""

    pass


class SecurityScanError(DevSecOpsError):
    """Raised when security scan fails."""

    pass


class NotificationError(DevSecOpsError):
    """Raised when notification sending fails."""

    pass


class GitHubAPIError(DevSecOpsError):
    """Raised when GitHub API call fails."""

    pass


class SonarQubeAPIError(DevSecOpsError):
    """Raised when SonarQube API call fails."""

    pass


class SlackAPIError(DevSecOpsError):
    """Raised when Slack API call fails."""

    pass


class TaskExecutionError(DevSecOpsError):
    """Raised when task execution fails."""

    pass


class AgentInitializationError(DevSecOpsError):
    """Raised when agent initialization fails."""

    pass
