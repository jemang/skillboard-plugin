---
name: lazy-code
description: Use BEFORE writing, adding, refactoring, or fixing code, and before adding a library or dependency — forces the laziest solution that actually works (YAGNI, reuse before writing, stdlib and native before custom, one line before fifty). Triggers on "be lazy", "lazy mode", "simplest solution", "minimal solution", "shortest path", "do less", "yagni", and whenever a change risks over-engineering, boilerplate, a speculative abstraction, or a needless dependency. The "ladder" is the standing coding discipline that pairs with CLAUDE.md's Surgical Changes rule. NOT for cleaning up or reviewing code already written (that is /simplify). NOT for choosing between viable tech/product routes (that is decision-routes). NOT for non-coding requests.
---

# Lazy code — climb the ladder before you write

Lazy means efficient, not careless. The best code is the code never written. This skill runs **after** you understand the problem — read the code the change touches and trace the real flow first — never instead of that.

## The ladder

Before writing new code, stop at the first rung that holds:

1. **Does this need to exist at all?** Speculative need → skip it, say so in one line. (YAGNI)
2. **Already in this codebase?** A helper, util, type, or pattern that already lives here → reuse it. Look before you write — re-implementing what's a few files over is the most common slop.
3. **Stdlib does it?** Use it.
4. **Native platform feature covers it?** `<input type="date">` over a picker lib, CSS over JS, a DB constraint over app code.
5. **Already-installed dependency solves it?** Use it. Never add a new dep for what a few lines can do.
6. **Can it be one line?** One line.
7. **Only then:** the minimum code that works.

Two rungs work → take the higher one and move on. The first lazy solution that works is the right one — once you actually know what the change has to touch. The ladder shortens the solution, never the reading.

## Bug fix = root cause, not symptom

A report names a symptom. Before you edit, grep every caller of the function you're about to touch. One guard in the shared function is a smaller diff than a guard in every caller — and patching only the path the ticket names leaves every sibling caller still broken. Fix it once, where all callers route through.

## Rules

- No unrequested abstractions: no interface with one implementation, no factory for one product, no config for a value that never changes.
- No boilerplate or scaffolding "for later" — later can scaffold for itself.
- Deletion over addition. Boring over clever — clever is what someone decodes at 3am.
- Fewest files, shortest working diff — but only once you understand the problem. The smallest change in the wrong place isn't lazy, it's a second bug.
- Complex request? Ship the lazy version and question it in the same response: "Did X; Y covers it. Need full X? Say so." Never stall on an answer you can default.
- Two stdlib options, same size? Take the one correct on edge cases. Lazy means less code, not the flimsier algorithm.

## Mark the corners you cut

Mark a deliberate simplification that has a known ceiling with a `lazy:` comment naming the ceiling and the upgrade path, e.g. `# lazy: global lock, per-account locks if throughput matters`. Grep-able so the debt is tracked, not forgotten.

## Leave one runnable check

Lazy code without its check is unfinished. Non-trivial logic (a branch, loop, parser, or money/security path) leaves ONE runnable check behind — the smallest thing that fails if the logic breaks: an `assert`-based `demo()`/`__main__` self-check or one small `test_*.py`. No frameworks, no fixtures. Trivial one-liners need no test — YAGNI applies to tests too.

## When NOT to be lazy

Never simplify away: understanding the problem, input validation at trust boundaries, error handling that prevents data loss, security measures, accessibility basics, runtime performance on a hot or known-large-input path (never trade an available O(n) for an O(n²) just to save lines — fewer lines is the goal, slower code is not), the readability the next reader needs (minimal means no *unneeded* code, never terse or cryptic code — match the codebase's own naming, idiom, and comment density), or anything the user explicitly asked to keep. Hardware needs the calibration knob a minimal model can't see — a real clock drifts, a real sensor reads off; the platform is never the spec ideal. User insists on the full version → build it, no re-arguing.

## Output

Code first. Then at most three short lines: what was skipped, when to add it. Pattern: `[code] → skipped: [X], add when [Y].` If the explanation is longer than the code, delete the explanation. Explanation the user explicitly asked for (a report, a walkthrough) is not debt — give it in full.
