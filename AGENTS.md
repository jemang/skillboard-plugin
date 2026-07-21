# Skillboard (Codex)

Portable agent setup. On Codex this ships **skills + these instructions**, and Codex runs the sync SessionStart/tool hooks from `hooks/hooks.json`. The one async hook (memory-index + dashboard refresh) isn't supported on Codex and is skipped — run the `skillboard` command manually to refresh the index/dashboard. Codex has no skill auto-routing, so use the index below to pick a skill by hand.

## Skill index — read the skill's `SKILL.md` when its trigger fits

| When | Skill |
|---|---|
| Before writing/adding/refactoring/fixing code, or adding a dependency | `skills/lazy-code/` — the laziest solution that works (YAGNI, reuse, stdlib, one line) |
| A plan was formed/approved, or resuming work | `skills/persisting-plans/` — write it to `.doc/`, keep Status current |
| Ending a session mid-work / handing off | `skills/handoff/` — a fixed `handoff.md` at repo root, updated in place |
| "What did we decide about X?" | `skills/memory-recall/` — search the memory index before re-deriving |
| Choosing between viable tech/product routes | `skills/decision-routes/` |
| Writing onboarding / dev documentation | `skills/dev-docs/` |
| A multi-step workflow repeats and should be frozen | `skills/self-learning/` |
| Bootstrapping a fresh machine | `skills/skillboard-init/` |

## Standing discipline

**Surgical changes.** Every changed line traces to the current request. Don't improve/refactor/reformat adjacent code — match existing conventions. Mention unrelated issues, never act unasked. Remove only orphans your change created. State multiple interpretations before picking; name a simpler approach if one exists. Never replicate a genuinely harmful pattern (security, data loss) for consistency — flag it.

**Lazy-code ladder.** Before writing code, stop at the first rung that holds: (1) does it need to exist? (2) already in this codebase — reuse it. (3) stdlib. (4) native platform feature. (5) already-installed dependency. (6) one line. (7) only then, minimum code that works. Never simplify away: understanding the problem, input validation at trust boundaries, error handling, security, accessibility, runtime performance on hot/large-input paths, or the readability the next reader needs.

**Memory routing — one fact, one home.** Repo gotcha → that repo's conventions. Cross-repo preference/feedback → auto-memory. Work-in-progress → `handoff.md` + `.doc/`. Personal knowledge → the remember brain. Recall before re-deriving.

**New memory filenames:** `<type>-<subject>[-<detail>]` kebab-case, `<type>` ∈ user|feedback|project|reference — slug states category + subject. Leave existing files untouched.

**New plan-doc filenames** (any doc written into `.doc/`): `YYYY-MM-DD-NN-<topic>-<type>.md` — date + 2-digit per-day sequence + kebab topic + trailing type `plan` (implementation) or `design` (spec), e.g. `2026-07-21-01-user-dashboard-redesign-plan.md`. New docs only.

**Continuity.** On resume, read the repo's `.doc/*.md` plans + `handoff.md` first. Keep their Status/Current-position current as work proceeds.
