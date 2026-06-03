"""
Base task for the DevSecOps Deployment Gatekeeper.
"""

from typing import Any, Dict, Optional
from crewai import Task, Agent


class ConfigurableTask(Task):
    """A crewAI Task initialized from a YAML config dict."""

    def __init__(
        self,
        agent: Agent,
        config: Dict[str, Any],
        description: Optional[str] = None,
        expected_output: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            description=description
            or config.get("description", "No description provided"),
            expected_output=expected_output
            or config.get("expected_output", "Task output"),
            agent=agent,
            **kwargs,
        )
