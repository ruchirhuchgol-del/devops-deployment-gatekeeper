"""DevSecOps Deployment Gatekeeper - Automated Security Checks for CI/CD."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("devops-deployment-security-gate")
except importlib.metadata.PackageNotFoundError:
    __version__ = "1.0.0"

from .core.crew import DevopsDeploymentSecurityGateCrew

__all__ = ["DevopsDeploymentSecurityGateCrew"]
