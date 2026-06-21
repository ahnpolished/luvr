# Context Gathering Research: Instagram + Lightweight Self-Summary

Recommendation for what context Luvr should gather in v0.1.0 to make dating
advice better, without making onboarding feel intrusive. This informs the
Instagram integration and Telegram-native context gathering work.

## What context improves dating advice quality most

In rough priority order for v0.1.0:

1. **Self-described dating goals/status** (volunteered, not extracted) — the
   single highest-leverage signal; advice that ignores stated goals reads as
   generic.
2. **Communication/tone preference** (e.g. casual vs. direct) — cheap to
   collect, immediately visible in response quality.
3. **A short public-facing bio/handle hint** (Instagram bio, or a one-line
   self-summary) — useful for flavor and specificity, but materially weaker
   than #1 and #2.
4. **Recent public activity hints** (e.g. an Instagram bio line) — lowest
   value, highest creepiness risk if over-collected.

Conclusion: a short, user-provided summary does more for advice quality than
deep social-media extraction. Instagram should be treated as a *flavor*
source, not a primary signal.

## Instagram vs. self-summary fallback

- **Instagram in scope for v0.1.0**: handle + bio + an optional one-line
  "recent public hint," all explicitly typed/pasted by the user during web
  onboarding. No scraping, no API pull, no follower/following graph.
- **Self-summary fallback**: when a user skips Instagram or it can't be read,
  ask one short, non-corny free-text question instead (e.g. "two lines about
  yourself" ) so context collection never blocks on a single provider.
- Both paths terminate in the same shape: a short text summary attached to
  the alpha profile, capped (280 chars per field), never raw scraped HTML or
  follower lists.

## What should never be collected in v0.1.0

- No automated Instagram scraping or third-party data pulls — only what the
  user explicitly types or pastes.
- No full conversation transcripts or photos/voice files treated as context.
- No information about other people who haven't consented.
- No persistent, retrievable long-term memory — this is alpha-session
  context only (see `AUTH_MEMORY.md` for the longer-term memory boundary).
- No X/Twitter or any other social platform — Instagram only, per the
  v0.1.0 decision constraints.

## How context should appear in prompts

Context should read like something a friend would mention, not a profile
dump:

- Inject as 1–2 short natural-language clauses (e.g. "they mentioned on
  Instagram that they're into hiking"), not as raw JSON or a labeled field
  list.
- Never quote the user's bio verbatim back to them — paraphrase so it
  doesn't feel surveilled.
- Omit entirely when context is empty rather than prompting the model with
  "no context provided."
- Treat the self-summary fallback identically to Instagram-derived context
  in the prompt — the model shouldn't need to know the source.

**Gap found during this research:** `instagram_context_summary` is stored on
the alpha profile (`src/alpha/registry.py`) but is not yet read by any
prompt-building code in `src/llm` or `src/handler`, and is not included in
`weave_labels_for_telegram`. Context is captured but not yet consumed. This
should be a fast-follow rather than blocking v0.1.0, but the release gate
(HUM-1397) should explicitly call it out as an accepted alpha risk if it
isn't closed before release.

## How this should be evaluated in Weave

- Label traces with whether context was present (`has_instagram_context`,
  `has_self_summary`) and its source, not the raw text, so eval datasets can
  segment "with context" vs. "without context" without re-exposing personal
  data in trace listings.
- Curate a small eval set with paired prompts (same scenario, with and
  without context) to check that context measurably changes response
  specificity without overriding the user's stated goals.
- Redact bios/summaries before promoting any trace into a long-lived
  regression dataset, consistent with the eval-trace policy already in place
  for v0.1.0.

## Telegram → web → Telegram journey

- Telegram bot sends a single short-lived link when the user wants richer
  advice or hits the alpha context step.
- Web flow: authenticate → connect Instagram or skip → (if skipped or
  unreadable) one short self-summary prompt → confirmation screen.
- Redirect/deep-link back to Telegram immediately after confirmation; the
  bot should acknowledge completion in-chat rather than leaving the user on
  the web page.
- Total flow should stay at or under 4 screens, matching the onboarding
  acceptance criteria already shipped in `HUM-1391`.

## Status

This recommendation reflects and validates the context-gathering approach
already implemented in `HUM-1379` (web Instagram integration) and `HUM-1391`
(web onboarding flow). No implementation changes are proposed here beyond
the prompt/Weave-label gap noted above, which is left for a follow-up issue.
