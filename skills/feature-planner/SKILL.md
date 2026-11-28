---
name: feature-planner
description: Use when turning a new, unclear, cross-module, risky, reference-based, or product-facing request into a cross-review-ready implementation plan. Defines behaviour contracts with stable rule IDs, acceptance IDs, Architecture Contracts, Allowed/Not Allowed/Deferred phase boundaries, tests, verification, and checkpoint gates before coding.
---

# Feature Planner

Turn a rough request into a plan another agent can implement without inventing product or architecture decisions. Plan only; do not implement unless the user explicitly asks.

**Size it.** Small changes (one-line or behaviour-neutral edits, tests aligned to a recorded ruling) need no plan. Medium changes need a ruling plus the affected behaviour-contract rules. Large changes (new module, cross-module, risky, reference-based) get the full plan below.

## Common gates

- **Branch:** start with `git status --short --branch`. Plan, implementation, fix, and re-review of one task share one branch (repository convention, else `feat/<task-slug>`). Switch or create only from a clean worktree; never stash, reset, or carry unrelated changes — use a separate worktree or ask.
- **Source of truth:** latest explicit user instruction > approved plan > implementation record > current code > reference behaviour > general practice.
- **Intent:** never resolve a concern by dropping, deferring, narrowing, or weakening a requested capability without the user's approval. Keep phase and acceptance IDs stable once review starts.
- **Standards:** read `AGENTS.md`, `ENGINEERING_STANDARDS.md` (or equivalent), glossary/context files, ADRs, and the project knowledge ledger. Cite their rule IDs.
- **Orchestrated mode:** when an orchestrator dispatched this task, it owns rulings and acceptance; report decisions and gaps to it instead of choosing.
- Never push or open a PR unless the user asks. Never quote secret values from local configuration.

## Clarification gate

Ask before finalizing when any of these is unclear and material: the user problem and flow; scope, non-goals, deferred work; acceptance or manual checks; API, data, migration, or retention; auth, privacy, security; async, streaming, or event contracts; new dependencies or external services; configuration and defaults; how closely to follow a reference; rollback or compatibility.

Return blocking questions with options and a recommendation. Never present `Option A / B`, `TBD`, or a recommended-but-unconfirmed choice as implementation-ready, and never let the implementer pick.

## Workflow

1. Understand the goal, user problem, scope, success and failure behaviour.
2. Pass the common gates; inspect the current code and its authoritative implementation before naming files.
3. Inspect any reference separately; separate reusable ideas from incompatible assumptions.
4. Write the behaviour contract, acceptance IDs, Architecture Contract, and phases.
5. Write or update the plan and implementation documents; hand off to review.

## What the plan must contain

Include each item that applies; omit the rest.

- **Summary and decisions:** product summary, goals and non-goals, user flow, confirmed decision ledger (dated), assumptions.
- **Current findings:** what the code does today, glossary/ADR impact.
- **Behaviour contract** (per touched module): structure (owners, files, module layout within the repository's size and layering rules); numbered MUST rules with stable IDs; the test that proves each rule. A rule without a test, or a test without a rule, is a gap.
- **Reference parity:** with a reference implementation, a rule-by-rule comparison and the adaptation matrix below. When the user wants parity, conflicts resolve to the reference's observed behaviour; rank evidence live observation > reference static analysis > third-party code > legacy code, and record each decision with its evidence in one place (contract or interface spec).
- **Stable acceptance IDs** (`AC-001`) for success, failure, boundary, permission, privacy, persistence, API, and UI behaviour.
- **Production gates:** API request/response/errors and compatibility; configuration names, defaults, secret boundaries; data migration, backfill, rollback; security, privacy, and what must never be logged; release flags and fallback; observability.
- **Background work, caching, performance:** event- or user-triggered refresh, long intervals, stop when idle (justify any faster cadence); start from the reference's caching strategy; name measurements, the baseline taken before the change, and a per-rule status (planned / implemented / verified-live).
- **Simplicity and style:** patterns to reuse, abstractions and refactors to avoid. Plan no new variable, gate, threshold, retry, fallback, or compatibility branch without a current requirement, a real consumer, and verification.
- **Architecture Contract** (below) for every non-trivial phase.
- **Phases** (below), test strategy, Definition of Done, risks, rollback.
- **Open Questions:** `None`, or only items explicitly marked non-blocking/deferred with the reason.

## Architecture Contract

```text
Business capability and owning module
Behaviour owner and state owner; authoritative rule location
Existing dependency direction; allowed new edges; forbidden edges and internal surfaces
Public API and data-model impact
Transaction, concurrency, idempotency boundary
Empty / rejection / failure / timeout / fallback semantics
Existing patterns to reuse; new abstractions or control surfaces and their present justification
Change-locality boundary; cleanup of superseded code, rules, config, tests, docs
Verification evidence required
```

Treat size and dependency counts as investigation signals, not acceptance gates, unless the repository has an approved measured limit.

## Phases

Each phase: stable ID, goal, Allowed / Not Allowed / Deferred, prerequisites (phases, decisions, reviews, checkpoints), Architecture Contract and rule IDs, likely files, acceptance IDs mapped to deliverables, tests to add (named), verification commands, cleanup and stale-reference checks, manual checks.

Prefer narrow vertical slices through the needed layers over "all backend, then all frontend". Do not mix broad refactoring with feature delivery.

The implementation record tracks: phase checklist and status, review references, branch decision, conformance evidence by rule ID, finding ledger (`OPEN | READY_FOR_REVIEW | CLOSED | BLOCKED | INVALID`), files, tests, commands and results, known failures, manual checks actually done, deferred items.

## Reference adaptation matrix

| Area | Reference behaviour | Current state | Decision | Reason |
|---|---|---|---|---|
| API / data / UI / dependency / security |  |  | Adopt / Adapt / Reimplement / Reject / Defer |  |

`Adopt` only when it fits without changing architecture or approved scope; `Adapt` to follow local conventions; `Reimplement` when the behaviour is needed but the code must not be copied; `Reject` on conflict; `Defer` outside the phase.

## Handoff

- Large or risky plans go to `$cross-review` (read-only plan review) before implementation. `APPLY-REVIEW-FIX` → `$apply-review-fix`, then re-review. `REJECT` → resolve the decisions first.
- `$feature-implementer` starts only when blocking questions are resolved, the review says `ACCEPT`, and blocking findings are `CLOSED`.
- Material scope, boundary, or acceptance changes after review need a new user decision and another review.
- Record durable, verified project facts or pitfalls in the `AGENTS.md` knowledge ledger (fact, action, evidence; no secrets or history).
