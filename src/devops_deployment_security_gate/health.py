"""
Health check endpoint for the DevSecOps Deployment Gatekeeper.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any
from .config.settings import settings
from .utils.logger import get_logger

logger = get_logger(__name__)


def get_health_status() -> Dict[str, Any]:
    """
    Get the health status of the application.

    Returns:
        Dict containing health status information
    """
    try:
        # Check if required environment variables are set
        env_checks = {
            "openai_api_key": bool(
                settings.openai_api_key and settings.openai_api_key != "dev-openai-key"
            ),
            "github_token": bool(
                settings.github_token and settings.github_token != "dev-github-token"
            ),
            "sonarqube_token": bool(
                settings.sonarqube_token
                and settings.sonarqube_token != "dev-sonarqube-token"
            ),
            "slack_bot_token": bool(
                settings.slack_bot_token
                and settings.slack_bot_token != "dev-slack-token"
            ),
        }

        # Overall health status
        healthy = all(env_checks.values())

        health_status = {
            "status": "healthy" if healthy else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.app_version,
            "service": settings.app_name,
            "checks": {
                "environment_variables": {
                    "status": "pass" if all(env_checks.values()) else "fail",
                    "details": env_checks,
                },
                "application": {
                    "status": "pass",
                    "details": {
                        "debug_mode": settings.debug,
                        "log_level": settings.log_level,
                    },
                },
            },
        }

        logger.info(f"Health check completed: {health_status['status']}")
        return health_status

    except Exception as e:
        logger.error(f"Error during health check: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.app_version,
            "service": settings.app_name,
            "error": str(e),
        }


def get_metrics() -> Dict[str, Any]:
    """
    Get application metrics.

    Returns:
        Dict containing metrics information
    """
    try:
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.app_version,
            "service": settings.app_name,
            "settings": {
                "openai_model": settings.openai_model,
                "sonarqube_timeout": settings.sonarqube_timeout,
                "sonarqube_poll_interval": settings.sonarqube_poll_interval,
            },
        }

        logger.info("Metrics retrieved successfully")
        return metrics

    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    # Print health status when run directly
    health = get_health_status()
    print(json.dumps(health, indent=2))
