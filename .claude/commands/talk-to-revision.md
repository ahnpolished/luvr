---
description: Analyze a Luvr revision for implementation.
argument-hint: [revision-id]
allowed-tools: Read, Grep, Glob, Bash(git show:*), Bash(git diff:*), Bash(git log:*), Bash(git status:*)
---

You are helping implement or review a specific Luvr revision.

Revision id: `$ARGUMENTS`

If no revision id is provided, stop and ask for one.

Follow this workflow:

1. Confirm the working tree state with `git status --short --branch`.
2. Locate all repo references to the revision id with search before drawing conclusions.
3. Inspect the surrounding files and recent git context relevant to that revision.
4. Summarize what the revision is trying to change in plain implementation terms.
5. Identify the smallest safe next step, including exact files likely to change.
6. Call out blockers, missing context, or risky assumptions explicitly.

Return:

- Revision: the id and any matching source context.
- Intent: the concrete behavior or product change implied by the revision.
- Implementation notes: concise, file-level guidance.
- Verification: commands or checks that should be run after changes.
- Open questions: only if the next implementation step is genuinely ambiguous.
