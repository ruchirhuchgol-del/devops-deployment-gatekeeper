# Deployment Guide

## Docker Compose (recommended for self-hosted)

```bash
# 1. Copy environment template
cp .env.example .env
# Edit .env with your real credentials

# 2. Start all services
docker-compose up -d

# 3. Verify health
curl http://localhost:8090/health
```

## CI/CD Integration

See `.github/workflows/security-scan.yml` for the GitHub Actions integration.

The security gate runs automatically on every pull request targeting `main` or `develop`.

## Environment Variables

All required variables are documented in `.env.example`.

## Monitoring

- Metrics: http://localhost:8090/metrics (Prometheus format)
- Dashboards: http://localhost:3000 (Grafana, default credentials admin/admin)
- Prometheus: http://localhost:9090
