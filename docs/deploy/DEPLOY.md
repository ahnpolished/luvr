# Luvr Continuous Deploy Infrastructure

## Stack
- **Server:** Railway (FastAPI + Telegram bot worker)
- **Frontend:** Vercel (web onboarding flow, if separate)
- **DNS/CDN:** Cloudflare

## Railway

The FastAPI server and Telegram bot run as a single Railway service.

### Setup
1. Create Railway project linked to this repo.
2. Set root directory to `.`.
3. Use the `railway.json` or auto-detect Python.
4. Required environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `ALPHA_AUTH_SECRET`
   - `ALPHA_INVITE_CODE`
   - `ALPHA_WEB_BASE_URL`
   - `OPENAI_API_KEY` (or provider of choice)
   - `PORT` (Railway sets this automatically)

### Health check
Railway health check hits `GET /health` — returns `{"status": "ok"}`.

## Vercel

The web onboarding flow can be deployed as a Vercel serverless function or as part of the FastAPI server on Railway. For v0.1.0, the web auth endpoints run on Railway alongside the bot.

If a separate Vercel frontend is needed later:
1. Point Vercel to a `web/` directory with its own `package.json`.
2. Backend URL configured via `VITE_API_BASE_URL` env var.

## Cloudflare

For v0.1.0, Cloudflare handles:
- DNS for the web onboarding domain
- SSL/TLS termination
- Optional: caching static assets

No Cloudflare Workers or R2 storage is used in v0.1.0.
