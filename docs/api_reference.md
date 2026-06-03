# DevSecOps Deployment Gatekeeper: API Reference

## Table of Contents
1. [Core Classes](#core-classes)
2. [Agents](#agents)
3. [Tools](#tools)
4. [Models](#models)
5. [Tasks](#tasks)
6. [Utilities](#utilities)

## Core Classes

### DevopsDeploymentSecurityGateCrew
Main class that orchestrates the security gate workflow.

**Methods:**
- `__init__(self, **kwargs)` - Initialize the crew
- `crew(self) -> Crew` - Create and return the crew instance
- `run_security_gate(self, inputs: Dict[str, Any]) -> Dict[str, Any]` - Run the security gate workflow

**Example:**
```python
from devops_deployment_security_gate.core.crew import DevopsDeploymentSecurityGateCrew

crew = DevopsDeploymentSecurityGateCrew()
result = crew.run_security_gate({
    'pr_number': '123',
    'repository': 'myorg/myrepo',
    'branch_name': 'feature-branch'
})
```

## Agents

### PRMetadataExtractionSpecialist
Agent specialized in extracting and validating GitHub PR metadata.

**Methods:**
- `extract_pr_context(self, pr_number: str, repository: str, branch_name: str) -> Dict[str, Any]` - Extract PR context information

### SonarQubeSecurityScanner
Agent specialized in executing SonarQube security scans.

**Methods:**
- `execute_security_scan(self, branch_name: str, project_key: str, sonarqube_url: str) -> SecurityReport` - Execute a security scan

### SecurityPolicyDecisionEngine
Agent that evaluates security scan results against organizational policies.

**Methods:**
- `evaluate_security_report(self, report: SecurityReport) -> SecurityDecision` - Evaluate a security report
- `apply_ml_enhancement(self, report: SecurityReport) -> SecurityReport` - Apply ML enhancements

### SecurityAlertNotificationManager
Agent specialized in sending security alert notifications.

**Methods:**
- `send_security_notification(self, decision: str, repository: str, pr_number: str, slack_channel: str, critical_issues: List[Dict] = None) -> Dict[str, Any]` - Send security notification

## Tools

### GitHubPRTool
Tool for interacting with GitHub PRs.

**Methods:**
- `_run(self, pr_number: str, repository: str, **kwargs) -> Dict[str, Any]` - Extract PR metadata from GitHub

### SonarQubeSecurityScannerTool
Tool for executing security scans using SonarQube.

**Methods:**
- `_run(self, branch_name: str, project_key: str, sonarqube_url: str = None, **kwargs) -> Dict[str, Any]` - Execute a security scan

### SlackNotificationTool
Tool for sending notifications to Slack.

**Methods:**
- `_run(self, message: str, channel: str, **kwargs) -> Dict[str, Any]` - Send notification to Slack channel

## Models

### SecurityIssue
Represents a single security issue found during scanning.

**Attributes:**
- `key: str` - Unique identifier
- `rule: str` - Rule that triggered the issue
- `severity: SeverityLevel` - Issue severity
- `type: VulnerabilityType` - Issue type
- `component: str` - Affected component
- `message: str` - Issue description
- `line: Optional[int]` - Line number
- `status: str` - Issue status
- `cwe: Optional[int]` - CWE identifier
- `owasp_category: Optional[str]` - OWASP category

### SecurityReport
Represents a complete security scan report.

**Attributes:**
- `project_key: str` - Project identifier
- `branch: str` - Branch name
- `scan_id: str` - Scan identifier
- `scan_status: str` - Scan status
- `total_issues: int` - Total issues found
- `critical_count: int` - Critical issues count
- `major_count: int` - Major issues count
- `minor_count: int` - Minor issues count
- `info_count: int` - Info issues count
- `security_hotspots: int` - Security hotspots count
- `issues: List[SecurityIssue]` - List of issues
- `scan_timestamp: str` - Scan timestamp
- `scan_duration: Optional[int]` - Scan duration

**Properties:**
- `has_critical_issues: bool` - Whether critical issues exist
- `has_major_issues: bool` - Whether major issues exist
- `security_score: float` - Calculated security score

### SecurityDecision
Represents a security decision made by the policy engine.

**Attributes:**
- `decision: str` - Decision (ALLOW or BLOCK)
- `reason: str` - Reason for the decision
- `policy_violations: List[str]` - Policy violations found
- `recommendations: List[str]` - Recommendations
- `override_allowed: bool` - Whether override is allowed
- `decision_timestamp: str` - Decision timestamp

## Tasks

### ExtractPRSecurityContextTask
Task for extracting PR security context.

### ExecuteSonarQubeSecurityScanTask
Task for executing SonarQube security scan.

### ApplySecurityGateDecisionTask
Task for applying security gate decision.

### DeliverSecurityAlertNotificationsTask
Task for delivering security alert notifications.

## Utilities

### Settings
Configuration settings class.

**Attributes:**
- `app_name: str` - Application name
- `debug: bool` - Debug mode
- `github_token: str` - GitHub token
- `sonarqube_url: str` - SonarQube URL
- `sonarqube_token: str` - SonarQube token
- `slack_bot_token: str` - Slack bot token
- `openai_api_key: str` - OpenAI API key
- And many more configuration options

### Logger
Logging utilities.

**Functions:**
- `setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> None` - Set up logging
- `get_logger(name: str) -> logging.Logger` - Get a logger instance

## Enums

### SeverityLevel
Severity levels for security issues.
- `CRITICAL`
- `MAJOR`
- `MINOR`
- `INFO`

### VulnerabilityType
Types of vulnerabilities.
- `VULNERABILITY`
- `SECURITY_HOTSPOT`
- `CODE_SMELL`
- `BUG`