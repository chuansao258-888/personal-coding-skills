---
name: feature-implementer
description: Use when implementing a cross-reviewed, approved feature plan, a named phase, or an orchestrator's dispatch. Enforces task-branch, prerequisite, behaviour-contract, Architecture Contract, boundary, cleanup, and verification gates, and hands off as IMPLEMENTED_PENDING_REVIEW instead of self-accepting or committing early.
---

# Feature Implementer

Implement the approved phase faithfully, keep the change scoped, prove it with tests, and record the evidence. Implement the named phase, not the whole roadmap.

**Size it.** A small change (one-line or behaviour-neutral, or tests aligned to a recorded ruling) needs only the boundary, targeted tests, and a short record. Everything else uses the full gates.

## Common gates

- **Branch:** start with `git status --short --branch`. Plan, implementation, fix, and re-review of one task share one branch (repository convention, else `feat/<task-slug>`). Switch or create only from a clean worktree; never stash, reset, or carry unrelated changes — use a separate worktree or ask.
- **Source of truth:** latest explicit user instruction > approved plan > implementation record > current code > reference behaviour > general practice.
- **Intent:** never satisfy a finding or difficulty by dropping, deferring, narrowing, or weakening a requested capability. If the plan and the latest user intent diverge, stop and ask.
- **Standards:** read `AGENTS.md`, `ENGINEERING_STANDARDS.md` (or equivalent), glossary, ADRs, and the knowledge ledger; use their terms and cite rule IDs.
- **Orchestrated mode:** when an orchestrator dispatched this task, its dispatch is the execution contract. Report design gaps to it instead of deciding; do not commit unless the dispatch says so.
- Never push or open a PR unless the user asks. Never quote secret values from local configuration. Preserve unrelated changes.

## Before editing

Assemble the execution contract: plan path and phase, goal, acceptance and behaviour-contract rule IDs, Allowed / Not Allowed / Deferred, cleanup obligations, verification, prerequisites, latest review recommendation, open finding IDs.

Proceed only when:

- the latest plan review says `ACCEPT` (or the user or orchestrator waived it), and blocking findings are `CLOSED`;
- prerequisite phases are accepted and required checkpoints exist;
- no unresolved Open Question, Option, or TBD affects this phase — otherwise ask; never pick an option yourself;
- success criteria are measurable (expected behaviour, edge cases, named tests, build expectations, manual checks).

`APPLY-REVIEW-FIX` → use `$apply-review-fix`, not this skill. `REJECT` or a new product or architecture decision → return to `$feature-planner` or the user. If the user asks to continue or verify a phase, first check whether it is already implemented.

## While implementing

- One narrow vertical slice at a time, inside `Allowed`; never touch `Not Allowed` or `Deferred`.
- For bugs and behaviour changes, write the failing test first, make the smallest fix, refactor only when green. If TDD is impractical, say why.
- Keep one authority per business rule and one owner per state; no cross-module internals, reversed dependencies, cycles, or unplanned public surface.
- Add no interface, factory, registry, wrapper, retry, cache, fallback, or compatibility layer without a present, phase-specific reason. Keep empty, rejection, failure, timeout, and degradation distinguishable.
- Match local style: placement, naming, construction, errors, logging, imports, tests. Do not reformat unrelated code.
- Keep files within the repository's size and layering rules; split along responsibilities instead of growing a god file.
- Remove superseded code, config, tests, and comments named by Cleanup, and search for stale references.
- Comments only for non-obvious reasoning or invariants.

If conformance needs a new architecture decision or a prohibited surface, stop and return to `$feature-planner`.

## Tests

- Prove observable behaviour: exact payloads and events, ordering, limits, timeouts, malformed and boundary input, disabled and unavailable states, privacy of logs. Not just that a mock was called.
- Name tests after the behaviour-contract rule IDs they prove; add a regression test for every finding.
- A failing existing test is a contract: fix the code, or stop and report the conflict. Never loosen assertions, delete coverage, or edit shared fixtures outside the task.
- Tests run silently: headless browsers, recording ports instead of real shell, file-picker, or opener calls, every async wait bounded by a timeout.

## Verification

Run synchronously, narrow to broad: targeted tests; the complete test set of every package you touched (not only edited files); every stack affected by a shared type or interface change; lint, type check, build; manual or headless UI check of changed flows. Review `git diff` for unintended files, secrets, debug code, and scope creep. Record pre-existing failures separately. Quote raw summary lines; if something did not run, say so.

## Record and hand off

Update the implementation record: status `IMPLEMENTED_PENDING_REVIEW`; acceptance and rule-ID evidence; boundary audit; Architecture Conformance Evidence (ownership, dependency edges, public surface, failure semantics, new abstractions and why, cleanup); files; tests; commands and results; known failures; manual checks still pending. Add durable, verified pitfalls to the `AGENTS.md` knowledge ledger.

Never mark a phase accepted or commit before independent acceptance. Hand off to `$cross-review` (or the orchestrator) with the execution contract and evidence. Final response: what changed, what ran and passed, what remains.
