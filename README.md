# Skillboard

Portable Claude Code setup — skills, hooks, memory index, and the Skillboard dashboard — packaged as one plugin. Built for continuity across sessions/compaction and for weak-model reliability (collision-free skill descriptions, structural hooks instead of prose rules).

## What's inside

| Component | What it does |
|---|---|
| `skills/handoff` | package a session so a fresh agent resumes cold |
| `skills/persisting-plans` | plans always saved to the repo's `.doc/` |
| `skills/memory-recall` | indexed lookup of past decisions/gotchas across all memory homes |
| `skills/self-learning` | research a technology → generate a new skill (w/ ecosystem check) |
| `skills/decision-routes` | evidence-graded options + one recommendation |
| `skills/dev-docs` | regenerate a repo's living docs in one pass |
| `skills/skillboard-init` | **START HERE** — idempotent machine bootstrap |
| `hooks/hooks.json` | continuity pointers at session start, plan preservation around compaction, weekly memory-maintenance nag, memory-index + dashboard auto-refresh, optional rtk/code-review-graph integration (silent when tools absent) |
| `scripts/memory-index.py` | disposable FTS5 index over memory files (files stay the only truth) |
| `scripts/setup-dashboard.py` | the Skillboard dashboard → `~/.claude/skillboard.html` |
| `templates/CLAUDE-sections.md` | standard CLAUDE.md sections (Memory Routing, Surgical Changes, …) |

## Install (new machine)

```bash
gh auth login        # private repo — auth first
```

In Claude Code:

```
/plugin marketplace add <user>/skillboard
/plugin install skillboard@skillboard
/skillboard-init
```

Then add to `~/.zshrc`:

```bash
alias skillboard='python3 ~/.claude/scripts/setup-dashboard.py --open'
```

(`~/.claude/scripts/*.py` are 2-line shims installed by init; the real scripts live in the plugin cache and update with the plugin.)

Full component reference + recommended companion plugins with live install-status: open the dashboard → **Setup** tab.

## Design rules (do not break)

- **Files are the only memory truth.** The SQLite index is disposable; deleting `~/.claude/memory-index.db` loses nothing.
- **One fact, one home.** Repo gotchas → repo `project-conventions`; preferences → auto-memory; WIP → `handoff.md`/`.doc`; personal → remember brain.
- **Every hook fails open.** Missing optional tools (rtk, codegraph, code-review-graph, remember) = silent no-op, never a broken session.
- **Skill descriptions are collision-free** — rich triggers plus "NOT for X — use Y" cross-pointers. Don't shorten them for token savings; weak-model routing depends on them.

## Updating

Edit here → bump `version` in `.claude-plugin/plugin.json` → push → `/plugin update skillboard` on each machine.
