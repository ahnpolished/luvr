# Luvr Continuous Deploy Infrastructure

> DNS and frontend provisioned with Terraform; Railway managed via `railway.json`.

## Stack

| Layer | Platform | How Managed |
|-------|----------|------------|
| **DNS / Proxy / WAF** | Cloudflare (`ahnpolished.com` zone) | Terraform — `infra/modules/cloudflare-dns` |
| **Frontend** | Vercel (`web/`) | Terraform — `infra/modules/vercel-project` |
| **Server (API)** | Railway → `luvr` service (FastAPI) | `.github/workflows/railway-deploy.yml` (Railway CLI) |
| **Server (Worker)** | Railway → not yet provisioned (polling bot) | Known gap — `telegram-worker` service does not exist yet |
| **Terraform State** | Google Cloud Storage (GCS backend) | Manual one-time setup |

> **Why Terraform doesn't manage Railway:** The community Railway Terraform provider (`railwayapp/railway`) does not exist on the public Terraform Registry. Railway infrastructure is configured via the checked-in `railway.json` file, but deploys are triggered explicitly by `.github/workflows/railway-deploy.yml` using the Railway CLI — not Railway's GitHub App auto-deploy, so production can be gated behind manual approval the same way Terraform/Vercel are.
>
> **Note:** the project currently has a single Railway service named `luvr` (not `api`/`telegram-worker` as `railway.json`'s per-service keys assume — those keys are ignored unless service names match exactly). The `luvr` service's start command and health check are set directly via Railway service config to run the API (`uvicorn src.server:app`). The Telegram worker described below is not deployed.

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
                    │  Terraform  │  │  └─ telegram-wkr │
                    └─────────────┘  │  railway.json    │
                                     └──────────────────┘
```

## Environments

| Environment | Frontend | API | Telegram Worker |
|------------|----------|-----|-----------------|
| **Staging** | `staging.luvr.ahnpolished.com` | `api-staging.luvr.ahnpolished.com` | No custom domain |
| **Production** | `luvr.ahnpolished.com` | `api.luvr.ahnpolished.com` | No custom domain |

Both environments track `main`. Staging's Railway deploy fires automatically on push to `main`; production's Railway deploy only runs via manual `workflow_dispatch`, gated behind the `production` GitHub Environment's required reviewer — same pattern as the Terraform/Vercel jobs.

## Directory Layout

```
infra/
  modules/
    cloudflare-dns/        # Zone data source + DNS records + zone settings + WAF
    vercel-project/        # vercel_project + domain + env vars
  envs/
    staging/               # Backend "gcs", provider blocks, module calls
    production/            # Same structure, production values
.github/workflows/
  terraform-plan.yml       # PR touching infra/**: fmt check, validate, plan, comment
  terraform-apply.yml      # push to main: auto-apply staging, gated production
railway.json               # Multi-service config for Railway (api + telegram-worker)
```

## Prerequisites (Manual, One-Time)

### Terraform

1. **GCS bucket** for Terraform state:
   ```bash
   gcloud storage buckets create gs://luvr-tf-state --location=us-central1
   ```

2. **GCP Service Account** with `Storage Object Admin` on the bucket.
   Download the JSON key and store as GitHub Actions secret `GCP_SA_KEY`.

3. **Cloudflare API token** (Zone:DNS:Edit + Zone:Settings:Edit + Zone:WAF:Edit).
   Store as `CLOUDFLARE_API_TOKEN`.

4. **Vercel API token** (Full Account scope).
   Store as `VERCEL_API_TOKEN`.

5. **GitHub Environment** named `production` with a required reviewer.

6. **Railway API tokens** (one per environment, created in the Railway dashboard under Project Settings → Tokens, scoped to the `staging` and `production` environments respectively):
   - Store as GitHub Actions secrets `RAILWAY_TOKEN_STAGING` and `RAILWAY_TOKEN_PRODUCTION`.

7. **Disable Railway's GitHub App auto-deploy on the `production` environment** (Railway dashboard → environment settings). Otherwise Railway will deploy production on every push to `main` regardless of the GitHub Actions approval gate. Staging can keep GitHub App auto-deploy enabled, or rely solely on the `railway-deploy.yml` workflow — either is fine since both fire on push to `main` without approval.

### Railway

Railway is set up manually or via their CLI:

1. Create Railway project(s) linked to the GitHub repo:
   ```bash
   railway link                    # link to project
   railway up                      # initial deploy
   ```

2. Configure environment variables in Railway dashboard (or via `railway variables set`):
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
   - `ALPHA_AUTH_SECRET`
   - etc. (see `.env.example`)

3. Add custom domains to the `api` service:
   - Staging: `api-staging.luvr.ahnpolished.com`
   - Production: `api.luvr.ahnpolished.com`

4. Note the Railway-generated CNAME target, then update `railway_cname_target` in Terraform and re-apply.

## Railway Services (via railway.json)

### `api` (luvr-server)
- **Start**: `uvicorn src.server:app --host 0.0.0.0 --port ${PORT:-8000}`
- **Health check**: `GET /health` → `{"status": "ok"}`
- **Custom domain**: `api.luvr.ahnpolished.com` (prod) / `api-staging.luvr.ahnpolished.com` (staging)

### `telegram-worker` (luvr-telegram)
- **Start**: `python -m src.telegram_server`
- **Health check**: *disabled* (no HTTP port — known gap)
- **No custom domain**: The worker polls Telegram; it doesn't serve HTTP

## CI/CD Pipeline

### On PR (touching `infra/**`)
1. `terraform fmt -check -recursive infra/`
2. `terraform init`
3. `terraform validate`
4. `terraform plan`
5. Plan output posted as PR comment

### On Merge to `main`
1. **Staging**: `terraform apply -auto-approve` (Terraform); `railway-deploy.yml` deploys the `luvr` service to the `staging` environment automatically
2. **Production**: Terraform/Vercel gated behind `environment: production` → manual approval → `terraform apply -auto-approve`. Railway deploy follows the same gate — `railway-deploy.yml`'s `deploy-production` job only runs via manual `workflow_dispatch`, also gated by the `production` GitHub Environment

## DNS Sequencing

Cloudflare DNS records are provisioned with `proxied = false` (DNS-only) so Railway and Vercel can verify the custom domains and issue their own TLS certificates.

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
