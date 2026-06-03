"""
Shared test fixtures for the DevSecOps Deployment Gatekeeper test suite.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def no_health_server(monkeypatch):
    """Prevent health server from starting during any test."""
    monkeypatch.setattr(
        "devops_deployment_security_gate.core.orchestrator.start_health_server",
        lambda: None,
    )


@pytest.fixture
def mock_settings(monkeypatch):
    """Patch settings with test-safe values."""
    from devops_deployment_security_gate.config.settings import Settings

    test_settings = Settings(
        openai_api_key="test-openai-key",
        github_token="test-github-token",
        sonarqube_url="https://sonarqube.test",
        sonarqube_token="test-sonar-token",
        slack_bot_token="test-slack-token",
        critical_vulnerability_threshold=0,
        major_vulnerability_threshold=5,
        allow_manual_override=False,
        enable_metrics=False,
    )
    monkeypatch.setattr(
        "devops_deployment_security_gate.config.settings.settings", test_settings
    )
    return test_settings


@pytest.fixture
def sample_security_report():
    """Return a clean security report fixture."""
    from devops_deployment_security_gate.models.security import SecurityReport

    return SecurityReport(
        project_key="test-project",
        branch="feature-branch",
        scan_id="scan_test_001",
        scan_status="SUCCESS",
        total_issues=0,
        critical_count=0,
        major_count=0,
        minor_count=0,
        info_count=0,
        security_hotspots=0,
        issues=[],
        scan_timestamp="2025-01-01T00:00:00Z",
    )
