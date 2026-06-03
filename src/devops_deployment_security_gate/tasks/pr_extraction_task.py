"""
PR Extraction Task for the DevSecOps Deployment Gatekeeper.
"""

from typing import Any, Dict, Optional
from crewai import Agent
from .base_task import ConfigurableTask


class ExtractPRSecurityContextTask(ConfigurableTask):
    """Task for extracting PR security context."""

    def __init__(
        self,
        agent: Agent,
        config: Dict[str, Any],
        description: Optional[str] = None,
        expected_output: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            agent=agent,
            config=config,
            description=description,
            expected_output=expected_output,
            **kwargs,
        )
