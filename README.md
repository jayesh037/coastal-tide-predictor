# Coastal Tide Predictor

Real-time tidal forecasting with Temporal Fusion Transformer.

## Setup

```bash
# Copy template files
cp docker-compose.yml.example docker-compose.yml
cp .env.example .env

# Edit with your credentials
nano .env

# Start
docker compose up -d
```

## Files

- `docker-compose.yml.example` — Template (commit)
- `.env.example` — Template (commit)
- `.env` — Local secrets (git-ignored)
- `docker-compose.local.yml` — Local overrides (git-ignored)
- `logs.txt` — Runtime logs (git-ignored)
