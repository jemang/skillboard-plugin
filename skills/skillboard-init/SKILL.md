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

If missing, **detect first, then confirm** — propose detected values in one question instead of asking cold (never write silently; the user can override any of them). Defaults shown:

```json
{ "dev_root": "~/development", "brain_dir": "~/remember", "codex_dir": "~/.codex", "repo": "" }
```

**If it already exists, reconcile it** — an older config predates keys the template gained later, and writing-only-when-missing lets that drift forever. Compare its keys against `$ROOT/templates/skillboard.config.json`:

```bash
python3 -c 'import json,os;t=json.load(open("'"$ROOT"'/templates/skillboard.config.json"));c=json.load(open(os.path.expanduser("~/.claude/skillboard.json")));m={k:v for k,v in t.items() if k not in c};print(json.dumps(m) if m else "config complete")'
```

All keys present → report `already configured`. Otherwise list each missing key with its default and what it controls, say whether the code already falls back to that same value (most do — then it is cosmetic, not a break), and offer to add them. Never change a key the user already set.

- `dev_root`: where their repos live (continuity + plan scanning). Detect: among `~/development ~/dev ~/code ~/Projects ~/src ~/repos`, propose the existing dir containing the most `*/.git` entries; none found → ask.
- `brain_dir`: remember-plugin brain path, `""` if they don't use it. Detect: remember plugin in `claude plugin list` or `~/remember/` exists → propose `~/remember`; else `~/.claude-mem/memory/` exists → propose that (claude-mem markdown logs); neither → propose `""`.
- `codex_dir`: Codex CLI home (its native memories get indexed too), `""` if no Codex. Detect: `~/.codex/` exists or a codex binary resolves → propose `~/.codex`; else `""`.
- `repo`: `owner/repo` GitHub path — powers dashboard copy-link cards; `""` disables the links. Detect: parse the skillboard marketplace's git remote (`claude plugin marketplace list`, or `git -C <marketplace source> remote get-url origin` when it is a local clone) into `owner/repo`; unparseable → `""`.
- `external_memory`: free-text naming an external memory store this setup has, used by memory-recall's no-match fallback and the search hint; `""` = none. **Detect before asking:** `~/.claude-mem/` exists → propose "claude-mem MCP — search / get_observations" (and offer pointing `brain_dir` at `~/.claude-mem/memory` to index its markdown logs); a Basic Memory MCP is configured (`claude mcp list` or `search_notes` tool present) → propose "Basic Memory MCP — search_notes". Confirm the proposal with the user, never write it silently; nothing detected → default `""`.

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

Notes: Codex reads the same `hooks/hooks.json` (sync hooks run; the async memory-index hook is skipped — run `python3 ~/.claude/scripts/memory-index.py` manually on Codex to refresh recall). The dashboard is on-demand on both harnesses (`skillboard`), so nothing about it differs on Codex. Reinstalling via `plugin add` is also the fix whenever hooks change and Codex distrusts them (`authPolicy: ON_INSTALL` re-pins the hashes). After any Codex upgrade: rerun `plugin add`, `doctor`, and a bounded `exec` check to verify hook behavior and trust handling on the installed version — don't assume version thresholds noted in past audits still apply (re-test rather than trust a stale note; last verified 2026-09-29 on Codex 0.157: sync hooks run, async memory-index hook still skipped — evidence: `~/.claude/memory-index.db` mtime unchanged across a Codex session).

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

Note: a SessionStart hook nags when setup is incomplete (config/keys/shims missing) and self-silences once init completes. A user who wants the nag gone WITHOUT completing setup mutes it: `touch ~/.claude/skillboard-init-mute` (delete the file to re-enable).
