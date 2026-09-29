# Skillboard

Portable agent setup — skills, hooks, memory index, and the Skillboard dashboard — packaged as one plugin for **Claude Code and Codex CLI** (one repo, both harnesses). Built for continuity across sessions/compaction and for weak-model reliability (collision-free skill descriptions, structural hooks instead of prose rules).

## What's inside

| Component | What it does |
|---|---|
| `skills/handoff` | package a session so a fresh agent resumes cold |
| `skills/persisting-plans` | plans always saved to the repo's `.doc/` |
| `skills/memory-recall` | indexed lookup of past decisions/gotchas across all memory homes |
| `skills/self-learning` | research a technology → generate a new skill (w/ ecosystem check) |
| `skills/skill-evolve` | periodic skill audit: cheap local usage baseline first (`scripts/skill_usage.py`), then small-model research agents (trends, version verify) only where it finds candidates → verified verdicts: refresh, absorb, or flag |
| `skills/decision-routes` | evidence-graded options + one recommendation |
| `skills/lazy-code` | the laziest solution that works — YAGNI ladder, debt markers, one runnable check |
| `skills/dev-docs` | regenerate a repo's living docs in one pass |
| `skills/database-design-doc` | database-design.md with Mermaid ER diagrams (Laravel/Rails, degrades elsewhere) |
| `skills/skillboard-init` | **START HERE** — idempotent machine bootstrap (incl. optional Codex registration) |
| `hooks/hooks.json` | continuity pointers at session start, plan preservation around compaction, weekly memory-maintenance nag, memory-index refresh, stale-skill freshness nag, `.doc/` naming guard on Write, optional rtk/code-review-graph integration (silent when tools absent). The dashboard is **not** on any hook — run `skillboard` when you want it. |
| `hooks/enforce-doc-naming.sh` | blocks a `.doc/*.md` write whose name breaks `YYYY-MM-DD-NN-topic-(plan\|design).md`, telling the agent the right name (catches plan-mode's random slug before it lands) |
| `scripts/memory-index.py` | disposable FTS5 index over memory files (files stay the only truth) |
| `scripts/setup-dashboard.py` | the Skillboard dashboard → `~/.claude/skillboard.html`; maintenance-log UI (design system in `DESIGN.md`, contract in `.impeccable/`) with per-skill usage pills; built **on demand** (`skillboard`), never on a hook — no session pays for a page it may not open |
| `scripts/skill_usage.py` | counts real skill usage from this machine's session logs (Skill calls + slash commands) — feeds the dashboard pills and skill-evolve's usage baseline |
| `templates/CLAUDE-sections.md` | standard CLAUDE.md sections (Memory Routing + naming conventions, Surgical Changes, …) |
| `AGENTS.md` + `.codex-plugin/` | Codex CLI target: instructions + manual skill index + plugin manifest |

## Install (new machine)

Private repo — any working git auth is enough (SSH key already set up, or HTTPS credentials, or `gh auth login`). No `gh` dependency.

In Claude Code:

```
/plugin marketplace add git@github.com:jemang/skillboard-plugin.git
/plugin install skillboard@skillboard
/skillboard-init
```

Then add to `~/.zshrc`:

```bash
alias skillboard='python3 ~/.claude/scripts/setup-dashboard.py --open'
```

(`~/.claude/scripts/*.py` are 2-line shims installed by init; the real scripts live in the plugin cache and update with the plugin.)

Full component reference + recommended companion plugins with live install-status: open the dashboard → **Setup** tab.

### Codex CLI

`/skillboard-init` step 7 registers the plugin on Codex automatically when the binary is present (`codex plugin marketplace add` + `plugin add`). Codex runs the same sync hooks from `hooks/hooks.json`; the async memory-index/dashboard refresh isn't supported there — run the `skillboard` alias manually. After changing any hook, reinstall on Codex (`codex plugin add skillboard@skillboard --json`) so it re-trusts the hook hashes.

## Design rules (do not break)

- **Files are the only memory truth.** The SQLite index is disposable; deleting `~/.claude/memory-index.db` loses nothing.
- **One fact, one home.** Repo gotchas → repo `project-conventions`; preferences → auto-memory; WIP → `handoff.md`/`.doc`; personal → remember brain.
- **Every hook fails open.** Missing optional tools (rtk, codegraph, code-review-graph, remember) = silent no-op, never a broken session.
- **Skill descriptions are collision-free** — rich triggers plus "NOT for X — use Y" cross-pointers. Don't shorten them for token savings; weak-model routing depends on them.

## Updating

Edit here → bump `version` in BOTH `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` (`tests/test_manifests.py` enforces the match) → push → `claude plugin update skillboard@skillboard` and `codex plugin add skillboard@skillboard --json` on each machine.
