# Luvr Setup Guide

> Step-by-step guide to getting Luvr running locally on your Mac.

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] **Mac** running macOS (Monterey or later)
- [ ] **iMessage** signed in with an Apple ID on your Mac
- [ ] **Python 3.12+** installed (`python3 --version`)
- [ ] **Git** installed (`git --version`)
- [ ] An **OpenAI API key** (https://platform.openai.com/api-keys) **or** **Anthropic API key** (https://console.anthropic.com)

## Step 1: Clone & Install Luvr

```bash
git clone https://github.com/ahnpolished/luvr.git
cd luvr
make install
```

This creates a virtual environment and installs all dependencies.

## Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Required: BlueBubbles connection
BLUEBUBBLES_SERVER_URL=http://localhost:1234
BLUEBUBBLES_PASSWORD=your_bluebubbles_password

# Required: Choose your LLM provider
LLM_PROVIDER=openai            # or "anthropic"
OPENAI_API_KEY=sk-...          # if using OpenAI
ANTHROPIC_API_KEY=sk-ant-...   # if using Anthropic
```

## Step 3: Install BlueBubbles

BlueBubbles is the bridge between iMessage and the Luvr bot.

### 3.1 Download & Install

1. Go to https://bluebubbles.app
2. Download the latest macOS server
3. Install and launch BlueBubbles
4. Grant the required permissions (Full Disk Access, Accessibility)

### 3.2 Configure BlueBubbles

1. Open BlueBubbles settings
2. Go to **Server** tab:
   - Set a **password** (use the same one as in your `.env`)
   - Note the **server URL** (default: `http://localhost:1234`)
3. Go to **Webhook** tab:
   - Set webhook URL to: `http://127.0.0.1:8000/webhook`
     (Use `127.0.0.1` NOT `localhost` — BlueBubbles resolves `localhost` to IPv6 `::1`,
     which won't connect to the server.)
   - Enable "New Message" event
4. Go to **Connection** tab:
   - Ensure iMessage is connected (green indicator)

### 3.3 Verify BlueBubbles

```bash
# Check that BlueBubbles is running
curl http://localhost:1234/api/v1/server/info?password=your_password
```

## Step 4: Configure iMessage

1. Open **Messages** app on your Mac
2. Sign in with your Apple ID (if not already)
3. Enable **Messages in iCloud** (optional, for sync)
4. Verify you can send/receive iMessages normally

**Important**: BlueBubbles uses the same iMessage account. Any messages sent/received on your Mac will be visible to the bot.

## Step 5: Start Luvr

```bash
make run
```

You should see:
```
INFO     luvr_starting           version=0.1.0 llm_provider=openai
INFO     luvr_ready              port=8000
INFO     Started server process
INFO     Uvicorn running on http://0.0.0.0:8000
```

## Step 6: Test the Connection

### Option A: Smoke tests (no real iMessage)

```bash
# In another terminal
make smoke-test
```

Expected output:
```
💨 Luvr Smoke Tests
==================================================
  Provider: openai
  Model: gpt-4o-mini

📱 Testing TEXT messages...
----------------------------------------
  ✅ [text] (1.2s)
     Q: I've been talking to someone for 3 weeks...
     A: That's tough! First, take a breath...

✅ All smoke tests passed!
```

### Option B: Real iMessage test

1. From your iPhone (or another device), send an iMessage to your Mac's iMessage address
2. Example: "Hey Luvr, should I text him back tonight?"
3. You should receive a response within a few seconds

## Step 7: Try Different Message Types

### Text Messages
Just text normally! Ask relationship questions, describe situations, etc.

### Photo Messages
Send a screenshot of:
- A confusing text conversation
- A dating app profile
- Something relevant to your dating life

### Voice Memos
Record a voice memo in iMessage and send it. The bot will transcribe and respond.

## Troubleshooting

### Messages not coming through

1. Check BlueBubbles is running and connected to iMessage
2. Verify webhook is configured to `http://127.0.0.1:8000/webhook` (NOT localhost!)
3. Check Luvr logs for errors

### LLM errors

1. Verify your API key in `.env`
2. Check you have credits on your OpenAI/Anthropic account
3. Try switching providers (`LLM_PROVIDER=anthropic`)

### BlueBubbles connection issues

1. Restart BlueBubbles
2. Check firewall settings (allow port 1234)
3. Verify iMessage is signed in on your Mac
4. Check BlueBubbles logs for details

### Voice memos not working

1. Ensure `OPENAI_API_KEY` is set (Whisper uses OpenAI)
2. Check the audio file size (max 25MB by default)
3. Use shorter voice memos for testing

## Next Steps

- [ ] Set up multiple users (v0.2.0)
- [ ] Deploy to cloud server
- [ ] Add conversation history
- [ ] Customize bot personality
- [ ] Build iOS companion app

## Need Help?

- **Issues**: https://github.com/ahnpolished/luvr/issues
- **BlueBubbles docs**: https://docs.bluebubbles.app
- **Linear project**: https://linear.app/humphreyahn/project/luvr-3b2084037dfc
