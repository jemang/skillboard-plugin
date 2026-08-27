---
name: self-learning
description: "Autonomous skill generator that learns new technologies from the web. Use when users want to learn about a new library/framework/tool, need to create a skill for an unfamiliar technology, want to research and document a technology's usage patterns, or invoke with `/learn <topic>`. NOT for auditing or refreshing the EXISTING skill set against trends/staleness — that is skill-evolve."
---

# Self-Learning Skill Generator

Autonomously research and learn new technologies from the web, then generate a reusable skill.

## Usage

```
/learn <topic>
```

### 1. Parse the topic

If `<topic>` is missing, show usage. If topic is ambiguous, ask to clarify:

- "react" → "React for web, React Native, or a specific library like react-query?"
- "apollo" → "Apollo GraphQL client, Apollo Server, or Apollo Federation?"
- "aws" → "Which AWS service? (S3, Lambda, DynamoDB, etc.)"

Normalize to **kebab-case** for filenames.

### 2. Ecosystem Check (before building)

Before researching from scratch, check whether a reputable skill already exists:

```bash
npx -y skills find <topic>        # searches skills.sh ecosystem
```

If a match exists from a reputable source (1K+ installs, known org like vercel-labs/anthropics), offer it to the user instead of building: show name, install count, and `npx skills add <owner/repo> --skill <name>`. If they accept, still run the step-6 collision check on the installed skill's description. If no reputable match (or `npx` unavailable/offline), continue to step 3.

### 3. Discover Sources (Web Search)

Use web search tool to find authoritative documentation:

**Search queries to try:**
1. `<topic> official documentation`
2. `<topic> getting started guide`
3. `<topic> API reference`
4. `<topic> GitHub repository`

**Source prioritization:**
1. Official docs sites (e.g., docs.*, *.dev)
2. Official GitHub repositories (README, /docs)
3. Official blogs/announcements

Select **3–5 high-quality URLs** maximum.

If no credible sources found, ask user to provide a URL.

---

### 4. Extract Content (URL Reading)

For each selected URL, read the content:

**Extract only relevant sections:**
- Installation / setup
- Core concepts
- API reference / key functions
- Common patterns / examples
- Version information

**Skip irrelevant content:**
- Navigation, ads, login prompts
- Unrelated sidebar content
- Comments, forums

If reading the content fails (JavaScript-heavy sites), fall back to browser agent:

```
Task: Navigate to <URL> and extract the main content including:
- Installation instructions
- Core concepts and API reference
- Code examples
Return the extracted content as markdown.
```

Record scrape timestamp for each source (use current date: YYYY-MM-DD format).

---

### 5. Generate Skill

Skills are modular, self-contained packages. Every skill consists of a required `SKILL.md` file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

1. Read `references/skill_creation_guide.md` to understand the format and principles.
2. Synthesize the learned and extracted information into a new skill.
    - **Trigger:** Write a description that clearly defines when to use it.
    - **Workflow:** Create step-by-step instructions.
    - **Format:** Ensure valid YAML frontmatter and proper file structure.
    - **Freshness stamp (required):** the skill body's opening states `Researched YYYY-MM-DD` plus the exact versions verified (e.g. `langgraph 1.2.6`), and the description names the covered major lines (e.g. "Covers langgraph 1.x"). The skillboard dashboard reads this date to flag stale skills — a tech skill without a stamp can't be audited.

### 6. Save the Skill

Two locations:

- `~/.claude/skills/<skill-folder>/` — Global (all projects)
- `<repo>/.claude/skills/<skill-folder>/` — Project-specific (committed with the repo)

**Always ASK the user where to save — with a recommendation, not a blind question:**

1. Detect: is the topic a dependency of the current repo? (grep manifests — package.json, pyproject.toml, composer.json, go.mod, Cargo.toml)
2. Recommend **project** if it's a repo dependency or version-pinned to this repo's stack; recommend **global** if it's general tooling used across projects.
3. Ask via one question: "Save as [recommended] skill? (project = travels with repo, global = all projects)"

**Never mix scopes in one file:** general API knowledge and project-specific decisions are different lifetimes. If research surfaced project-specific notes (this repo's design decisions, pinned quirks), put the skill wherever chosen but move project-only notes into `<repo>/.claude/skills/project-conventions/SKILL.md` gotchas instead.

**Before saving, collision check:** read the description lines of every existing skill in BOTH locations (`grep -h "^description:" ~/.claude/skills/*/SKILL.md <repo>/.claude/skills/*/SKILL.md`). If the new skill's triggers overlap an existing skill's, either narrow the new description and add a "NOT for X — use Y" cross-pointer to both, or merge into the existing skill. Two skills answering the same trigger = weak models pick wrong.

**Size cap:** SKILL.md body ≤ ~150 lines; overflow goes to `references/*.md` files loaded on demand.

Create directory if it doesn't exist, warn user before overwriting existing skill.

---

### 7. Confirm to User

Report:
```
✓ Created skill: <topic>
  Sources scraped: <N>
  Saved to: <the chosen path — ~/.claude/skills/<topic>/SKILL.md or <repo>/.claude/skills/<topic>/SKILL.md>
  This skill will auto-trigger when working with <topic>.
```

---

## Tool Reference

- `WebSearch`: Discover documentation URLs
- `WebFetch`: Extract content from static pages — always try FIRST (cheap, distilled)
- `defuddle parse <url> --md` via Bash: FALLBACK ONLY, when WebFetch returns thin/incomplete extracts (missing code examples, "content does not include" answers). Full-fidelity markdown, but dumps whole page into context — never first choice.
- Browser MCP tools (`browser_*`): Extract content from JavaScript-heavy sites (defuddle is static-HTML only)
- `Write`: Save the generated skill

## Critical Rules

1. **Never hallucinate documentation:** Only include information from scraped sources.
2. **Never invent APIs:** If documentation is unclear, ask the user what to do.
3. **Ask for URLs:** If automated discovery fails, ask user for specific URLs.
4. **Verify sources:** Prefer official sources over third-party tutorials.
