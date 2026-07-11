---
name: skillboard-init
description: "Bootstrap or verify the Skillboard setup on this machine — run after installing the skillboard plugin on a NEW machine, or anytime to health-check the install. Triggers: '/skillboard-init', 'set up skillboard', 'bootstrap my agent setup', 'configure skillboard on this machine'. Idempotent: re-running reports 'already configured' per step and fixes only what's missing. NOT for generating repo docs (dev-docs) and NOT for the dashboard itself (run the dash alias)."
---

# Skillboard Init — bootstrap a machine

Idempotent bootstrap. Every step: check current state FIRST, report `already configured` and skip if satisfied, otherwise ask before changing. Never overwrite user content without asking. All settings edits: back up `~/.claude/settings.json` to `~/.claude/settings.json.bak-skillboard` once before the first change.

The plugin root for this install (call it `$ROOT`): the directory two levels above this skill file (this file lives at `$ROOT/skills/skillboard-init/SKILL.md`).

## Steps

### 1. Dependency check — report a table

Required: `python3` (3.9+), `jq`. Optional (features degrade silently without them): `rtk` (bash-output compression), `codegraph` + `code-review-graph` (code intelligence), `gh` (private-repo plugin updates).
`command -v` each; report table: dep | found | what it unlocks. Missing REQUIRED → stop, tell user install command (brew).

### 2. Config file `~/.claude/skillboard.json`

If missing, ask the user for values then write (defaults shown):

```json
{ "dev_root": "~/development", "brain_dir": "~/remember", "corpus_trigger": 50, "repo": "" }
```

- `dev_root`: where their repos live (continuity + plan scanning).
- `brain_dir`: remember-plugin brain path, `""` if they don't use it.
- `repo`: `owner/repo` GitHub path (e.g. `jemang/skillboard-plugin`) — powers dashboard copy-link cards; `""` disables the links.

### 3. Script shims at `~/.claude/scripts/`

The plugin owns the real scripts at `$ROOT/scripts/`. Stable local paths (used by the `skillboard` alias and the memory-recall skill) are 2-line shims. For each of `memory-index.py`, `setup-dashboard.py`: if `~/.claude/scripts/<name>` is missing OR is not a shim (no `SKILLBOARD-SHIM` marker), write:

```python
#!/usr/bin/env python3
# SKILLBOARD-SHIM — real script lives in the skillboard plugin cache
import glob, os, re, runpy, sys
c = max(glob.glob(os.path.expanduser("~/.claude/plugins/cache/skillboard/skillboard/*/scripts/SCRIPTNAME")), key=lambda p: [int(x) for x in re.findall(r"\d+", p.split(os.sep)[-3])])
sys.argv[0] = c; runpy.run_path(c, run_name="__main__")
```

(replace `SCRIPTNAME`). If an old full copy exists, ask before replacing.

### 4. settings.json keys (ask per item, jq merge)

- `plansDirectory: ".doc"` — plan-mode files auto-save into each repo.
- `includeGitInstructions: false` — ~2K tokens/session off; only if the user commits manually.
After edits: `jq -e . ~/.claude/settings.json` must parse.

### 5. CLAUDE.md sections

`$ROOT/templates/CLAUDE-sections.md` holds the standard sections (Memory Routing, Surgical Changes, Task Completion Report Format, Subagent Model Routing, Skill Creation Nudge). For each `## section` missing from `~/.claude/CLAUDE.md`: offer to append. Never modify existing sections.

### 6. Companion plugins (offer, never auto-install)

Show the Recommended list with install commands (same list as the dashboard Setup tab): superpowers, caveman, remember, token-optimizer, security-guidance, context7, frontend-design + CLI tools rtk/codegraph. Let the user pick.

### 7. First run + finish

```bash
python3 ~/.claude/scripts/memory-index.py        # builds ~/.claude/memory-index.db
python3 ~/.claude/scripts/setup-dashboard.py     # writes ~/.claude/skillboard.html
```

Print the alias line for `~/.zshrc`:

```bash
alias skillboard='python3 ~/.claude/scripts/setup-dashboard.py --open'
```

Report: per-step status table (configured / skipped / changed), then point at dashboard → Setup tab for the full component reference.
