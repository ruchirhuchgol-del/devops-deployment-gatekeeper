"""
Validation utilities for the DevSecOps Deployment Gatekeeper.
"""

import re
from typing import Any, Optional
from .exceptions import ValidationError


def validate_github_repo_format(repo: str) -> bool:
    """Validate GitHub repository format (owner/repo)."""
    if not repo or not isinstance(repo, str):
        return False

    # Should contain exactly one slash and non-empty parts
    parts = repo.split("/")
    if len(parts) != 2:
        return False

    owner, repo_name = parts
    if not owner.strip() or not repo_name.strip():
        return False

    return True


def validate_pr_number(pr_number: str) -> bool:
    """Validate pull request number."""
    if not pr_number or not isinstance(pr_number, str):
        return False

    # Should be a positive integer
    try:
        num = int(pr_number)
        return num > 0
    except ValueError:
        return False


def validate_branch_name(branch: str) -> bool:
    """Validate branch name format."""
    if not branch or not isinstance(branch, str):
        return False

    # Basic validation: not empty, no whitespace at ends
    branch = branch.strip()
    if not branch:
        return False

    # Should not start or end with slash or dot
    if branch.startswith(("/", ".")) or branch.endswith(("/", ".")):
        return False

    # Should not contain double dots or consecutive slashes
    if ".." in branch or "//" in branch:
        return False

    return True


def validate_url(url: str) -> bool:
    """Validate URL format."""
    if not url or not isinstance(url, str):
        return False

    # Basic URL pattern
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return url_pattern.match(url) is not None


def validate_not_empty(value: Any, field_name: str) -> None:
    """Validate that a value is not empty."""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{field_name} cannot be empty")


def validate_positive_integer(value: Any, field_name: str) -> None:
    """Validate that a value is a positive integer."""
    try:
        num = int(value)
        if num <= 0:
            raise ValidationError(f"{field_name} must be a positive integer")
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid integer")


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False

    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    return email_pattern.match(email) is not None
