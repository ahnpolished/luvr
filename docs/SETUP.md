# Luvr Setup Guide

> Step-by-step guide to getting Luvr running locally via Telegram — no Mac required.

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] **Python 3.12+** installed (`python3 --version`)
- [ ] **Git** installed (`git --version`)
- [ ] A **Telegram account** on your phone
- [ ] An **LLM API key** — at least one of:
  - **OpenAI API key** ([platform.openai.com](https://platform.openai.com/api-keys))
  - **Anthropic API key** ([console.anthropic.com](https://console.anthropic.com))
  - **DeepSeek API key** ([platform.deepseek.com](https://platform.deepseek.com))
  - **OpenCode server** (local, no external API key needed)

## Step 1: Clone & Install Luvr

```bash
git clone https://github.com/ahnpolished/luvr.git
cd luvr
make install
```

This creates a virtual environment and installs all dependencies.

## Step 2: Create a Telegram Bot

1. Open Telegram and chat with [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the bot token (looks like `123456:ABCdef...`)

## Step 3: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

### Required settings

```env
PLATFORM=telegram
TELEGRAM_BOT_TOKEN=your_token_from_botfather
```

### Choose your LLM provider

```env
# Option A: OpenAI (default)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini

# Option B: Anthropic Claude
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-haiku-20240307

# Option C: DeepSeek
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-...
LLM_MODEL=deepseek-chat

# Option D: OpenCode (local gateway)
LLM_PROVIDER=opencode
OPENCODE_BASE_URL=http://localhost:54321
OPENCODE_PROVIDER_ID=deepseek
LLM_MODEL=deepseek-chat
```

### Optional: Restrict users

To only allow specific Telegram users during alpha testing:

```env
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321
```

If this is empty, the bot is open to anyone who finds it.

### Optional: Voice reply (TTS)

When a user sends a voice memo, Luvr can reply with its own voice message:

```env
TTS_ENABLED=true          # default: true
TTS_MODEL=tts-1           # tts-1 (faster) or tts-1-hd (higher quality)
TTS_VOICE=nova            # alloy, echo, fable, onyx, nova, shimmer
```

### Optional: Alpha auth & web onboarding

For the web onboarding flow (alpha invite code + Instagram context):

```env
ALPHA_INVITE_CODE=your-secret-invite-code
ALPHA_AUTH_SECRET=your-hmac-signing-secret
ALPHA_WEB_BASE_URL=http://localhost:8000
```

## Step 4: Run the Bot

```bash
# Polling mode (default, simplest for local dev)
make run-telegram

# Or webhook mode for production
luvr-telegram --mode webhook --webhook-url https://your-domain.com/webhook
```

You should see:
```
INFO     luvr_telegram_starting    mode=polling
INFO     llm_client_created        provider=openai model=gpt-4o-mini
INFO     luvr_telegram_ready       mode=polling
```

## Step 5: Chat!

1. Open Telegram on your phone
2. Find your bot by its username
3. Send `/start` to see the welcome message
4. Try sending a dating question!

---

## 🌐 Web Onboarding Setup (Alpha)

The web onboarding flow lets alpha users authenticate and optionally provide Instagram context.

### Prerequisites

- **Node.js 18+** for the frontend
- Alpha auth env vars configured (see Step 3)

### 1. Start the FastAPI backend

```bash
make run
```

### 2. Start the web frontend (separate terminal)

```bash
cd web
npm install
npm run dev
```

### 3. Test the flow

1. In Telegram, send `/link` to your bot
2. Open the deep-link URL in your browser
3. Enter the alpha invite code
4. Provide Instagram handle + bio (or skip)
5. You'll be redirected back to Telegram

---

## 💬 iMessage Setup (Mac only, secondary)

The iMessage bridge via BlueBubbles is also available for Mac users.

### Step 3: Install BlueBubbles

1. Go to https://bluebubbles.app
2. Download the latest macOS server
3. Install, launch, and grant permissions (Full Disk Access, Accessibility)

### Step 4: Configure BlueBubbles

1. Open BlueBubbles settings → **Server** tab:
   - Set a **password**
   - Note the server URL (default: `http://localhost:1234`)
2. Go to **Webhook** tab:
   - Set webhook URL to: `http://127.0.0.1:8000/webhook`
   - Use `127.0.0.1` NOT `localhost` — BlueBubbles resolves `localhost` to IPv6 `::1`
   - Enable "New Message" event
3. **Connection** tab: ensure iMessage shows green indicator

### Step 5: Configure iMessage env

```env
PLATFORM=imessage
BLUEBUBBLES_SERVER_URL=http://localhost:1234
BLUEBUBBLES_PASSWORD=your_bluebubbles_password
```

### Step 6: Run iMessage server

```bash
make run
```

### Step 7: Test

```bash
# Smoke tests (no real iMessage needed)
make smoke-test

# Or send a real iMessage to your Mac's iMessage address
```

---

## 🧪 Running Tests

```bash
make test             # All unit tests
make test-cov         # With coverage report
make tg-smoke-test    # Telegram smoke tests (no API keys needed)
make smoke-test       # iMessage smoke tests (needs API keys)
```

## 🧪 Running Evaluation Tests

```bash
make eval         # Fast deterministic metric tests (no API keys needed)
make eval-slow    # Full suite including LLM-dependent tests
make eval-all     # Run everything
```

## 🃏 Generating Tarot Card Images

```bash
make generate-tarot-images
```

This generates 22 Major Arcana card images as PNG assets.

---

## Troubleshooting

### Bot not responding

1. Check the bot is running (no errors in terminal)
2. Verify `TELEGRAM_BOT_TOKEN` is correct in `.env`
3. If using allowlist, verify your Telegram user ID is in `TELEGRAM_ALLOWED_USER_IDS`
4. Try restarting the bot

### LLM errors

1. Verify your API key in `.env`
2. Check you have credits on your provider account
3. Try switching providers: `LLM_PROVIDER=anthropic`

### Voice memos not working

1. Ensure `OPENAI_API_KEY` is set (Whisper uses OpenAI regardless of LLM provider)
2. Check audio file size (max 25MB by default)
3. Try shorter voice memos for testing

### TTS voice replies not working

1. Check `TTS_ENABLED=true` in `.env`
2. Ensure `OPENAI_API_KEY` is set (TTS uses OpenAI)
3. Check for quota/rate-limit errors in logs

### Web onboarding not working

1. Ensure both backend (`make run`) and frontend (`cd web && npm run dev`) are running
2. Verify `ALPHA_INVITE_CODE` and `ALPHA_AUTH_SECRET` are set in `.env`
3. Check the `ALPHA_WEB_BASE_URL` matches where your backend is running

## Next Steps

- [ ] Set up web onboarding for alpha users
- [ ] Try tarot readings (`/tarot` in Telegram)
- [ ] Review eval results and prompt quality
- [ ] Deploy to Railway/Fly.io for 24/7 uptime

## Need Help?

- **Issues**: https://github.com/ahnpolished/luvr/issues
- **Telegram Bot docs**: https://core.telegram.org/bots
- **BlueBubbles docs**: https://docs.bluebubbles.app
- **Linear project**: https://linear.app/humphreyahn/project/luvr-3b2084037dfc
