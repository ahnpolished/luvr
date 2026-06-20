# Persistent Product Memory Architecture: v0.2.0 research

**Status:** v0.1.0 research output  
**Date:** 2026-06-20

## Scope

This document evaluates candidate approaches for persistent product memory in Luvr v0.2+. Product memory means: long-term storage of conversation history / user facts that persists across sessions, enabling Luvr to reference past conversations naturally ("you mentioned last week that...").

This is separate from:
- **Eval traces** (short-lived, anonymized, for Weave evaluation only)
- **Registry** (operational profile metadata: Telegram IDs, auth status, usage counters)
- **Instagram context** (short summary stored on alpha profile)

## Candidates evaluated

### 1. SQLite + embeddings (in-house)

**Write:** Each conversation turn is saved as a row with (user_id, timestamp, role, content, embedding). Embeddings generated via OpenAI `text-embedding-3-small` or similar.

**Read:** On each new message, embed the query text and do cosine similarity search over recent conversations. Inject the top-K relevant past turns into the LLM prompt.

**Deletion:** SQL DELETE by user_id or timestamp. Privacy-respecting.

**Local dev:** SQLite requires zero setup. Embedding model calls need API key.

**Cost:** ~$0.02/1K embeddings. Storage cost negligible for alpha scale.

**Operational burden:** Low. Python's sqlite3 stdlib. No external service.

**Security:** All data on Railway node. Encryption at rest via filesystem. No external data store.

### 2. Managed vector DB (Pinecone / Weaviate)

**Write:** Embedding → upsert into hosted vector index with metadata.

**Read:** ANN search with metadata filtering. Better performance at scale.

**Deletion:** Supported via metadata-based delete.

**Local dev:** Requires running a local Pinecone/Weaviate instance or mock.

**Cost:** Pinecone free tier is generous. Weaviate open-source self-hosted possible.

**Operational burden:** Medium. Another service to manage, monitor, pay for.

**Security:** Data leaves Railway. Pinecone is SOC 2 compliant.

### 3. Memory-as-a-service (Mem0 / LangChain Memory / Zep)

**Write:** High-level API abstracts storage, embedding, and retrieval.

**Read:** Simple `memory.search("what does user like?")` API.

**Deletion:** Supported via API.

**Local dev:** API keys + network calls. Easiest to prototype.

**Cost:** Mem0 free tier limited. Zep open-source self-hosted option.

**Operational burden:** Low for managed; medium for self-hosted Zep.

**Security:** Third-party data processor. Needs DPA review.

## Hybrid option (recommended for v0.2.0)

**SQLite + embeddings for v0.2.0**, with optional upgrade path to managed vector DB later.

Rationale:
1. Lowest operational burden — no new service dependency.
2. Zero additional cost for alpha scale (≤50 users).
3. Complete data sovereignty — all data stays on Railway.
4. Easy to delete user data (DELETE FROM conversations WHERE user_id=?).
5. Embedding search via brute-force cosine similarity works fine for <10K conversations.
6. Architecture is modular: if scale demands it, swap sqlite for Pinecone with minimal code changes.

## v0.2.0 implementation plan

### Phase 1: Conversation storage
- Add `conversations` table to SQLite (or JSON file for alpha).
- Store: user_id, role (user/assistant), content, embedding, timestamp.
- Generate embeddings on each message.

### Phase 2: Retrieval
- On each new message, embed and search top-5 relevant past turns.
- Inject into system prompt as "## Relevant past conversations".
- Gate behind feature flag/alpha user allowlist.

### Phase 3: Deletion & consent
- DELETE by user_id.
- Auto-expire conversations older than 30 days (v0.2 alpha policy).
- /forget command to trigger immediate deletion.

## Security & privacy trade-offs

| Approach | Data location | Deletion ease | GDPR readiness | Alpha suitability |
|----------|--------------|---------------|----------------|-------------------|
| SQLite   | Railway node | Immediate     | Good           | Excellent         |
| Pinecone | US cloud     | API call      | Requires DPA   | Good              |
| Mem0     | US cloud     | API call      | Requires DPA   | Good              |

## How eval traces differ from product memory

| Aspect | Eval traces | Product memory |
|--------|------------|----------------|
| Purpose | Evaluate prompt quality | Improve conversation quality |
| Retention | 7-30 days | 30+ days |
| Content | Redacted/synthetic by default | Real conversations (consented) |
| Access | Admin/operator only | Used by LLM at inference time |
| Storage | Weave (W&B) | Application database |

**Golden rule:** eval traces are NEVER used for product memory, and product memory is NEVER used as eval data without explicit consent and redaction.
