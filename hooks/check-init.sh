#!/bin/bash
# SessionStart nag: setup incomplete -> suggest /skillboard-init. Fail-open,
# silent when complete, muted by ~/.claude/skillboard-init-mute.
[ -f "$HOME/.claude/skillboard-init-mute" ] && exit 0

MSG=""
CFG="$HOME/.claude/skillboard.json"
TPL="${CLAUDE_PLUGIN_ROOT}/templates/skillboard.config.json"

if [ ! -f "$CFG" ]; then
  MSG="config missing"
elif [ -f "$TPL" ] && command -v python3 >/dev/null 2>&1; then
  MSG=$(python3 -c "
import json,sys
try:
    t=json.load(open('$TPL')); c=json.load(open('$CFG'))
    m=[k for k in t if k not in c]
    print('config keys missing: '+', '.join(m) if m else '')
except Exception: pass" 2>/dev/null)
fi

if [ -z "$MSG" ] && [ ! -f "$HOME/.claude/scripts/setup-dashboard.py" ]; then
  MSG="script shims missing"
fi

[ -n "$MSG" ] && echo "SKILLBOARD SETUP INCOMPLETE ($MSG) — suggest /skillboard-init to the user; to silence this: touch ~/.claude/skillboard-init-mute"
exit 0
