# Context gathering for Luvr v0.1.0: Instagram + self-summary

**Status:** v0.1.0 recommendation  
**Authors:** Humphrey Ahn + pi coding agent  
**Date:** 2026-06-20

## Research questions & answers

### 1. What context improves dating advice quality most?

| Context signal      | Quality impact | Effort | v0.1.0? |
|---------------------|---------------|--------|---------|
| Instagram public bio/summary | High — helps Luvr understand personality, tone, interests | Medium (parse URL, scrape public page) | Yes |
| Self-summary (user-written) | High — user self-describes what matters to them | Low (text input) | Yes |
| Photo style (Instagram grid) | Medium — visual cues about lifestyle | High (computer vision) | No |
| Full caption history | Low-medium — noisy, high risk of overfitting | High (scraping reliability) | No |
| Social graph / follower count | Low — not useful for dating advice | Low | No |

### 2. What should come from Instagram vs a self-summary fallback?

- **Instagram:** try to extract bio line, theme keywords from public captions if the account is public. Keep it brief (≤300 chars summary).
- **Self-summary fallback:** if Instagram is private, unavailable, or scraping fails, present a short non-corny prompt: *"Tell me a bit about yourself — what kind of person are you, what do you enjoy, and what's your dating vibe?"*
- **Never force:** always allow skipping. The bot works fine with zero context.

### 3. What should never be collected in v0.1.0?

- Private account content (must not require following).
- DMs, story content, location data.
- Real names unless intentionally provided.
- Phone numbers beyond Telegram linking.
- Photos stored outside ephemeral processing.
- Any data used for persistent memory (out of scope for v0.1.0).

### 4. How should context appear in prompts without feeling creepy?

Context should be injected as a **discreet, factual preface** before the user message, not as an explicit "profile dump":

```
## About the person you're talking to
- They describe themselves as: [self-summary or Instagram-derived summary]
- Their general vibe: [derived from Instagram bio if available]
```

Never say "I looked at your Instagram" in responses. Let context inform tone, not content.

### 5. How should this be evaluated in Weave?

- Add `has_instagram_context: bool` and `context_source: "instagram"|"self_summary"|"none"` labels to eval spans.
- Compare eval scores for conversations with vs without Instagram context.
- Track whether context summary is present but empty (signals scraping failure).

### 6. What should the Telegram→web→Telegram journey feel like?

- Telegram: user taps `/link`
- Web: auth page → (optional) Instagram handle → self-summary fallback → "Done!" with back-to-Telegram button
- Telegram: bot sends a short confirmation: "Got it! I'll use what you shared to give better advice. 💝"
- Total: ≤3 minutes, ≤4 screens.
