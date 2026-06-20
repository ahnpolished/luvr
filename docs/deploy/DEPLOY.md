# Luvr Continuous Deploy Infrastructure

> Provisioned with Terraform, executed from GitHub Actions — no Terraform Cloud.

## Stack

| Layer | Platform | Terraform Module |
|-------|----------|-----------------|
| **Server (API)** | Railway → `luvr-server` (FastAPI) | `infra/modules/railway-service` |
| **Server (Worker)** | Railway → `luvr-telegram` (polling bot) | `infra/modules/railway-service` |
| **Frontend** | Vercel (`web/`) | `infra/modules/vercel-project` |
| **DNS / Proxy / WAF** | Cloudflare (`ahnpolished.com` zone) | `infra/modules/cloudflare-dns` |
| **Terraform State** | Cloudflare R2 (S3-compatible backend) | Manual one-time setup |

## Architecture

```
                           ┌──────────────────┐
                           │   Cloudflare DNS  │
                           │ ahnpolished.com   │
                           └───┬──────────┬────┘
                               │          │
                    ┌──────────▼──┐  ┌────▼────────────┐
                    │ Vercel      │  │ Railway          │
                    │ (frontend)  │  │  ├─ api          │
                    │             │  │  └─ telegram-wkr │
                    └─────────────┘  └──────────────────┘
```

## Environments

| Environment | Frontend | API | Telegram Worker |
|------------|----------|-----|-----------------|
| **Staging** | `staging.luvr.ahnpolished.com` | `api-staging.luvr.ahnpolished.com` | No custom domain |
| **Production** | `luvr.ahnpolished.com` | `api.luvr.ahnpolished.com` | No custom domain |

Both environments track `main`. Staging auto-deploys on push; production requires manual approval via a GitHub Environment.

## Directory Layout

```
infra/
  modules/
    cloudflare-dns/        # Zone data source + DNS records + zone settings + WAF
    vercel-project/        # vercel_project + domain + env vars
    railway-service/       # railway_project + 2x railway_service + domain + env vars
  envs/
    staging/               # Backend "s3" (R2), provider blocks, module calls
    production/            # Same structure, production values
.github/workflows/
  terraform-plan.yml       # PR touching infra/**: fmt check, validate, plan, comment
  terraform-apply.yml      # push to main: auto-apply staging, gated production
railway.json               # Multi-service start commands (if Terraform provider doesn't support them)
```

## Prerequisites (Manual, One-Time)

Before the first `terraform apply`, these must be created manually:

1. **Cloudflare R2 bucket** for Terraform state:
   ```bash
   # Via Cloudflare dashboard or wrangler CLI:
   wrangler r2 bucket create luvr-terraform-state
   ```

2. **R2 S3-compatible API token** with Object Read & Write on the bucket.
   Store in GitHub Actions secrets: `R2_ACCESS_KEY`, `R2_SECRET_KEY`, `R2_ENDPOINT`, `TF_STATE_BUCKET`.

3. **API tokens** for each platform, stored as GitHub Actions secrets:
   - `CLOUDFLARE_API_TOKEN` — Zone:DNS:Edit + Zone:Settings:Edit + Zone:WAF:Edit
   - `VERCEL_API_TOKEN` — Full Account scope
   - `RAILWAY_API_TOKEN` — Project scope

4. **GitHub Environment** named `production` with a required reviewer for manual approval.

## CI/CD Pipeline

### On PR (touching `infra/**`)
1. `terraform fmt -check -recursive infra/`
2. `terraform init` (R2 backend)
3. `terraform validate` (both environments)
4. `terraform plan` (both environments)
5. Plan output posted as PR comment

### On Merge to `main`
1. **Staging**: `terraform apply -auto-approve`
2. **Production**: gated behind `environment: production` → manual approval → `terraform apply -auto-approve`

## Secret Variables

All secrets are sourced from GitHub Actions → `TF_VAR_*` environment variables. No secret values appear in the repo.

| Secret | Used In |
|--------|---------|
| `CLOUDFLARE_API_TOKEN` | `TF_VAR_cloudflare_api_token` |
| `VERCEL_API_TOKEN` | `TF_VAR_vercel_api_token` |
| `RAILWAY_API_TOKEN` | `TF_VAR_railway_api_token` |
| `STAGING_SHARED_ENV_VARS` | Shared Railway vars (JSON) |
| `STAGING_API_ENV_VARS` | API service Railway vars (JSON) |
| `STAGING_TELEGRAM_ENV_VARS` | Telegram worker Railway vars (JSON) |
| `PROD_SHARED_ENV_VARS` | Production shared Railway vars (JSON) |
| `PROD_API_ENV_VARS` | Production API Railway vars (JSON) |
| `PROD_TELEGRAM_ENV_VARS` | Production Telegram Railway vars (JSON) |

## Railway Services

### `api` (luvr-server)
- **Start**: `uvicorn src.server:app --host 0.0.0.0 --port ${PORT:-8000}`
- **Health check**: `GET /health` → `{"status": "ok"}`
- **Custom domain**: `api.luvr.ahnpolished.com` (prod) / `api-staging.luvr.ahnpolished.com` (staging)

### `telegram-worker` (luvr-telegram)
- **Start**: `python -m src.telegram_server`
- **Health check**: *disabled* (no HTTP port — this is a known gap)
- **No custom domain**: The worker polls Telegram; it doesn't serve HTTP

## DNS Sequencing

Cloudflare DNS records are provisioned with `proxied = false` (DNS-only, gray cloud) so Railway and Vercel can verify the custom domains and issue their own TLS certificates.

After initial apply and certificate provisioning:
1. Flip `proxied = true` (orange cloud) in the environment's module call
2. Set `ssl_mode = "strict"` in the Cloudflare zone settings
3. Re-apply Terraform

## Post-Apply Verification (Manual)

- [ ] `https://staging.luvr.ahnpolished.com` loads the web frontend
- [ ] `https://api-staging.luvr.ahnpolished.com/health` returns 200
- [ ] `telegram-worker` shows "running" in Railway (not flapping on a failed healthcheck)
- [ ] After production approval: same checks against prod domains

## Out of Scope

- Sentry / Prometheus monitoring (future, noted in `ARCHITECTURE.md`)
- Rollback strategy (native redeploy-previous-build on both platforms)
- Secret rotation
- `telegram-worker` health checks (no HTTP port — known gap)
- BlueBubbles/iMessage reachability from cloud environments
