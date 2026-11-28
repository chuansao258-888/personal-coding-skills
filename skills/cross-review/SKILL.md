---
name: cross-review
description: Use when reviewing a plan before implementation or completed work against an approved plan, behaviour contract, engineering standards, or acceptance criteria. Reads the core logic rule by rule, checks architecture, consistency, bugs, drift, test strength, scope, and verification; produces drift-bounded finding contracts and, when it owns acceptance, any required scoped checkpoint commit.
---

# Cross Review

Decide whether a plan is safe to implement, or whether completed work is correct, follows the plan, and is protected by tests. Start from findings; no praise or long summary. If there are none, say so and name the residual risk and remaining manual checks.

Review is read-only. The only allowed mutation is the Phase Checkpoint commit below, when this review owns acceptance.

**Size it.** For a small change, check the diff against its ruling and the targeted tests; skip the full contract machinery. Medium and large changes use everything below.

## Common gates

- **Branch:** start with `git status --short --branch`; review on the task's branch. Never stash, reset, or move unrelated changes.
- **Source of truth:** latest explicit user instruction > approved plan > implementation record > current code > existing tests > general practice. Older text never overrides a newer user decision.
- **Standards:** read `AGENTS.md`, `ENGINEERING_STANDARDS.md` (or equivalent), behaviour contracts, glossary, ADRs, knowledge ledger. Cite violated rule IDs.
- **Orchestrated mode:** when an orchestrator runs the workflow, this review produces findings and per-rule verdicts only; the orchestrator decides acceptance and commits.
- Never push or open a PR unless the user asks.

## Review modes

**Plan Review** (no code yet): can another agent implement this without inventing product or architecture decisions? Check: problem, goals, non-goals, scope, user flow; blocking decisions resolved; Open Questions / Options / TBD in the plan or implementation record are `None` or explicitly non-blocking (otherwise a P1 finding and `REJECT`, clarification required); behaviour contract with rule IDs and a test per rule; testable acceptance IDs; vertical phases with Allowed / Not Allowed / Deferred, tests, verification; production gates that apply; simplicity and style constraints; Architecture Contract per non-trivial phase; reference adaptation matrix and parity decisions when a reference exists; no unapproved endpoints, permissions, migrations, dependencies, or UI scope. Findings name the plan sections to fix, not production code.

**Implementation Review** (code exists): does it satisfy the approved plan and standards with enough evidence? Required fixes stay inside the approved phase; never rewrite documentation to make non-conforming code look compliant.

Run both axes and keep them separate: **Spec** (matches user intent, plan, acceptance) and **Standards** (label `[Standards/Architecture]`, `[Standards/Consistency]`, `[Standards/Simplicity]` when useful). A general preference becomes a finding only when it breaks an approved rule, local convention, or the phase contract.

## Implementation checklist

**Logic first.** For each behaviour-contract rule or acceptance ID: read the core changed functions, trace the runtime path (thread, surface, data flow, second page, restart, error, navigation), compare it with recorded rulings and gates, and give a verdict (implemented as designed / defect with reason). Green tests and screenshots alone do not prove the approach. Watch for:

- ordering applied per page instead of globally; keyset comparators without a unique tiebreak;
- one bad record failing a whole page; a background task disguised as pagination;
- unnormalised cache keys; state reset on mount that defeats a cache; loading shown while local data is ready;
- a change that reverses a recorded ruling or gate; a "fix" that never reproduced the failure;
- shared fixtures edited outside the task; residue of a revert; dead code that would reintroduce rejected behaviour.

**Scope and intent.** Exact phase scope; no narrowing or weakening of the user's capability (also in review-fix diffs); no unrequested endpoints, permissions, migrations, abstractions, or UI.

**Architecture and simplicity.** Conformance evidence matches the diff: one authority per rule, one owner per state, no cycles, cross-module internals, leaked infrastructure models, pass-through layers, speculative abstractions, hidden errors, or ambiguous fallback; every new variable, gate, retry, or fallback has a current need and a test; cleanup complete; file size and layering within repository rules; local style kept; no unrelated churn, secrets, debug code, or private artifacts.

**Contracts across stacks.** API, DTO, event, and database contracts agree between backend, frontend, tests, and docs; flags, budgets, retries, and error paths are wired end to end; logs and traces respect privacy.

**Tests.** Every contract rule has a test and every new test a rule; tests would fail on regression; they assert payloads and order, not just calls; boundary, empty, malformed, disabled, and wrong-session cases where relevant; no failing test loosened, and no test changed without a recorded ruling that superseded the old design; geometry tests measure rendered content, not containers equal by construction.

**UI.** Rendered behaviour checked; headless screenshots of each affected screen at a wide and a narrow width reviewed for alignment, overlap, and duplicate controls (check visibility: hidden kept-alive views make locators ambiguous); console errors checked.

**Records.** Implementation record states real verification and pending manual checks; durable pitfalls added to the knowledge ledger.

When asked whether a phase is done, check each criterion against the current code first; accept with evidence when all are met instead of asking for new code.

## Findings

Read [references/finding-contract.md](references/finding-contract.md) before writing or re-reviewing an actionable finding, and use its exact fields, checklist, closure criteria, confidence, severity, and classification.

A reviewer may specify how to close an evidenced finding inside the approved target, never redesign the feature, change product semantics, weaken acceptance, or invent adjacent work. For each finding, know: which requirement or rule is violated; whether the root cause is confirmed; the narrowest fix; which tempting adjacent changes are out of bounds; which test fails before and passes after. Unapproved adjacent work in the diff is removed, not adopted. Useful extras go under `Future Enhancement`, outside the verdict. If the only plausible fix changes scope, architecture, contracts, dependencies, security posture, phase boundaries, or acceptance, recommend `REJECT` and route to `$feature-planner`.

**Re-review of a fix pass:** reuse the original IDs and closure criteria; mark each item pass/fail with evidence; raise a new drift finding for work outside `Allowed`; state `CLOSED` or `OPEN` explicitly.

## Overall review

```text
Reviewed Target: user goal, plan/phase, branch, diff boundary
Blocking Fixes: IDs and titles, or None
Non-blocking Fixes: IDs and titles, or None
Fix Order: ID — first repair and why (omit when no fixes)
Anti-Drift: fixes stay in target Yes/No; findings adding features/APIs/schemas/dependencies: None | IDs; findings changing boundaries or acceptance: None | IDs
Recommendation: ACCEPT | APPLY-REVIEW-FIX | REJECT — one-sentence reason
Phase Checkpoint: NOT_APPLICABLE | CHECKPOINT_COMMITTED <hash> | CHECKPOINT_BLOCKED <reason>
```

`APPLY-REVIEW-FIX` only when every required finding is repair-ready; `REJECT` when clarification, root-cause work, or a plan change comes first. If accepted, say what was checked and what remains manual; never claim E2E coverage that was not run. Avoid vague repair language ("improve handling", "add more tests").

## Phase checkpoint

Only after an Implementation Review `ACCEPT`, when repository policy requires a commit per phase and this review owns acceptance (not in orchestrated mode). Require: blocking findings `CLOSED`; no blocking Open Question; tests, builds, docs, cleanup, and evidence complete; the task branch; reviewed files isolated from unrelated changes; nothing secret or temporary staged. Stage explicit paths only (never `git add -A` in a mixed worktree), inspect `git diff --cached`, make one focused commit, report the hash, do not push. If isolation fails, report `CHECKPOINT_BLOCKED`; never stash, reset, or bundle unrelated work.

## Handoff

Accepted plan → `$feature-implementer`. Findings → `$apply-review-fix` with exact IDs and specifications. Unresolved decisions → `$feature-planner` or the user. Module walkthrough after acceptance → `$module-introduction`.
