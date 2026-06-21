# Luvr Continuous Deploy Infrastructure

> DNS and frontend provisioned with Terraform; Railway managed via `railway.json`.

## Stack

| Layer | Platform | How Managed |
|-------|----------|------------|
| **DNS / Proxy / WAF** | Cloudflare (`ahnpolished.com` zone) | Terraform — `infra/modules/cloudflare-dns` |
| **Frontend** | Vercel (`web/`) | Terraform — `infra/modules/vercel-project` |
| **Server (API)** | Railway → `luvr-server` (FastAPI) | `railway.json` + Railway GitHub App |
| **Server (Worker)** | Railway → `luvr-telegram` (polling bot) | `railway.json` + Railway GitHub App |
| **Terraform State** | Cloudflare R2 (S3-compatible backend) | Manual one-time setup |

> **Why Terraform doesn't manage Railway:** The community Railway Terraform provider (`railwayapp/railway`) does not exist on the public Terraform Registry. Railway infrastructure is managed via the checked-in `railway.json` file and Railway's native GitHub integration, which auto-deploys on push to `main`.

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

Both environments track `main`. Staging auto-deploys on push; production requires manual approval via a GitHub Environment.

## Directory Layout

```
infra/
  modules/
    cloudflare-dns/        # Zone data source + DNS records + zone settings + WAF
    vercel-project/        # vercel_project + domain + env vars
  envs/
    staging/               # Backend "s3" (R2), provider blocks, module calls
    production/            # Same structure, production values
.github/workflows/
  terraform-plan.yml       # PR touching infra/**: fmt check, validate, plan, comment
  terraform-apply.yml      # push to main: auto-apply staging, gated production
railway.json               # Multi-service config for Railway (api + telegram-worker)
```

## Prerequisites (Manual, One-Time)

### Terraform

1. **Cloudflare R2 bucket** for Terraform state:
   ```bash
   wrangler r2 bucket create luvr-tf
   ```
   Or create via Cloudflare Dashboard → R2 → Create bucket.
   See official guide: https://developers.cloudflare.com/terraform/advanced-topics/remote-backend/

2. **R2 S3-compatible API token** with Object Read & Write.
   Store in GitHub Actions secrets:
   - `TF_STATE_BUCKET` — bucket name
   - `R2_ENDPOINT` — `https://<account>.r2.cloudflarestorage.com`
   - `R2_ACCESS_KEY` — R2 access key ID
   - `R2_SECRET_KEY` — R2 secret access key

3. **Cloudflare API token** (Zone:DNS:Edit + Zone:Settings:Edit + Zone:WAF:Edit).
   Store as `CLOUDFLARE_API_TOKEN`.

4. **Vercel API token** (Full Account scope).
   Store as `VERCEL_API_TOKEN`.

5. **GitHub Environment** named `production` with a required reviewer.

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
2. `terraform init -backend=false` (if R2 secrets not set) or full init
3. `terraform validate`
4. `terraform plan` (if secrets available)
5. Plan output posted as PR comment

### On Merge to `main`
1. **Staging**: `terraform apply -auto-approve`
2. **Production**: gated behind `environment: production` → manual approval → `terraform apply -auto-approve`

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
