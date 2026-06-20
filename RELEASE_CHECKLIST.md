# v0.1.0 Release Readiness Checklist

Last updated: 2026-06-20

## Automated Checks

- [x] `pytest` passes — 211 passed, 0 failed
- [x] `ruff check src/ tests/` passes — All checks passed
- [x] `mypy src` passes — Success: no issues found in 51 source files
- [x] Telegram smoke test passes with mock data — All handlers OK (text, photo, voice, error handling)

## Manual Verification

- [ ] Real-bot smoke test: text message → dating advice response
- [ ] Real-bot smoke test: photo message → image analysis response
- [ ] Real-bot smoke test: voice memo → transcription + dating advice + optional TTS reply
- [ ] Real-bot smoke test: /start command → welcome message
- [ ] Real-bot smoke test: /link command → deep-link URL for web onboarding
- [ ] Web auth: Telegram user opens deep-link, authenticates, returns to Telegram
- [ ] Instagram context: user can connect Instagram on web onboarding
- [ ] Instagram context: user can skip Instagram connection
- [ ] Instagram context appears on alpha profile after connection
- [ ] Tarot reading: /tarot initiates a tarot card reading flow
- [ ] Manual proactive message: `scripts/manual_proactive_checkin.py` runs successfully
- [ ] Weave traces: at least one linked alpha user's conversation produces labeled Weave traces
- [ ] Eval workflow: `scripts/run_weave_conversation_eval.py` can run against a synthetic dataset

## Policy & Docs

- [x] Security policy documented in `SECURITY.md` — covers access control, data handling, third-party services, safety, media limits, operational baseline
- [x] Eval trace policy implemented in `src/eval_trace_policy.py` — consent gate + retention (7–30 days)
- [x] Architecture documented in `ARCHITECTURE.md`
- [x] Design brief in `DESIGN_BRIEF.md`
- [x] Setup guide in `SETUP.md`

## Out-of-Scope Verification

These items are explicitly out of scope for v0.1.0. The codebase has been checked:

- [x] Kakaotalk — no Kakaotalk integration code exists
- [x] X/Twitter — no Twitter integration code exists
- [x] Payment — no payment/entitlement logic exists
- [x] Persistent product memory — `src/memory/` exists as research prototype only, not wired into conversation flow
- [x] Autonomous scheduler — no autonomous outbound message scheduling exists
- [x] User-editable memory UX — no memory management UI exists

## Accepted Alpha Risks

The following are accepted as known alpha risks:

1. **Manual real-bot smoke test**: Requires live Telegram bot token and API keys. The mock smoke test validates all handler logic; real-bot testing is a manual step.
2. **Weave trace verification**: Requires W&B/Weave credentials and at least one consenting alpha user. The infrastructure is in place (`src/weave_spans.py`, `src/eval_workflow.py`).
3. **Eval workflow run**: Requires W&B/Weave credentials. The CLI entry point exists (`scripts/run_weave_conversation_eval.py`) and the eval workflow logic is tested.
4. **Instagram context live flow**: Requires Meta developer app configuration. The web onboarding flow and alpha profile storage are implemented and tested.
