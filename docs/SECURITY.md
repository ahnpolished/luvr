# Security Policy

This document defines the realistic security baseline for **Luvr v0.1.0 alpha**.

v0.1.0 is a private alpha for validating the Telegram dating-advice experience. It is **not** a production-grade consumer launch, compliance program, payment platform, or long-term memory system.

## v0.1.0 scope

In scope:

- Telegram bot alpha access.
- Text, photo, and voice-message handling.
- Lightweight web authentication for alpha users (HMAC-signed session tokens).
- Telegram-to-web account linking through short-lived linking tokens (10 min).
- Web-to-Telegram return through deep links.
- Instagram context collection through the web onboarding flow.
- Alpha invite code gating (`ALPHA_INVITE_CODE`).
- LLM-backed dating advice responses.
- Optional text-to-speech voice replies (OpenAI TTS).
- Tarot readings (Major Arcana deck).
- Basic safety behavior for sensitive relationship conversations.
- Basic structured logging for debugging and evaluation.
- Optional Weave tracing for consenting alpha users.

Out of scope for this security baseline:

- Kakaotalk launch.
- Production-grade account management.
- Cross-channel account linking beyond Telegram.
- Persistent product memory (research prototype only in `src/memory/`).
- X/Twitter integration.
- Private social-media scraping or bypassing platform privacy.
- Payments or paid tarot readings.
- Formal compliance claims such as HIPAA, SOC 2, GDPR certification, or PCI.

## Access control

For v0.1.0, Luvr should be treated as a **private alpha bot**.

Required:

- Use Telegram bot tokens only from environment variables or secret storage.
- Do not commit real tokens, API keys, photos, voice files, or raw exported trace files.
- Do not commit user IDs, logs, transcripts, or eval datasets unless they are synthetic or intentionally redacted.
- Prefer `TELEGRAM_ALLOWED_USER_IDS` for private testing.
- If allowlist is empty, assume the bot is public and not safe for real-user testing.
- Rotate any token that appears in terminal output, test logs, screenshots, commits, or shared documents.
- Use a pre-shared alpha invite code (`ALPHA_INVITE_CODE`) for web auth gating.
- Use a separate HMAC signing secret (`ALPHA_AUTH_SECRET`) for session and linking tokens.

Recommended:

- Use a separate Telegram bot token for development, staging, and any real-user alpha.
- Restrict production/staging tokens to the minimum number of maintainers.
- Rotate `ALPHA_AUTH_SECRET` and `ALPHA_INVITE_CODE` between alpha cohorts.

### Alpha Auth Token Design

- **Session tokens**: HMAC-SHA256 signed JSON payloads containing `user_id`, `telegram_user_id`, and `iat` (issued-at). Expire after 24 hours.
- **Linking tokens**: Same format, shorter 10-minute expiry. Embed `telegram_user_id` and `telegram_chat_id` for Telegram→web deep-linking.
- Both tokens are URL-safe base64-encoded with hex signature suffix.
- Token verification uses constant-time comparison (`hmac.compare_digest`).

## Data handling

Luvr v0.1.0 should minimize retained user data while still allowing realistic alpha evaluation.

Important distinction:

- **Evaluation traces** are short-lived records used for debugging, Weave review, prompt evaluation, and regression dataset creation.
- **Product memory** is user-facing long-term memory used by the bot to personalize future responses.

v0.1.0 may store limited evaluation traces. v0.1.0 may store a minimal alpha user profile for web auth, Telegram linking, usage limits, Weave labels, and Instagram context. v0.1.0 should not ship user-facing persistent product memory until the product-memory research is complete.

### Alpha Profile Data

The alpha registry (`src/alpha/registry.py`) stores per user:
- `user_id` (internal alpha ID)
- `telegram_user_id`, `telegram_chat_id`, `telegram_username`
- `display_name`, `nickname`, `email` (optional, user-provided)
- `auth_completed`, `onboarding_completed` (boolean flags)
- `allowlisted` (boolean)
- `usage_counters` (per-feature integer counts)
- `instagram_context_summary` (short string, user-provided)

This data is stored as JSON on disk (`tmp/alpha_registry.json` by default). It is not encrypted at rest — for alpha, treat the filesystem as the security boundary.

Required:

- Do not use conversation history as product memory by default.
- Do not persist photos or voice files by default.
- Process media in memory or temporary files only when necessary.
- Delete temporary media files after processing.
- Do not log API keys, full Telegram payloads, raw image contents, or raw audio contents.
- Logs may include operational metadata such as handler name, message type, user/chat identifier, status, latency, prompt version, model, and error category.

Allowed for alpha evaluation and debugging:

- Time-bounded conversation traces for consenting alpha users.
- Voice transcripts when needed to evaluate voice behavior.
- Prompt/model metadata needed to reproduce responses.
- Alpha profile fields listed above when intentionally collected.
- Instagram/self-summary context summaries attached to alpha profiles.
- Redacted or synthetic eval datasets derived from real scenarios.
- Aggregated error counts and latency metrics.

Retention guidance:

- Raw alpha traces should be short-lived, 7–30 days (configurable via `EVAL_TRACE_RETENTION_DAYS`).
- Curated and redacted eval cases may be retained longer.
- Raw media should not be retained unless a specific debugging need is approved.
- Alpha profiles remain until manually deleted by the operator.

Not allowed without a separate design review:

- Persistent product memory.
- Long-term raw conversation transcript storage.
- Raw social profile dumps beyond the short alpha context summary.
- Raw media retention.
- Admin dashboards that broadly expose raw user conversations.

## Third-party services

Depending on configuration, Luvr may send user content to third-party services:

- Telegram for messaging transport.
- OpenAI for LLM, Whisper transcription, and TTS.
- Anthropic, DeepSeek, or another configured LLM provider for response generation.
- Weights & Biases / Weave only if explicitly enabled for traces or evals.

Required:

- Document which providers are enabled before testing with real users.
- Send real-user traces to observability/eval tooling only for consenting alpha users or when the data is sufficiently redacted.
- Prefer trace labels and metadata over unnecessary raw content.
- Use provider API keys with least practical privilege.

## Safety behavior

Luvr gives informal dating and relationship advice. It is not a therapist, lawyer, doctor, crisis service, or emergency responder.

Required:

- The assistant should avoid claiming professional authority.
- Crisis, self-harm, abuse, coercion, or immediate-danger situations should trigger supportive language and encourage contacting trusted people, emergency services, or local crisis resources.
- The bot should avoid manipulative advice, harassment, stalking, non-consensual monitoring, or instructions to bypass another person's privacy.
- The bot should not encourage unsafe escalation in dating or relationship conflict.

## Media limits

Required:

- Enforce maximum attachment size (`MAX_ATTACHMENT_SIZE_MB`, default 25MB).
- Reject unsupported media types with a friendly message.
- Fail closed on media download, transcription, or analysis errors.
- Prefer sending a text fallback when voice reply (TTS) generation fails.

## Usage limits

Alpha features have per-user monthly quotas:

| Feature | Limit | Enforced by |
|---------|-------|------------|
| Voice messages | 10/month | `src/alpha/voice_usage.py` |
| Tarot readings | 3/month | `src/alpha/tarot_usage.py` |

Limits are bookkeeping only — no payment/entitlement logic. Counters are stored in the alpha profile JSON.

## Operational baseline

Before using the bot with real alpha users:

- `pytest` passes.
- `ruff check src/ tests/` passes.
- `ty check src/` (type checker) passes.
- Telegram smoke test passes with mock data.
- A manual Telegram test confirms text, photo, voice, tarot, and /link behavior.
- Real tokens are absent from git history, test output, screenshots, and docs.
- `.env` is ignored by git.
- Alpha auth secrets are set and tested.

## Infrastructure security

- **DNS**: Cloudflare (Terraform-managed in `infra/`)
- **Hosting**: Vercel (frontend), Railway or Fly.io (backend)
- **CI/CD**: GitHub Actions with secret management
- **Terraform state**: Remote backend with encryption

## Vulnerability reporting

For now, report security issues directly to the project maintainer.

Include:

- What happened.
- Steps to reproduce.
- Whether any secret, user message, photo, voice file, or transcript may have been exposed.
- Suggested severity if known.

Do not publicly disclose active secrets, private user data, or exploit details before the maintainer has rotated credentials and patched the issue.

## Security review triggers

Do a separate security review before expanding beyond the v0.1.0 alpha baseline into any of the following:

- Persistent product memory.
- Production-grade authentication/account management.
- Account linking beyond Telegram.
- Private social-media import or social graph ingestion.
- Payment or entitlement logic.
- Autonomous proactive outbound messages.
- Admin dashboards with broad user-level data access.
- Unbounded Weave/raw trace retention beyond the alpha evaluation policy.
