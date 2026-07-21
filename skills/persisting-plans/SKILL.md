---
name: persisting-plans
description: Use when a plan has just been formed or approved — after plan mode, after writing an implementation plan, before starting multi-step work, or when a spawned agent produces a plan. Also use when resuming work to check for an existing plan. Triggers on "save the plan", "persist the plan", starting execution of any plan, and session start in a repo that has a .doc folder.
---

# Persisting Plans

Every plan lives on disk, not just in conversation. Context gets compacted, sessions end, agents change — a plan that exists only in chat is lost work.

## The Rule

After forming or updating ANY plan (plan mode, written plan, agent-produced plan): write it to `.doc/` at the root of each active repo/app before starting execution.

Note: plan-mode plans auto-save into `.doc/` via the `plansDirectory` setting **with a harness-generated random slug** (e.g. `nifty-meerkat.md`) — you don't pick that name. **Step 1: rename it to the convention** — `mv .doc/<slug>.md .doc/YYYY-MM-DD-NN-<topic>-plan.md` (plan-mode plans are `type=plan`). Then don't duplicate — ADD the Status / Current position / Decisions fields below to the renamed file and keep them updated. Renaming is the ONLY way the convention reaches plan-mode files; skip it and they keep the random slug.

```bash
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
mkdir -p "$ROOT/.doc"
```

One `.doc/` per active repo. If work spans multiple repos, each gets its own plan file.

## File format

Name: `.doc/YYYY-MM-DD-NN-<short-kebab-topic>-<type>.md` — creation date + 2-digit per-day sequence (`NN` = that day's existing `.doc/YYYY-MM-DD-*` count +1) + kebab topic + trailing type `plan` (implementation plan) or `design` (design spec), e.g. `2026-07-21-01-super-admin-redesign-plan.md`. The trailing type distinguishes a plan from a design spec when all `.doc/*.md` are read on resume. Set date/`NN`/type **once at creation**; on resume keep updating that same file — don't spawn a new dated one.

```markdown
# Plan: <title>

**Status:** planning | in-progress | blocked | done
**Updated:** <ISO timestamp>
**Intent:** <one sentence — why this work exists>

## Steps
- [ ] step — <file/symbol it touches>
- [x] done step — <what was verified>

## Current position
<exactly where execution stands; what the next agent should do first>

## Decisions & constraints
<choices made + why, user corrections, assumptions>
```

## Keep it live

- Tick checkboxes and update **Status** / **Current position** as steps complete — a stale plan misleads the next agent worse than no plan.
- On resume: read existing `.doc/*.md` plans FIRST before re-planning.
- Mark abandoned plans `Status: done` or delete them; don't leave zombies.
- Plans reference files by path; don't paste diffs or file contents.

## Red flags

- "The plan is short, I'll keep it in my head" → write it anyway.
- "I'll save it after the first step" → save BEFORE executing.
- "Plan mode already showed the user" → chat is not disk. Persist it.

Related: `handoff` packages a whole session; this skill persists just the plan artifact and is cheaper — use both when a session ends mid-plan.
