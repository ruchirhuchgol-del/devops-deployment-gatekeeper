"""
Policy evaluation service — deterministic, LLM-free security gate logic.
"""

from typing import List, Optional
from datetime import datetime, timezone
from ..models.security import SecurityReport, SecurityDecision
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PolicyEvaluator:
    """Stateless policy evaluator. No LLM, no Agent inheritance."""

    def __init__(
        self,
        critical_threshold: Optional[int] = None,
        major_threshold: Optional[int] = None,
        allow_override: Optional[bool] = None,
    ):
        self.critical_threshold = (
            critical_threshold
            if critical_threshold is not None
            else settings.critical_vulnerability_threshold
        )
        self.major_threshold = (
            major_threshold
            if major_threshold is not None
            else settings.major_vulnerability_threshold
        )
        self.allow_override = (
            allow_override
            if allow_override is not None
            else settings.allow_manual_override
        )
        self._HIGH_RISK_CWES = {79, 89, 90, 200, 352}

    def evaluate(self, report: SecurityReport) -> SecurityDecision:
        if not isinstance(report, SecurityReport):
            raise TypeError("Expected SecurityReport instance")

        violations: List[str] = []
        recommendations: List[str] = []

        if report.critical_count > self.critical_threshold:
            violations.append(
                f"Critical vulnerability threshold exceeded: "
                f"{report.critical_count} > {self.critical_threshold}"
            )
            recommendations.append(
                "Resolve all critical vulnerabilities before deployment"
            )

        if report.major_count > self.major_threshold:
            violations.append(
                f"Major vulnerability threshold exceeded: "
                f"{report.major_count} > {self.major_threshold}"
            )
            recommendations.append(
                f"Reduce major vulnerabilities to {self.major_threshold} or below"
            )

        high_risk = [
            i
            for i in report.issues
            if i.severity.value == "CRITICAL" and i.cwe in self._HIGH_RISK_CWES
        ]
        if high_risk:
            violations.append(f"Found {len(high_risk)} critical high-risk CWEs")
            recommendations.append("High-risk CWEs require immediate remediation")

        if report.security_score < 70.0:
            violations.append(f"Security score {report.security_score} < 70")
            recommendations.append("Improve security score to 70 or higher")

        if report.security_hotspots > 10:
            recommendations.append("Review and address security hotspots")

        decision = "ALLOW" if not violations else "BLOCK"
        return SecurityDecision(
            decision=decision,
            reason=(
                "; ".join(violations) if violations else "No policy violations detected"
            ),
            policy_violations=violations,
            recommendations=recommendations,
            override_allowed=self.allow_override,
            decision_timestamp=datetime.now(timezone.utc).isoformat(),
        )
