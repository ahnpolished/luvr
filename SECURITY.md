# Security Policy

This document defines the realistic security baseline for **Luvr v0.1.0 alpha**.

v0.1.0 is a private alpha for validating the Telegram dating-advice experience. It is **not** a production-grade consumer launch, compliance program, payment platform, or long-term memory system.

## v0.1.0 scope

In scope:

- Telegram bot alpha access.
- Text, photo, and voice-message handling.
- Lightweight web authentication for alpha users.
- Telegram-to-web account linking through short-lived links/tokens.
- Web-to-Telegram return through deep links or redirects.
- Instagram context collection through the web onboarding flow.
- LLM-backed dating advice responses.
- Optional text-to-speech voice replies.
- Basic safety behavior for sensitive relationship conversations.
- Basic structured logging for debugging and evaluation.

Out of scope for this security baseline:

- Kakaotalk launch.
- Production-grade account management.
- Cross-channel account linking beyond Telegram.
- Persistent product memory.
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

Recommended:

- Use a separate Telegram bot token for development, staging, and any real-user alpha.
- Restrict production/staging tokens to the minimum number of maintainers.

## Data handling

Luvr v0.1.0 should minimize retained user data while still allowing realistic alpha evaluation.

Important distinction:

- **Evaluation traces** are short-lived records used for debugging, Weave review, prompt evaluation, and regression dataset creation.
- **Product memory** is user-facing long-term memory used by the bot to personalize future responses.

v0.1.0 may store limited evaluation traces. v0.1.0 may store a minimal alpha user profile for web auth, Telegram linking, usage limits, Weave labels, and Instagram context. v0.1.0 should not ship user-facing persistent product memory until the product-memory research is complete.

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
- Alpha profile fields such as `user_id`, `telegram_user_id`, username, nickname, or email when intentionally collected for auth/linking or Weave analysis.
- A short Instagram/self-summary context summary attached to the alpha profile.
- Redacted or synthetic eval datasets derived from real scenarios.
- Aggregated error counts and latency metrics.

Retention guidance:

- Raw alpha traces should be short-lived, for example 7–30 days.
- Curated and redacted eval cases may be retained longer.
- Raw media should not be retained unless a specific debugging need is approved.

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
- The bot should avoid manipulative advice, harassment, stalking, non-consensual monitoring, or instructions to bypass another person’s privacy.
- The bot should not encourage unsafe escalation in dating or relationship conflict.

## Media limits

Required:

- Enforce maximum attachment size.
- Reject unsupported media types with a friendly message.
- Fail closed on media download, transcription, or analysis errors.
- Prefer sending a text fallback when voice reply generation fails.

## Operational baseline

Before using the bot with real alpha users:

- `pytest` passes.
- `ruff check src/ tests/` passes.
- `mypy src` passes.
- Telegram smoke test passes with mock data.
- A manual Telegram test confirms text, photo, and voice behavior.
- Real tokens are absent from git history, test output, screenshots, and docs.
- `.env` is ignored by git.

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
