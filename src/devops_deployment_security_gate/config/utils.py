"""
Utility functions for the DevSecOps Deployment Gatekeeper.
"""

import logging
import logging.config
import yaml
import os
from typing import Optional
from .settings import settings


def setup_logging_from_config(config_path: Optional[str] = None) -> None:
    """
    Set up logging configuration from YAML file.

    Args:
        config_path: Path to logging configuration file. If None, uses default.
    """
    if config_path is None:
        # Look for config in project directory
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "logging.yaml",
        )

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                logging.config.dictConfig(config)
            logging.getLogger(__name__).info(f"Logging configured from {config_path}")
        except Exception as e:
            logging.getLogger(__name__).error(
                f"Failed to load logging config from {config_path}: {e}"
            )
            setup_default_logging()
    else:
        logging.getLogger(__name__).warning(
            f"Logging config file not found: {config_path}"
        )
        setup_default_logging()


def setup_default_logging() -> None:
    """Set up default logging configuration."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=settings.log_format,
    )
    logging.getLogger(__name__).info("Default logging configuration applied")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with proper configuration.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def validate_environment() -> bool:
    """
    Validate that required environment variables are set.

    Returns:
        True if all required environment variables are set, False otherwise
    """
    logger = get_logger(__name__)

    required_vars = {
        "OPENAI_API_KEY": settings.openai_api_key,
        "GITHUB_TOKEN": settings.github_token,
        "SONARQUBE_URL": settings.sonarqube_url,
        "SONARQUBE_TOKEN": settings.sonarqube_token,
        "SLACK_BOT_TOKEN": settings.slack_bot_token,
    }

    missing_vars = []
    for var_name, var_value in required_vars.items():
        if not var_value or var_value.startswith("dev-"):
            missing_vars.append(var_name)

    if missing_vars:
        logger.warning(f"Missing or invalid environment variables: {missing_vars}")
        return False

    logger.info("All required environment variables are set")
    return True
