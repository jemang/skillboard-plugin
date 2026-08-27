---
name: handoff
description: Use when the current SESSION's work must be packaged so a fresh agent can resume it cold — user says "handoff", "write a handoff", "summarize this session for a fresh agent", "I'm running out of context", "context is getting full", "prep this for another session", "pass this to a new agent", or a long session is winding down and continuity matters. NOT for documenting the codebase itself for new team members — that is the handover-docs skill (if installed). Saves/updates handoff.md at the project root.
---

# Handoff

Produce a single Markdown file that lets a fresh agent resume this work **cold** — no access to the current conversation, only the file. Optimize for "the next reader has never seen any of this."

## Where to save

Save as `handoff.md` at the **app/project root** — the top of the repo, alongside the project's
own `README` / `composer.json` / `package.json`. Living at the root (not a temp dir) means the
next agent finds it the instant it opens the project, and every subsequent handover **updates the
same file in place** instead of scattering timestamped copies.

Resolve the root at runtime rather than hardcoding:

```bash
# nearest git repo root; fall back to the current working directory
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
FILE="$ROOT/handoff.md"
```

Use the fixed name `handoff.md` (no timestamp) so it stays a single, re-updatable living document.
If `handoff.md` already exists, this is a **re-update**, not a fresh write — see below.

One caveat: a root `handoff.md` is inside the repo, so it can be accidentally committed. If the
user doesn't want it tracked, offer to add `handoff.md` to `.gitignore`. It also means the
redaction step below matters more — treat this file as potentially shareable.

## Updating an existing handoff.md

Because the file is a living document, before writing, check whether `handoff.md` already exists at
the root. If it does, **read it first** and refresh it rather than blindly overwriting: keep the
context and decisions that are still true, update "Current state" and "Next steps" to reflect what
this session changed, and move anything now-finished out of "Next steps". Preserve the reader's
mental model across handovers — the goal is one file that gets better each pass, not a rewrite that
loses hard-won history. Update the `Created`/`Last updated` line to the new timestamp.

Two checks while refreshing (they keep an old handoff from misleading the next agent):

- **Stale references:** verify the file paths and symbols the existing handoff names still exist
  (`ls`, grep). Mark anything missing as `stale — verify, likely renamed/moved` rather than silently
  keeping or guessing; the next agent resolves it by reading code.
- **Plan vs. reality:** compare the previous "Next steps" against what actually happened this
  session — record answered open questions and materialized risks under "Key context & decisions",
  so the handoff carries momentum, not just a fresh snapshot.

## Core principle: reference, don't duplicate

Anything already captured durably elsewhere — PRDs, design docs, ADRs, plans, GitHub issues/PRs, commit messages, diffs, test output files — is a **link, not a paste**. Duplication rots: the moment you copy a plan into the handoff, the two versions drift and the next agent can't tell which is authoritative. Reference by path or URL and add only the one line of context the reader needs to know *why* it matters.

Bad: pasting the full migration diff into the handoff.
Good: `` See migration `database/migrations/2026_06_29_000001_add_user_is_active.php` — adds the `is_active` column the middleware depends on. ``

The handoff's job is the connective tissue that *isn't* written down anywhere else: what's in flight, what was tried, what's decided, what's still open, and the hard-won context that lives only in this conversation.

## Redact sensitive information

Before writing, scan what you're about to include and redact secrets and PII — API keys, tokens, passwords, connection strings with credentials, private keys, `.env` values, personal emails/phone numbers, customer data. Replace with a placeholder that preserves meaning without the secret, e.g. `DATABASE_URL=postgres://user:[REDACTED]@host/db` or `API key: [REDACTED — see 1Password / project secrets]`. The next agent needs to know a credential exists and where it lives, not its value. A handoff file lives at the repo root where it can be committed or shared, so treat it as if it could leak.

## Tailoring to the next focus (arguments)

If the user passed arguments, treat them as a description of what the **next** session will focus on, and shape the whole document around that. Lead with the parts of the current state that matter for that goal, and let the "Next steps" reflect it directly. If no arguments were passed, write a general-purpose handoff covering wherever the work currently stands.

Example: args = `"focus on getting the token UI tests green"` → foreground the test files, the failing assertions, and what's been tried; background unrelated threads.

## Gather the material first

Before writing, reconstruct the session honestly. Pull from: the conversation history, files you read or modified, commands you ran and their results, decisions the user made or corrected, and dead ends you hit. Don't invent progress — if something was attempted but unverified, say so. A handoff that overstates completion is worse than useless; the next agent builds on sand.

Check git state if in a repo (`git status`, `git log --oneline -10`, current branch) so the file records exactly what's staged, modified, or committed. Reference that state — don't reproduce the diff.

## Document structure

Use this template. Drop sections that genuinely don't apply rather than padding them, but keep the order.

```markdown
# Handoff: <short title of the work>

**Created:** <ISO timestamp>  ·  **Last updated:** <ISO timestamp>  ·  **By:** Claude (<model>)  ·  **Repo/branch:** <if applicable>
**Next session focus:** <from arguments, or "general — resume where left off">

## TL;DR
<3-5 sentences: what this work is, where it stands right now, and the single most important
thing the next agent should do first. Someone should be able to read only this and not be lost.>

## Current state
<What is done and verified vs. done but unverified vs. in progress. Be precise about which is which.>

## Key context & decisions
<The reasoning that lives only in this conversation: why an approach was chosen, constraints the
user stated, things the user corrected you on, assumptions in play. Link decisions recorded in
ADRs/PRDs rather than restating them.>

## Next steps
<Ordered, concrete actions. Each should be startable without re-deriving context. Tailor to the
next-session focus if arguments were given.>

## Watch out for
<Gotchas, dead ends already tried (so they aren't repeated), fragile areas, flaky tests,
environment quirks.>

## References
<Artifacts, by path or URL, one line of "why it matters" each. PRDs, plans, ADRs, issues, PRs,
commits, key source files, docs. This replaces pasting their contents.>

## Suggested skills
<See below.>
```

## Staleness — the reader weighs age

`Last updated` is not decoration; it tells the next agent how much to trust the rest. If real time has passed, "Current state" is a claim to re-verify (`git log`, `git status`, the test suite) before building on it — work may have continued outside this file. Say that in one line inside the document when the gap is likely to matter, so the next agent checks instead of assuming.

## The "Suggested skills" section

This is what turns a summary into an actionable handoff. Look at what the next steps require and recommend the specific skills the fresh agent should invoke, each with a one-line reason tied to the next step it serves. Pull from the skills actually available in the environment — don't invent skill names. Common fits:

- Resuming a written plan → `superpowers:executing-plans` or `superpowers:subagent-driven-development`
- A bug to chase → `superpowers:systematic-debugging`
- New feature/behavior work → `superpowers:brainstorming` then `superpowers:test-driven-development`
- Finishing/merging a branch → `superpowers:finishing-a-development-branch`
- Understanding an unfamiliar area of the code → `feature-explainer` (if available)
- About to claim done → `superpowers:verification-before-completion`
- A plan exists or will be made → `persisting-plans` (keep `.doc/` plan files current alongside this handoff)

Format each as `` `skill-name` — why the next agent should use it here. ``. If nothing applies, say so plainly rather than padding.

## Final step

After writing, output the absolute file path and a one-line summary of what's in it, and say whether
this was a fresh write or an in-place update, so the user knows the living doc is current
(e.g. "updated `/Users/you/app/handoff.md` — refreshed current state + next steps for the
login/is_active fix and the token UI tests").
