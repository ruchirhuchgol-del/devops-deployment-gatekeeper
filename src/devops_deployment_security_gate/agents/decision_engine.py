"""
Security Policy Decision Engine Agent for the DevSecOps Deployment Gatekeeper.
"""

from typing import Optional
from crewai import Agent
from ..models.security import SecurityReport, SecurityDecision
from ..config.settings import get_settings
from ..utils.logger import get_logger
from ..core.policy_evaluator import PolicyEvaluator

logger = get_logger(__name__)


class SecurityPolicyDecisionEngine(Agent):
    """Security policy decision engine delegating to PolicyEvaluator."""

    def __init__(self, **kwargs):
        super().__init__(
            role="Security Policy Decision Engine",
            goal="Evaluate security scan results against organizational policies and make deployment decisions",
            backstory=(
                "You are a senior security architect with expertise in threat modeling, "
                "compliance frameworks, and secure development practices. You analyze "
                "security reports to make data-driven decisions about deployment readiness."
            ),
            allow_delegation=False,
            **kwargs,
        )
        cfg = get_settings()
        object.__setattr__(
            self,
            "_evaluator",
            PolicyEvaluator(
                critical_threshold=cfg.critical_vulnerability_threshold,
                major_threshold=cfg.major_vulnerability_threshold,
                allow_override=cfg.allow_manual_override,
            ),
        )

    @property
    def evaluator(self) -> PolicyEvaluator:
        return object.__getattribute__(self, "_evaluator")

    def evaluate_security_report(self, report: SecurityReport) -> SecurityDecision:
        """Evaluate a security report against organizational policies."""
        try:
            return self.evaluator.evaluate(report)
        except Exception as e:
            error_message = f"Error evaluating security report: {str(e)}"
            logger.error(error_message)
            from datetime import datetime, timezone

            return SecurityDecision(
                decision="BLOCK",
                reason=error_message,
                policy_violations=[f"System error: {str(e)}"],
                recommendations=[
                    "Investigate system error and retry security evaluation"
                ],
                override_allowed=False,
                decision_timestamp=datetime.now(timezone.utc).isoformat(),
            )

    def apply_ml_enhancement(self, report: SecurityReport) -> SecurityReport:
        """Placeholder for ML integration."""
        logger.debug("Applying ML enhancements to security report")
        return report
