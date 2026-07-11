## Surgical Changes

When editing existing code, every changed line must trace directly to the current request:

- Don't "improve", refactor, or reformat adjacent code — match existing conventions even where you'd differ. Exception: never replicate a genuinely harmful pattern (security, data loss) for consistency — flag it instead.
- Unrelated dead code or improvement opportunities: mention them, never act unasked.
- Orphans YOUR change created (now-unused imports/vars/functions): remove them.
- If multiple interpretations of the request exist, state them before picking; if a simpler approach exists, say so.

## Task Completion Report Format

When finishing a task (or a task/todo milestone within a larger plan), end the final message with this structure:

1. **Status line first** (bold): what completed + hard evidence, e.g. `**T4 complete — stopping for review. Suite 82 passed (+6). P0 gap closed: KB retrieval now actually runs (was d.retrieve = None).**`
2. **File/Change table**: one row per touched file (or file group like "Tests"). File column = clickable link to the file. Change column = dense summary of what changed there — key function/param names in backticks, behavior notes (fail-open/fail-closed, defaults, scoping), counts for tests (e.g. `+6: ...`).
3. **Verification notes** (prose, after table): what was checked live/manually, what remains unverified, and any follow-up work that is out of scope for this task.
4. **Next step line**: short pointer, e.g. `Check + commit → continue = T5 (...)`.

Rules: table cells stay dense but concrete (real symbol names, not vague "updated logic"). Skip the table only for trivial single-file changes — then the status line + one sentence suffices. This format applies in every repo.

## Subagent Model Routing

When spawning Explore for bulk mechanical searches (multi-file sweeps, log scans, caller enumeration), pass `model: haiku`. Mechanical-locate only — main model reads/interprets the findings itself. Never route judgment tasks (bug hunting, flow summaries, relevance ranking) to cheaper models.

## Memory Routing — one fact, one home

When saving any fact worth remembering, route by type — never write the same fact to two homes:

- **Repo-specific gotcha / technical decision** → that repo's `.claude/skills/project-conventions/SKILL.md` gotchas (append, never delete existing).
- **Cross-repo user preference / workflow feedback** → built-in auto-memory (memory dir + MEMORY.md index line).
- **Work-in-progress state / plans** → `<repo>/handoff.md` + `<repo>/.doc/plan-*.md` (hooks handle reading; keep them updated).
- **Personal knowledge (people, beliefs, non-dev)** → remember brain (`remember this: ...`).
- Recall beats re-derivation: before exploring for a fact, check MEMORY.md, the repo's conventions gotchas, and `.doc/`/`handoff.md` first.
- **Self-capture:** when a session uncovers a hard-won fact — a root cause that took real digging, a non-obvious constraint, an approach that failed and why — save it to its home per the rules above immediately, without waiting to be asked. Bar: would rediscovering this cost another session real effort? If yes, save; routine facts, no.

## Skill Creation Nudge

If I request the same multi-step workflow a 2nd+ time (this session or recalled from memory), suggest freezing it as a skill in `~/.claude/skills/<name>/SKILL.md` — show the proposed SKILL.md before writing. One suggestion per workflow, drop silently if declined. If an existing skill's steps fail against reality, propose fixing the skill in the same turn. If a documented rule keeps getting ignored across sessions, propose structural enforcement (hook, checklist, forced step) instead of rewording it louder.
