"""
Core Crew Implementation for the DevSecOps Deployment Gatekeeper.
"""

import os
import json
import yaml
from typing import Dict, Any, List, Optional
from functools import cached_property
from datetime import datetime, timezone
from crewai import Agent, Crew, Process, Task, LLM

from ..agents.pr_extractor import PRMetadataExtractionSpecialist
from ..agents.scanner_agent import SonarQubeSecurityScanner
from ..agents.decision_engine import SecurityPolicyDecisionEngine
from ..agents.notification_manager import SecurityAlertNotificationManager
from ..tasks.pr_extraction_task import ExtractPRSecurityContextTask
from ..tasks.scan_task import ExecuteSonarQubeSecurityScanTask
from ..tasks.decision_task import ApplySecurityGateDecisionTask
from ..tasks.notification_task import DeliverSecurityAlertNotificationsTask
from ..tools.sonarqube_scanner import SonarQubeSecurityScannerTool
from ..tools.github_tool import GitHubPRTool
from ..tools.slack_tool import SlackNotificationTool
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DevopsDeploymentSecurityGateCrew:
    """Enhanced DevSecOps Deployment Gatekeeper crew with robust error handling and monitoring."""

    def __init__(self, **kwargs):
        try:
            self.llm = LLM(
                model=settings.openai_model,
                temperature=settings.openai_temperature,
                api_key=settings.openai_api_key,
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise

        # Initialize tools
        try:
            self.sonarqube_tool = SonarQubeSecurityScannerTool()
            self.github_tool = GitHubPRTool()
            self.slack_tool = SlackNotificationTool()
        except Exception as e:
            logger.error(f"Failed to initialize tools: {str(e)}")
            raise

        # Initialize agents
        try:
            self._initialize_agents()
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
            raise

        # Initialize tasks
        try:
            self._initialize_tasks()
        except Exception as e:
            logger.error(f"Failed to initialize tasks: {str(e)}")
            raise

        logger.info("DevSecOps Deployment Gatekeeper Crew initialized")

    def _initialize_agents(self):
        """Initialize all agents with their tools and configurations."""
        self.pr_extractor = PRMetadataExtractionSpecialist(
            tools=[self.github_tool], llm=self.llm
        )

        self.scanner_agent = SonarQubeSecurityScanner(
            tools=[self.sonarqube_tool], llm=self.llm
        )

        self.decision_engine = SecurityPolicyDecisionEngine(llm=self.llm)

        self.notification_manager = SecurityAlertNotificationManager(
            tools=[self.slack_tool], llm=self.llm
        )

    def _initialize_tasks(self):
        """Initialize all tasks with their configurations."""
        # Load task configurations
        tasks_config_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "tasks.yaml"
        )
        if not os.path.exists(tasks_config_path):
            raise FileNotFoundError(
                f"Tasks configuration file not found: {tasks_config_path}"
            )

        try:
            with open(tasks_config_path, "r") as f:
                tasks_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in tasks configuration file: {str(e)}")

        if not isinstance(tasks_config, dict):
            raise ValueError(
                f"Tasks configuration is not a dictionary: {type(tasks_config)}"
            )

        # Create tasks without context first
        self.extract_pr_context_task = ExtractPRSecurityContextTask(
            agent=self.pr_extractor, config=tasks_config["extract_pr_security_context"]
        )

        self.execute_scan_task = ExecuteSonarQubeSecurityScanTask(
            agent=self.scanner_agent,
            config=tasks_config["execute_sonarqube_security_scan"],
        )

        self.apply_decision_task = ApplySecurityGateDecisionTask(
            agent=self.decision_engine,
            config=tasks_config["apply_security_gate_decision"],
        )

        self.deliver_notifications_task = DeliverSecurityAlertNotificationsTask(
            agent=self.notification_manager,
            config=tasks_config["deliver_security_alert_notifications"],
        )

        task_registry = {
            "extract_pr_security_context": self.extract_pr_context_task,
            "execute_sonarqube_security_scan": self.execute_scan_task,
            "apply_security_gate_decision": self.apply_decision_task,
            "deliver_security_alert_notifications": self.deliver_notifications_task,
        }
        for task_obj, config_key in [
            (self.execute_scan_task, "execute_sonarqube_security_scan"),
            (self.apply_decision_task, "apply_security_gate_decision"),
            (self.deliver_notifications_task, "deliver_security_alert_notifications"),
        ]:
            if "context" in tasks_config[config_key]:
                task_obj.context = [
                    task_registry[ctx_name]
                    for ctx_name in tasks_config[config_key]["context"]
                    if ctx_name in task_registry
                ]

    @cached_property
    def crew(self) -> Crew:
        """Creates the DevopsDeploymentSecurityGate crew with enhanced error handling."""
        return Crew(
            agents=[
                self.pr_extractor,
                self.scanner_agent,
                self.decision_engine,
                self.notification_manager,
            ],
            tasks=[
                self.extract_pr_context_task,
                self.execute_scan_task,
                self.apply_decision_task,
                self.deliver_notifications_task,
            ],
            process=Process.sequential,
            memory=True,
            cache=True,
            max_rpm=60,  # Rate limiting
            planning=True,  # Enable planning
            planning_llm=self.llm,
        )

    def run_security_gate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the security gate workflow with enhanced monitoring."""
        # Validate inputs
        required_fields = ["pr_number", "repository", "branch_name"]
        for field in required_fields:
            if field not in inputs or not inputs[field]:
                logger.error(f"Missing required input field: {field}")
                return {
                    "status": "failed",
                    "error": f"Missing required input field: {field}",
                    "pr_number": inputs.get("pr_number"),
                    "repository": inputs.get("repository"),
                    "timestamp": self._get_current_timestamp(),
                }

        logger.info(
            f"Starting security gate workflow for PR #{inputs.get('pr_number')}"
        )

        try:
            # Execute the crew
            crew_output = self.crew.kickoff(inputs=inputs)
            raw_output = getattr(crew_output, "raw", str(crew_output))
            try:
                result = json.loads(raw_output)
            except (json.JSONDecodeError, AttributeError):
                logger.warning(
                    "Failed to parse crew output as JSON, returning raw string"
                )
                result = {"raw_output": raw_output}

            # Process and return results
            workflow_result = {
                "status": "completed",
                "pr_number": inputs.get("pr_number"),
                "repository": inputs.get("repository"),
                "decision": (
                    result.get("decision") if isinstance(result, dict) else None
                ),
                "security_report": (
                    result.get("security_report") if isinstance(result, dict) else None
                ),
                "notifications": (
                    result.get("notifications") if isinstance(result, dict) else None
                ),
                "timestamp": self._get_current_timestamp(),
            }

            logger.info(
                f"Security gate workflow completed for PR #{inputs.get('pr_number')}"
            )
            return workflow_result

        except Exception as e:
            logger.error(f"Error in security gate workflow: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "pr_number": inputs.get("pr_number"),
                "repository": inputs.get("repository"),
                "timestamp": self._get_current_timestamp(),
            }

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat()
