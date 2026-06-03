"""
Configuration settings for the DevSecOps Deployment Gatekeeper.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Settings
    app_name: str = "DevSecOps Deployment Gatekeeper"
    app_version: str = "1.0.0"
    debug: bool = False

    # Security Settings
    secret_key: str = "dev-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # GitHub Integration
    github_token: str = "dev-github-token"
    github_webhook_secret: str = "dev-webhook-secret"
    github_api_base_url: str = "https://api.github.com"

    # SonarQube Integration
    sonarqube_url: str = "https://sonarqube.example.com"
    sonarqube_token: str = "dev-sonarqube-token"
    sonarqube_timeout: int = 300
    sonarqube_poll_interval: int = 10

    # Slack Integration
    slack_bot_token: str = "dev-slack-token"
    slack_signing_secret: str = "dev-slack-signing-secret"
    slack_notification_channel: str = "#security-alerts"

    # AI/ML Settings
    openai_api_key: str = "dev-openai-key"
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.2

    # Security Policies
    critical_vulnerability_threshold: int = 0
    major_vulnerability_threshold: int = 5
    allow_manual_override: bool = False

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 8090

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance. Call get_settings.cache_clear() in tests to reset."""
    return Settings()


# Backward-compatible alias — do not call Settings() directly outside this module
settings = get_settings()
