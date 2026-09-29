---
name: skill-evolve
description: "Use when the installed skill set should be audited against what's current — user says '/skill-evolve', 'update my skills', 'are my skills outdated', 'check trending skills', 'evolve the skillboard', 'audit skills for staleness', 'suggest skills from my habits', 'what skills fit how I work', a 'STALE TECH SKILLS' session-start nag appeared, or months passed since the last skill audit. Works on Claude Code and Codex. NOT for learning ONE new technology into a skill (self-learning), NOT for evaluating ONE specific third-party plugin/repo (setup-advisor, if installed), NOT for editing the skillboard plugin's own code/hooks/dashboard (skillboard-maintain, if installed)."
---

# Skill Evolve — audit and refresh the installed skill set

Orchestrator workflow: small-model research agents gather facts, YOU verify and decide. Run the cheap usage pass (step 0) quarterly; run the full research lanes only when that pass surfaces a low/never-used candidate, a tech-pinned skill passes 90 days since its research stamp, or a material platform change occurred. The SessionStart nag fires on both stale stamps and an overdue audit (>90 days since the last one).

## 0. Usage baseline — cheap, local, run BEFORE any research

Run the plugin's usage scanner (newest plugin cache, or the repo checkout): `python3 <skillboard>/scripts/skill_usage.py` — on each machine you can reach (ssh + run remotely for the others). It reads only that machine's `~/.claude/projects/*/*.jsonl` (Skill calls + typed slash commands, plugin prefixes stripped; Codex sessions are NOT counted), so note which hosts you covered. Join `usage` entries to the inventory by skill basename; absent = never used.

Classify before researching: healthy/recent use → keep, no trends lane needed; zero/low use or last use >2 quarters ago → inspect prompt + overlap (candidate for step 4/6); tech-pinned → version-verify lane. Low use is evidence for review, never automatic deletion — some skills are knowledge/discipline skills applied without invocation.

Also read `~/.claude/memory-recall-misses.log` (failed memory searches, one `timestamp\tquery` line each). 2+ genuine misses of the same kind unlock building the matching deferred index improvement — bad ranking → bm25 column weighting; partial-word queries → last-term prefix matching; vague/synonym phrasings whose note existed → semantic lane (sqlite-vec + embeddings, needs non-system python). Junk/test queries don't count, and one-off misses stay logged, not built for.

## 1. Inventory

Scan every skill home: plugin skills (newest plugin cache `skills/` dir), `~/.claude/skills/`, `<repo>/.claude/skills/`, on Codex also `~/.codex/skills/`. For each collect: description, `Researched YYYY-MM-DD` / `re-verified` stamp, pinned versions and curated library lists. Split evergreen workflow skills (no pins — rarely stale) from tech-pinned skills (versions, curated lists — the staleness surface).

## 2. Research (small-model agents)

Dispatch cheap research agents in parallel (Claude Code: Agent tool, `general-purpose`, a small model like haiku; Codex or no Agent tool: run the same lanes yourself inline with web search). Facts only — no recommendations; judgment stays with the orchestrator. Three lanes:

- **Trends** — rising/declining tech per current surveys (Stack Overflow, State of JS, Thoughtworks Radar) and agent-framework/protocol shifts.
- **Ecosystem** — trending Claude/Codex skills and collections on GitHub; new platform capabilities (skills spec, hooks, subagents) since the last audit. Known-good starting sources from past audits (verify still live): `github.com/linny006/trending-claude-skills`, `agentskills.io`.
- **Version verify** — for EVERY pinned tech: current stable version, last release date, deprecations/renames/successors (npm / PyPI / GitHub releases).
- **Habits** — mine the user's OWN conversation history for recurring workflows and corrections. Prefer distilled sources first (memory/evidence logs, Codex `~/.codex/rollout_summaries/`, `~/.codex/memories/`), else sample recent local transcripts (`~/.claude/projects/<project>/*.jsonl`). Local analysis only — transcript content never leaves the machine; the lane reports patterns ("user always X after Y", "user corrected Z three times"), never verbatim content.

Prompts must be self-contained: today's date, strict output format, "mark uncertain claims (unverified)", a word cap.

## 3. Verify before acting

Small-model reports inflate star counts and invent repos. Before any verdict: `curl` the repo (expect HTTP 200), `npm view` / PyPI-check the package, and read the actual source of anything you might absorb. A claim isn't true until observed.

## 4. Verdicts — absorb, don't install

For each finding, stop at the first rung that holds:

1. Already covered by an existing skill/tool → **skip** (note why).
2. Carries 1–2 genuinely new ideas → **absorb** them into the existing skill as a sentence or step.
3. Majority valuable AND non-overlapping → **install/create** — collision-grep all skill descriptions first; add "NOT for X — use Y" cross-pointers both directions.
4. Stale pin → **refresh**: update the `Researched`/re-verified stamp and versions; keep edits surgical.
5. Dead upstream, retired project, or superseded skill → **flag for removal**.

Changes to plugin-shipped skills go through the skillboard-maintain skill (edit repo → bump → update) — never the plugin cache.

## 5. Habit → skill proposals

A habit qualifies as skill material when it recurs across 2+ separate sessions, is genuinely good practice (not a workaround for a fixable problem), and no existing skill covers it. Then SUGGEST, don't create: show the drafted SKILL.md and write it only on user approval; one suggestion per habit, drop silently if declined. If a habit-born skill already exists and a new good habit fits it, fold it in as a step (absorb, rung 2) — habit skills improve run over run. Never copy transcript content into a skill: patterns and steps only, no secrets, no PII, no verbatim conversation. (The in-session variant of this is the Skill Creation Nudge, if configured in CLAUDE.md — this step is the retrospective sweep across history.)

## 6. Removals need the user

Never delete a skill on your own verdict. Present flagged skills with evidence (dead upstream, project retired, trigger collision) and delete only on explicit confirmation.

## 7. Record + refresh

Write or update a plan doc in the repo's `.doc/` (`YYYY-MM-DD-NN-<topic>-plan.md`) with research summary, verdict table, and tasks. Mark the audit done so the overdue nag resets: `touch ~/.claude/skillboard-audit-stamp` (the dashboard reads its mtime). Rerun the dashboard (`skillboard` alias) so freshness badges and usage pills pick up new stamps. Report per file: changed, skipped (why), awaiting confirmation.

## Common mistakes

| Mistake | Fix |
|---|---|
| Trusting agent star counts / repo names | Verify existence + read source first |
| Installing a trending bundle wholesale | Absorb the 1–2 new ideas into existing skills |
| Deleting "old" skills unprompted | Flag with evidence; user confirms |
| Editing plugin cache files | Repo → bump → update (skillboard-maintain) |
| "Refreshing" a curated list by swapping picks | Add maintenance notes; picks change only on user request |
| Auto-creating a skill from a one-off behavior | 2+ recurrences + show draft + user approval first |
| Transcript content pasted into a habit skill | Patterns and steps only — no secrets, PII, or verbatim conversation |
