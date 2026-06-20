# v0.1.0 Release Readiness Gate

**Date:** 2026-06-20
**Status:** All automated checks PASS. Manual tests pending.

## Automated Checks

- [x] `pytest -W error` — 211 passed, 0 failed
- [x] `ruff check src/ tests/` — All checks passed
- [x] `mypy src` — Success: no issues found in 51 source files
- [x] `.env` ignored — `git check-ignore -q .env` passes
- [x] No token-shaped values in diff

## Manual Smoke Tests (need real Telegram bot)

- [ ] Text message → LLM response
- [ ] Photo message → vision analysis + response
- [ ] Voice memo → transcription + response
- [ ] `/tarot` → tarot reading flow
- [ ] `/link` → web auth deep link generated
- [ ] Web auth flow → profile created
- [ ] Instagram onboarding → context saved
- [ ] Web → Telegram return (deep link back)
- [ ] Manual proactive message script (dry-run and real)

## v0.1.0 In-Scope Features Status

| Feature | Status |
|---------|--------|
| Alpha user registry | Done |
| Usage limits (voice + tarot) | Done |
| Lightweight web auth | Done |
| Telegram-web deep linking | Done |
| Web onboarding (Instagram) | Done |
| Bilingual EN/KO | Done |
| Tarot deck + prompt | Done |
| Baseline test/lint hygiene | Done |
| Context gathering research | Done |
| Eval trace capture schema | Done (other session) |
| Weave conversation spans | Done (other session) |
| Alpha labels in Weave | Done (other session) |
| Voice memo conversation | Done (other session) |
| Conversation eval workflow | In Progress (PR #23) |
| Manual proactive script | In Progress (other session) |

## Known Out-of-Scope (Not Implemented — by Design)

- [x] Kakaotalk linking — out of scope
- [x] X/Twitter — out of scope
- [x] Stripe/payment — out of scope
- [x] Persistent product memory — out of scope
- [x] Autonomous scheduler — out of scope
- [x] Long-form transcript storage — out of scope

## Alpha Risk Acceptance

- Eval workflow (HUM-1388) still in progress but not a blocking gate.
- Manual smoke tests require real bot credentials; not runnable in CI.
