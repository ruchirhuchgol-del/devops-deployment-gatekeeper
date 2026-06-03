# DevSecOps Deployment Gatekeeper: Quick Start Guide

## Prerequisites
- Python 3.10+
- GitHub account with repository access
- SonarQube instance
- Slack workspace with bot permissions

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd devops-deployment-security-gate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Configuration

Edit the `.env` file with your actual credentials:

```env
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_token
SONARQUBE_URL=https://your-sonarqube-instance.com
SONARQUBE_TOKEN=your_sonarqube_token
SLACK_BOT_TOKEN=your_slack_bot_token
```

## First Run

Run a security check on a pull request:

```bash
python -m devops_deployment_security_gate run \
  --pr-number 123 \
  --repository myorg/myrepo \
  --branch feature-branch
```

## Testing

Run the test suite:

```bash
python tests/run_tests.py
```

## Next Steps

1. Customize agent configurations in `config/agents.yaml`
2. Modify task definitions in `config/tasks.yaml`
3. Set up CI/CD integration in your pipeline
4. Configure security policies in `config/settings.py`