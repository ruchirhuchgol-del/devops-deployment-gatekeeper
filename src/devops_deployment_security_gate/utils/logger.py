"""
Logging utilities for the DevSecOps Deployment Gatekeeper.
"""

import logging
import sys
from typing import Optional
from ..config.utils import setup_logging_from_config, get_logger as get_config_logger


def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> None:
    """
    Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
    """
    try:
        # Try to set up logging from config file
        setup_logging_from_config()
    except Exception as e:
        # Fallback to basic configuration
        if format_string is None:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format=format_string,
            handlers=[logging.StreamHandler(sys.stdout)],
        )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return get_config_logger(name)
