# Skillboard

Portable Claude Code setup — skills, hooks, memory index, and the Skillboard dashboard — packaged as a single plugin.

## Install (new machine)

```bash
gh auth login                                   # private repo — auth first
```

In Claude Code:

```
/plugin marketplace add <user>/skillboard
/plugin install skillboard@skillboard
/skillboard-init
```

Then add to `~/.zshrc`:

```bash
alias dash='python3 "$(ls -d ~/.claude/plugins/cache/skillboard/skillboard/*/scripts | head -1)/setup-dashboard.py" --open'
```

Full component reference: open the dashboard → **Setup** tab.
(README expanded in Task 6.)
