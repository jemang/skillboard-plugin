#!/usr/bin/env python3
"""Count skill usage from local Claude Code session logs (~/.claude/projects/**/*.jsonl).

Counts Skill tool_use calls plus typed slash commands; keys are normalized to
the skill basename (plugin prefix and leading slash stripped). Stdlib only,
fail-open per file. CLI prints JSON; the dashboard imports collect().
"""
import collections
import glob
import json
import os
import re
import sys

BUILTIN = {"model", "clear", "help", "config", "usage", "caveman", "fast",
           "artifacts", "compact", "exit", "login", "logout", "mcp", "plugin",
           "plugins", "skills", "reload-plugins", "reload-skills", "memory",
           "plan", "feedback", "autocompact", "remote-control", "doctor",
           "status", "goal"}
CMD_RE = re.compile(r"<command-name>/?([^<]+)</command-name>")
TS_RE = re.compile(r'"timestamp":\s*"(\d{4}-\d{2}-\d{2})')


def norm(name):
    return name.strip().lstrip("/").split(":")[-1]


def collect(root=None):
    root = root or os.path.expanduser("~/.claude/projects")
    use = collections.defaultdict(lambda: {"n": 0, "last": "", "sessions": set()})
    for f in glob.glob(os.path.join(root, "*", "*.jsonl")):
        sid = os.path.basename(f)
        try:
            with open(f, errors="replace") as fh:
                for line in fh:
                    if '"Skill"' not in line and "<command-name>" not in line:
                        continue
                    m = TS_RE.search(line)
                    ts = m.group(1) if m else ""
                    names = []
                    if '"Skill"' in line:
                        try:
                            content = (json.loads(line).get("message") or {}).get("content")
                        except ValueError:
                            content = None
                        if isinstance(content, list):
                            names += [(blk.get("input") or {}).get("skill", "")
                                      for blk in content
                                      if isinstance(blk, dict)
                                      and blk.get("type") == "tool_use"
                                      and blk.get("name") == "Skill"]
                    names += CMD_RE.findall(line)
                    for raw in names:
                        base = norm(raw)
                        if not base or base in BUILTIN:
                            continue
                        e = use[base]
                        e["n"] += 1
                        e["last"] = max(e["last"], ts)
                        e["sessions"].add(sid)
        except OSError:
            continue
    return {k: {"n": v["n"], "last": v["last"], "sessions": len(v["sessions"])}
            for k, v in use.items()}


if __name__ == "__main__":
    json.dump({"host": os.uname().nodename, "usage": collect()}, sys.stdout, indent=1)
    sys.stdout.write("\n")
