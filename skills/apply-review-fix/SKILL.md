---
name: apply-review-fix
description: Use when applying drift-bounded findings from a plan or implementation review, or an orchestrator's fix round. Stays on the reviewed task branch, consumes Finding IDs with their boundaries, acceptance, validation, cleanup, and closure criteria, makes only the minimal allowed change, and returns evidence as READY_FOR_REVIEW for independent re-review.
---

# Apply Review Fix

Make each selected finding ready for independent re-review with the smallest correct change. Fix the reviewed issue, not the surrounding codebase, and never redefine or self-close a finding.

**Size it.** A small finding (one-line, or aligning a test to a recorded ruling) needs only the change, its validation, and a one-line evidence entry.

## Common gates

- **Branch:** start with `git status --short --branch`; use the reviewed task's branch, no separate repair branch unless policy requires it. Never stash, reset, or carry unrelated changes.
- **Source of truth:** latest explicit user instruction > approved plan > implementation record > current code. If a finding contradicts the plan or a newer decision, stop and ask.
- **Intent:** never "fix" a finding by weakening the requirement — rewriting the plan so it disappears, making it optional or warn-only, or moving it out of phase — without the user's approval.
- **Standards:** read `AGENTS.md`, `ENGINEERING_STANDARDS.md` (or equivalent), behaviour contracts, glossary, ADRs, knowledge ledger; preserve cited rule IDs.
- **Orchestrated mode:** in an orchestrator's fix round, its dispatch is the contract; report gaps to it and do not commit unless told.
- Never push or open a PR unless the user asks. Never quote secret values. Preserve unrelated changes.

## Intake

Build a repair ledger in the review's Fix Order. Per finding: ID, classification, confidence, rule IDs, required change, minimal fix, Allowed / Not Allowed / Deferred, acceptance, validation, cleanup, invariant to restore, closure criteria, status `PENDING`.

- `ACCEPT`: nothing to repair; invent no work.
- `REJECT`: no production or plan-semantic edits; only the requested bounded investigation, then back to review or planning.
- `APPLY-REVIEW-FIX`: repair the selected findings whose reviewer checklist is fully green.
- Confidence `LOW` or an unchecked checklist item: get the missing evidence first. `MEDIUM`: verify the stated assumption; if false, stop rather than improvise.
- Unresolved Open Questions, Options, or TBD in the plan or record that affect the fix: ask before editing.
- Legacy findings without the structured contract: normalize only when the boundary is unambiguous, and state it before editing.
- Never implement `Future Enhancement` items. An invalid finding gets file-and-line evidence, not a forced change.

## Plan fix

When findings target a plan and code has not started: edit only the cited plan, design, ADR, contract, glossary, or record documents. Close gaps such as unclear decisions, missing gates, weak boundaries, missing acceptance or behaviour-contract rules, missing reference decisions, stale conflicting text. Leave real choices as blocking questions for the user; never decide product, architecture, data, API, or UX on their behalf. Re-read changed sections, check fences, search for old phrasing, and map each finding to its acceptance and boundary.

## Implementation fix

1. Re-check for blocking Open Questions; read only the cited or Allowed code and nearby tests.
2. For non-obvious runtime or performance bugs: reproduce, minimize, state 2–4 falsifiable hypotheses, instrument only to test them (tag temporary logs uniquely and remove them), turn the reproduction into a regression test.
3. Write or update the regression test named by Validation so it fails without the fix.
4. Apply the minimal fix for one finding or a dependency-coherent group; a group never widens the file scope.
5. Run the finding's validation, then the complete test set of every touched package and every affected stack, synchronously; quote raw summary lines.
6. Complete Cleanup; leave no second authority, obsolete fallback, dead abstraction, or stale config.
7. Audit the diff against the boundary, rule IDs, ownership and dependency invariants, secrets, and debug code.

If the minimal fix would change ownership, dependency direction, public API, concurrency, or the failure model beyond the finding, stop and return to `$feature-planner`. Keep fixes simple and in local style; add no new variable, gate, retry, or fallback unless the finding requires it.

## Tests

Prove the real contract: captured payloads or events for propagation bugs, exact order for sequences, negative cases (wrong session, disabled, permission, empty, malformed), boundary values, privacy of logs on success and failure paths. Never loosen assertions, delete coverage, or edit shared fixtures outside the boundary to make a finding pass. Tests run silently with bounded waits.

## Evidence and handoff

Per finding, record in the implementation record: `READY_FOR_REVIEW | BLOCKED | INVALID`; required-change, acceptance, validation, and cleanup evidence; boundary audit; branch; rule-ID evidence; files; simplicity and style impact; tests; commands and results; remaining manual checks; knowledge-ledger entry or `None`.

Never claim `CLOSED` or accepted, and never commit before re-review closes the findings. Final response: finding IDs in fix order with status and evidence, what actually ran, residual risk. Hand off to `$cross-review` (or the orchestrator) with the original IDs, specifications, checklists, and closure criteria.
