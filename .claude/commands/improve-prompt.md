---
description: Improve the Luvr persona prompt using eval evidence.
argument-hint: [eval-name]
allowed-tools: Read, Grep, Glob, Bash(git diff:*), Bash(git status:*), Bash(make:*)
---

You are improving Luvr's persona prompt from eval evidence.

Eval name: `$ARGUMENTS`

If no eval name is provided, use `luvr-eval-v1`.

Follow this workflow:

1. Confirm the working tree state with `git status --short --branch`.
2. Locate the persona/prompt code and eval coverage related to the eval name.
3. Read the relevant eval cases, metrics, and prompt construction code before proposing edits.
4. Use Weave results only if they are available in the current context; otherwise rely on local eval files and say that trace evidence was unavailable.
5. Identify the smallest prompt change likely to improve the eval without weakening product voice.
6. Make the prompt edit only if the requested change is concrete enough to implement.
7. Run the narrowest relevant eval or test target available.

Keep the Luvr voice:

- Direct, warm, and text-native.
- Grounded in user context instead of generic coaching.
- No therapy disclaimers, pickup-artist framing, or ornate mystical language.
- Bilingual only when the user context calls for it.

Return:

- Eval: the eval name used and matching local evidence.
- Diagnosis: the observed prompt weakness.
- Change: exact files and prompt text changed or proposed.
- Verification: command output summary and remaining risk.
- Follow-up: one next eval or prompt experiment if useful.
