---
name: skillboard-init
description: "Bootstrap or verify the Skillboard setup on this machine — run after installing the skillboard plugin on a NEW machine, or anytime to health-check the install. Triggers: '/skillboard-init', 'set up skillboard', 'bootstrap my agent setup', 'configure skillboard on this machine'. Idempotent: re-running reports 'already configured' per step and fixes only what's missing. NOT for generating repo docs (dev-docs), NOT for the dashboard itself (run the skillboard alias), and NOT for changing the plugin's own code/skills/hooks (skillboard-maintain)."
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
{ "dev_root": "~/development", "brain_dir": "~/remember", "codex_dir": "~/.codex", "repo": "" }
```

**If it already exists, reconcile it** — an older config predates keys the template gained later, and writing-only-when-missing lets that drift forever. Compare its keys against `$ROOT/templates/skillboard.config.json`:

```bash
python3 -c 'import json,os;t=json.load(open("'"$ROOT"'/templates/skillboard.config.json"));c=json.load(open(os.path.expanduser("~/.claude/skillboard.json")));m={k:v for k,v in t.items() if k not in c};print(json.dumps(m) if m else "config complete")'
```

All keys present → report `already configured`. Otherwise list each missing key with its default and what it controls, say whether the code already falls back to that same value (most do — then it is cosmetic, not a break), and offer to add them. Never change a key the user already set.

- `dev_root`: where their repos live (continuity + plan scanning).
- `brain_dir`: remember-plugin brain path, `""` if they don't use it.
- `codex_dir`: Codex CLI home (its native memories get indexed too), `""` if no Codex.
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

Show the Recommended list with install commands (same list as the dashboard Setup tab): superpowers, caveman, remember, security-guidance, context7, frontend-design + CLI tools rtk/codegraph. Let the user pick.

### 7. Codex bootstrap (optional)

Register the plugin on Codex CLI too, if present. Fail-open: no Codex → report `skipped: Codex not installed`, continue.

1. Detect the binary: `command -v codex`, else `/Applications/ChatGPT.app/Contents/Resources/codex` (macOS ChatGPT app). Call it `$CODEX`.
2. `"$CODEX" plugin list` → `skillboard@skillboard` already `installed, enabled` at the current version → report `already configured`, done.
3. Else (ask first): `"$CODEX" plugin marketplace add "$ROOT" --json` (if the marketplace is missing) → `"$CODEX" plugin add skillboard@skillboard --json`.
4. Verify: `"$CODEX" doctor` → 0 fail (ignore network/reachability warns); optionally a bounded `"$CODEX" exec "Reply only: OK"`.

Notes: Codex reads the same `hooks/hooks.json` (sync hooks run; the async memory-index hook is skipped — run `python3 ~/.claude/scripts/memory-index.py` manually on Codex to refresh recall). The dashboard is on-demand on both harnesses (`skillboard`), so nothing about it differs on Codex. Reinstalling via `plugin add` is also the fix whenever hooks change and Codex distrusts them (`authPolicy: ON_INSTALL` re-pins the hashes). Codex ≥0.148 may support async hooks (unverified as of 2026-08-27; local was 0.144.2) — after a Codex upgrade, re-test whether the async hook runs; ≥0.149 retires the `untrusted` approval policy.

### 8. First run + finish

```bash
python3 ~/.claude/scripts/memory-index.py        # builds ~/.claude/memory-index.db
python3 ~/.claude/scripts/setup-dashboard.py     # writes ~/.claude/skillboard.html
```

Print the alias line for `~/.zshrc`:

```bash
alias skillboard='python3 ~/.claude/scripts/setup-dashboard.py --open'
```

Report: per-step status table (configured / skipped / changed), then point at dashboard → Setup tab for the full component reference.
