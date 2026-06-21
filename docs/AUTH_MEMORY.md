# Auth + Memory Research Recommendation

This document tracks the boundary between **v0.1.0 lightweight web auth/linking** and the upcoming **XL research ticket for persistent product memory**.

v0.1.0 now includes lightweight web authentication, Telegram ↔ web linking, and Instagram onboarding. The remaining research question is how Luvr should safely build long-term product memory after v0.1.0.

## Context

Luvr needs two related but distinct capabilities:

1. **v0.1.0 identity/onboarding**: recognize alpha users enough to link Telegram to a web-authenticated profile, collect Instagram context, label Weave traces, enforce usage limits, and return smoothly between Telegram and web.
2. **Post-v0.1 product memory**: remember useful context over time and retrieve it in future conversations.

The v0.1.0 identity/onboarding plan is:

- Telegram provides a natural link to a mobile web auth/onboarding flow.
- User authenticates on the web.
- User connects/provides Instagram context on the web.
- Web redirects or deep-links the user back to Telegram.
- Luvr stores a minimal alpha profile and short context summary.

Persistent product memory remains research/prototyping scope, not a v0.1.0 production requirement.

## Eval traces vs. product memory

Luvr v0.1.0 can save conversation/evaluation traces without shipping persistent product memory.

The difference:

- **Eval traces** are short-lived records used by maintainers to debug conversations, run Weave evals, improve prompts, and create redacted regression datasets.
- **Product memory** is long-term user-facing memory that the bot retrieves in future conversations to personalize responses.

v0.1.0 should allow limited eval traces for consenting alpha users because realistic prompt evaluation needs conversation and context. v0.1.0 also includes lightweight web auth and Telegram linking. That does not mean v0.1.0 must solve long-term memory, automatic memory retrieval, or user-editable memory.

Recommended v0.1.0 stance:

- Save enough trace data to reproduce and evaluate conversations.
- Label traces with prompt version, model, message type, user/channel identifier, and selected metadata.
- Avoid retaining raw photo/audio files by default.
- Retain raw conversation traces for a short window, for example 7–30 days.
- Promote only redacted or synthetic examples into long-term eval datasets.
- Do not use saved traces as automatic future memory for the bot.

The persistent product memory XL ticket should decide how, when, and whether trace/profile/context data can safely graduate into explicit user-approved memory.

## Research goals

The XL ticket should answer:

1. What user context should become long-term product memory, and what should not?
2. Should memory be built in-house, bought as a managed tool, or hybrid?
3. How do we support deletion, consent, inspection, and debugging from the beginning?
4. How should memory interact with the v0.1.0 alpha profile and Instagram context summary?
5. What is the minimum memory data model for v0.2.0?
6. What should be explicitly deferred?

## Recommended research approach

Try at least **3 complete candidate memory approaches**, not just isolated tools.

Each candidate should cover:

- How it uses the v0.1.0 alpha user profile as identity input.
- User profile / memory storage model.
- Memory write/read behavior.
- Deletion and consent flow.
- Local development ergonomics.
- Cost and operational burden.

Example candidate stacks to evaluate:

### Candidate A: Managed auth + Postgres memory

Examples:

- Clerk, Auth0, Supabase Auth, WorkOS, Firebase Auth.
- Postgres plus pgvector, hosted through Supabase, Neon, RDS, or similar.

Why try it:

- Strong auth primitives.
- Clear data ownership.
- Easy to inspect and migrate.
- Good fit if Luvr wants custom memory rules.

Risk:

- More application code to write.
- Memory quality depends on our extraction/retrieval design.

### Candidate B: Backend platform with auth + database + storage

Examples:

- Supabase.
- Firebase.
- Appwrite.

Why try it:

- Fastest way to prototype account, database, storage, and admin workflows together.
- Good local/dev story may reduce setup burden.

Risk:

- Platform conventions may shape architecture too strongly.
- Migration path and vendor lock-in need review.

### Candidate C: Specialized memory layer + separate auth

Examples:

- Zep.
- Mem0.
- LangGraph Store / LangMem-style memory.
- LlamaIndex memory components.

Why try it:

- Faster experimentation with conversation memory behavior.
- May provide summaries, retrieval, and memory management out of the box.

Risk:

- Privacy, deletion, observability, and data portability need careful validation.
- May be too much abstraction for an early product.

### Candidate D: Minimal custom memory first

Examples:

- Managed auth provider.
- Small `users`, `channel_accounts`, `memories`, and `memory_events` tables.
- Simple embedding/retrieval later, not on day one.

Why try it:

- Maximum control and easiest to reason about.
- Good for a sensitive product where memory must feel trustworthy.

Risk:

- Slower to reach advanced memory quality.
- Requires discipline to avoid overbuilding.

## Suggested current recommendation

Start the research with this bias:

> Prefer managed auth for identity, and prefer a simple owned database for early memory unless a specialized memory tool clearly proves better on privacy, deletion, quality, and developer speed.

Reasoning:

- Auth is security-sensitive and usually not worth building from scratch.
- Memory is product-sensitive and should remain understandable.
- Early Luvr memory should be sparse, explicit, editable, and deletable.
- A black-box memory layer may move faster at first but could make trust, debugging, and deletion harder.

This is only a starting hypothesis. The XL ticket should validate or reject it with prototypes.

## Minimum product requirements

A successful product-memory design should support:

- The system can use the v0.1.0 alpha profile as the identity anchor.
- The user can see that memory exists.
- The user can request memory deletion.
- The bot can use approved memory in a response.
- The bot can still work when memory is unavailable.
- The implementation avoids storing raw media by default.
- The implementation separates eval traces from product memory.
- The implementation avoids using full conversation history as product memory unless explicitly approved.

## Memory principles

Memory should be:

- **Consent-based**: users should know when Luvr remembers things.
- **Sparse**: store durable facts and preferences, not every message.
- **Useful**: memory should improve advice quality, not just accumulate data.
- **Editable/deletable**: users should be able to correct or remove memory.
- **Auditable**: developers should be able to explain why a memory was used.
- **Safe by default**: avoid storing highly sensitive details unless clearly necessary.

Examples of reasonable early memories:

- Preferred name or nickname.
- Language preference.
- Dating status if the user volunteered it.
- Communication style preference.
- Stated dating goals.
- Important boundaries or preferences.

Examples to avoid in early product memory unless explicitly designed:

- Full conversation transcripts.
- Photos or voice recordings.
- Third-party social-media content.
- Highly sensitive sexual, medical, legal, or financial details.
- Information about other people who did not consent.

These may still appear temporarily in alpha eval traces when needed for debugging or prompt evaluation, but they should not automatically become long-term memory.

## v0.1.0 account linking decision

Account linking is now implementation scope for v0.1.0, not part of the memory research comparison.

Chosen flow:

1. User starts or chats with the Telegram bot.
2. Bot sends a secure short-lived link to web auth/onboarding.
3. User authenticates on the web.
4. User provides Instagram context or skips it.
5. Web links the authenticated profile to the Telegram user/chat.
6. Web redirects or deep-links the user back to Telegram.
7. Bot confirms successful setup.

The memory research should build on this identity anchor rather than reopen the account-linking decision unless v0.1.0 implementation proves it insufficient.

## Success criteria for the XL ticket

The XL ticket is successful when it produces:

### 1. Prototype evidence

- At least 3 candidate memory approaches tried.
- Each candidate has a short prototype, branch, script, or demo notes.
- Each candidate demonstrates at least one memory read/write path anchored to a v0.1.0-style user profile.

### 2. Security and privacy answer

For the recommended approach, document:

- What data is stored as eval trace.
- What data is stored as product memory.
- Where each type of data is stored.
- How deletion works for traces and memory.
- How consent works.
- How secrets are managed.
- What appears in logs and traces.
- What third parties receive.

### 3. Developer experience answer

The recommended approach should be practical for one maintainer:

- Local setup under 30 minutes.
- Clear test strategy.
- No excessive infrastructure.
- Simple migration path.
- Easy manual inspection during alpha.

### 4. Product quality answer

The recommendation should show that memory improves the Luvr experience:

- At least 5 realistic conversation scenarios tested.
- At least 2 Korean/English scenarios tested if multilingual support remains in scope.
- Memory use feels helpful rather than invasive.
- Bot can explain or gracefully avoid using memory when uncertain.

### 5. Operational answer

The chosen path should include:

- Rough monthly cost estimate for alpha and early beta.
- Failure modes and fallback behavior.
- Rate-limit implications.
- Monitoring/debugging plan.
- Known lock-in risks.

### 6. Decision artifact

The ticket should end with a written recommendation containing:

- Recommended stack.
- Rejected alternatives and why.
- Proposed v0.2.0 implementation plan.
- Minimum schema or architecture diagram.
- Open questions that still need product decisions.

## Evaluation rubric

Score each candidate from 1 to 5:

| Criterion | Weight | Notes |
|---|---:|---|
| Security | 5 | Secret handling, account linking safety, least privilege. |
| Privacy/deletion | 5 | Can users understand and remove stored data? |
| Product fit | 5 | Does memory improve dating-advice quality? |
| Simplicity | 4 | Can one maintainer operate it? |
| Developer speed | 4 | How quickly can we ship a safe v0.2? |
| Data ownership | 4 | Can we inspect, export, and migrate data? |
| Observability | 3 | Can we debug without leaking private content? |
| Cost | 3 | Reasonable for alpha/beta usage. |
| Multichannel readiness | 3 | Can Telegram, Kakaotalk, and future channels map to one user? |
| Vendor lock-in | 2 | Can we leave without rewriting everything? |

A candidate should not be chosen if it scores poorly on security or privacy, even if it is fast.

## Recommended non-goals

The XL ticket should not attempt to ship all of this at once:

- Full production auth rollout.
- Payment integration.
- Social-media scraping.
- Multi-channel production account merge.
- Complex long-term memory ranking.
- Admin dashboard for all user data.
- Productionized automated Weave prompt revision pipeline.

Basic Weave eval traces and manual prompt-evaluation workflow may remain in v0.1.0. The auth + memory XL ticket should not try to solve the full automated revision system unless it is explicitly expanded.

Those should come after the auth + memory foundation is chosen.

## Proposed ticket title

**[XL] Research and prototype persistent product memory architecture for Luvr**

## Proposed ticket acceptance criteria

- At least 3 candidate memory approaches are prototyped or deeply evaluated.
- Each candidate includes memory write, memory read, deletion, consent, and local-dev notes.
- Each candidate explains how eval traces differ from product memory.
- Each candidate explains how it anchors memory to the v0.1.0 alpha user profile.
- Security/privacy trade-offs are documented for each candidate.
- A weighted recommendation is written with clear rationale.
- A v0.2.0 implementation plan is proposed but not necessarily implemented.
