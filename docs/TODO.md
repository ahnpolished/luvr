# Luvr TODOs

## ✅ Done (v0.1.0)

- [x] Telegram bot with text, photo, voice message handling
- [x] LLM integration: OpenAI, Anthropic, DeepSeek, OpenCode
- [x] Tarot readings — 3-card relationship spread with Major Arcana images
- [x] Web onboarding flow: alpha auth, Telegram linking, Instagram context
- [x] Alpha user registry with profile storage and Telegram linking
- [x] Usage limits: voice messages (10/mo), tarot readings (3/mo)
- [x] TTS voice replies via OpenAI TTS
- [x] Language detection: Korean vs. English
- [x] Weave conversation eval + span instrumentation
- [x] DeepEval safety, tone, and friend-likeness eval cases
- [x] Korean eval cases for multilingual testing
- [x] mem0 memory store prototype (research only)
- [x] Manual proactive check-in copy builder
- [x] iMessage bridge via BlueBubbles (secondary platform)
- [x] Terraform-managed infra: Cloudflare DNS + Vercel

## 🔜 Next (v0.2.0)

### Context consumption gap
- **[ ] Wire `instagram_context_summary` into LLM prompts** — context is stored on alpha profiles but not yet read by prompt-building code in `src/llm/` or handlers. This is the highest-impact immediate follow-up.

### Persistent product memory
- [ ] Research and prototype memory architecture (see `docs/AUTH_MEMORY.md`)
- [ ] Build memory read/write into conversation flow
- [ ] User-facing memory visibility and deletion UX

### Multi-user polish
- [ ] Conversation history persistence
- [ ] Better multi-turn context handling
- [ ] Personality/style customization per user

## 📋 Later (v0.3.0+)

- [ ] Multi-channel: revive iMessage, add Kakaotalk
- [ ] Production deployment (Railway/Fly.io, monitoring, alerts)
- [ ] Admin dashboard for alpha management
- [ ] Improved Instagram extraction (public API where available)
- [ ] Fortune telling feature
- [ ] Calendar integration for date-aware advice
- [ ] App Store companion app

## 💭 Ideas

- Conversational onboarding: interactive questionnaire instead of forms
- "Draft the text" feature: help users compose tricky messages
- Date journal: lightweight tracking of dating experiences
- Voice tone analysis: detect emotional state from voice memos
