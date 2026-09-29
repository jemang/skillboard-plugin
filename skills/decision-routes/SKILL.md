---
name: decision-routes
description: Use when the user is weighing options or unsure which direction to take while building software — choosing a tech stack, framework, library, database, architecture pattern, OR a product/feature/MVP direction. Triggers on phrases like "which should I choose", "what approach should I take", "help me decide", "which direction", "is it better to X or Y", "what's the best way to build", "should I use ... or ...", and any moment the user faces a fork between viable build paths. Use it even when the user only describes the problem and hasn't explicitly asked for options — surfacing routes is the point. NOT for a problem whose direction is already chosen — don't manufacture a routes exercise; go execute (lazy-code). Produces 2–3 distinct routes, each with gaps, difficulties, and a research-grounded success rate, then a single recommendation. NOT for forcing the minimal implementation of an already-chosen approach — that is lazy-code.
---

# Decision Routes

Help the user choose a direction when building an application. The deliverable is always the same shape: a small set of genuinely different routes, an honest accounting of what's hard or missing about each, a success-rate estimate grounded in real evidence, and one clear recommendation.

This skill exists because the expensive failures in software aren't bad code — they're committing to the wrong path before seeing the alternatives. The job here is to make the fork visible and the tradeoffs legible so the user commits with eyes open.

## Workflow

### 1. Pin down the decision and the context

Restate the decision in one sentence so the user can confirm you understood it. Then establish the context that actually moves a recommendation:

- **Constraints**: deadline, team size, existing skills, budget.
- **Scale & lifespan**: prototype vs. product, expected users/load, how long it must live.
- **What already exists**: current stack, codebase, infra the choice has to fit into.

If the codebase is relevant and indexed, use codegraph/code-review-graph tools to learn the existing stack rather than asking the user what you can read yourself. If one or two facts are genuinely missing and would flip the answer, ask a targeted question — but don't interrogate. When something is unknown, make a reasonable assumption, **state it explicitly**, and proceed. A useful answer under stated assumptions beats a delayed one.

### 2. Generate 2–3 genuinely distinct routes

The routes must be different *approaches*, not flavors of one approach. "Postgres vs MySQL" is one route (relational SQL); "relational vs document vs managed-BaaS" is three. Aim for the real branches a thoughtful engineer would actually debate. Three is the sweet spot; use two when the space is genuinely binary, four only when the field is wide and the extra option is distinct.

Each route should be something a real team has actually shipped — not a clever idea you invented. If you can't name who builds this way, it's probably not a route.

### 3. Research before you score

This is what makes the success rate mean something. Before assigning a number, ground each route in evidence:

- **WebSearch** for current adoption, maturity, known failure modes, and "X in production" / "migrating off X" post-mortems. The reality of a technology lives in its complaints, not its landing page.
- **context7** (`resolve-library-id` → `query-docs`) for library/framework specifics, version state, and whether the thing is actively maintained.
- Look specifically for **where each route breaks down** — the scale it stops working at, the team size it overwhelms, the lock-in it creates.

Cite what you find. A success rate with no evidence behind it is a guess wearing a number.

### 4. For each route, account for gaps, difficulties, and success rate

- **Gaps**: what's missing, unknown, or unproven for *this* user's situation — capability holes, ecosystem immaturity, things they'd have to build themselves.
- **Difficulties**: the genuinely hard parts — steep learning curve, operational burden, scaling cliffs, migration cost.
- **Success rate**: your estimate of the probability this route leads to a working, maintainable outcome *given the stated context*. See calibration below.

### 5. Recommend one

End with a single pick and the reasoning. State plainly what would change the recommendation — the condition under which a different route wins. A recommendation the user can't stress-test is just an opinion.

## Calibrating the success rate

The number is the probability that a competent team following this route reaches a working, maintainable result under the stated constraints — not "how good is this tech in the abstract." A rock-solid technology used for the wrong context deserves a low number.

Keep the estimates honest and spread out:

- **Anchor on evidence**, not enthusiasm: maturity, adoption at similar scale, documented failure rates, fit to the stated constraints.
- **Don't cluster.** If every route lands at 80–90%, you're not discriminating. Real forks have real spread. A route you're recommending against should look like it.
- **Penalize fit, not just quality.** A great tool that mismatches the timeline or team skills should score low even if it's excellent in isolation.
- **Always show the basis** — one line on what drives each number (e.g. "high adoption at this scale, but team has no Rust experience → learning curve risk").

Treat the percentage as a calibrated judgment, not a measurement. Precision theater (87.3%) is worse than honest rounding (≈65%).

## Output format

Use this structure exactly:

```markdown
## Decision: <one-sentence restatement>

**Context & assumptions:** <constraints used; flag every assumption you made>

## Routes at a glance

| # | Route | Approach in a line | Key gaps | Difficulty | Success rate |
|---|-------|--------------------|----------|------------|--------------|
| A | <name> | <...> | <...> | Low / Med / High | NN% |
| B | <name> | <...> | <...> | Low / Med / High | NN% |
| C | <name> | <...> | <...> | Low / Med / High | NN% |

## Route detail

### A. <name> — NN%
- **What it is:** <approach>
- **Why it fits here:** <tie to the user's actual context>
- **Gaps:** <what's missing/unknown for this situation>
- **Difficulties:** <the genuinely hard parts>
- **Evidence:** <sources, adoption, benchmarks, or post-mortems driving the score>

### B. <name> — NN%
<same structure>

### C. <name> — NN%
<same structure>

## Recommendation

**Pick: <route>.** <2–4 sentences on why, grounded in the user's context.>

**What would change this:** <the condition under which a different route wins.>
```

Drop the table's third route row (and section C) when there are only two routes; add a row/section for a fourth only when it's genuinely distinct.

## Principles

- **Routes must be mutually distinct.** Overlapping options waste the user's decision.
- **Tie everything to the user's context.** A generic comparison they could've googled isn't worth their time; the value is in mapping options onto *their* constraints.
- **Be honest about the route you're not picking.** Steelman it. If a route only looks bad because you described it weakly, the recommendation is untrustworthy.
- **Cite, don't assert.** Especially for the success rate — link the evidence so the user can verify your reasoning.
- **Name what would change your mind.** The most useful part of advice is the boundary where it flips.
