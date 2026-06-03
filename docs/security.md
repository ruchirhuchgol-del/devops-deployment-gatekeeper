# Security Considerations

## Secret Management

- Never commit `.env` to version control (it is gitignored)
- Rotate all API tokens quarterly
- Use GitHub Secrets for CI/CD credential injection
- Container runtime credentials are injected via environment variables, never baked into images

## Webhook Validation

All GitHub webhook payloads are validated using HMAC-SHA256 with `GITHUB_WEBHOOK_SECRET` before processing.

## Principle of Least Privilege

- GitHub token requires only: `repo:status`, `pull_requests:write`
- SonarQube token requires: Execute Analysis, Browse
- Slack bot requires: `chat:write`

## Compliance

For SOC2 and audit trail requirements, every security gate decision is logged with timestamp, PR number, repository, decision (ALLOW/BLOCK), and policy violations. See `docs/architecture.md` for the audit flow.
