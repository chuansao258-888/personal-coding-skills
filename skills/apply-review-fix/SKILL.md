---
name: apply-review-fix
description: Use when applying drift-bounded findings from plan or implementation review. Stay on the reviewed task branch; consume Finding IDs, engineering-standard rules, boundaries, checklists, and closure criteria; make only minimal allowed changes and return validation, cleanup, and architecture evidence for re-review.
---

# Apply Review Fix

Use this skill after a review has produced concrete findings that need plan, documentation, code, or test changes.

The goal is to make each selected finding ready for independent re-review with
the smallest correct change, without letting the fixer redefine or self-close
the finding.

## Core Rules

- Fix the reviewed issue, not the surrounding codebase.
- Preserve the Finding ID, classification, Fix Specification, Implementation
  Boundary, Acceptance, Validation, Cleanup, and Closure Criteria. They are the
  repair contract, not suggestions to reinterpret while coding.
- Respect `Allowed`, `Not Allowed`, and `Deferred` literally. If the repair
  appears to require a prohibited or deferred surface, stop instead of expanding
  scope or retroactively changing the plan.
- Never implement `Future Enhancement` items as part of a review fix.
- Follow the review's `Fix Order` unless repository evidence proves a dependency
  inversion; record that evidence before changing the order.
- Preserve unrelated user changes and existing behavior.
- Pass the Task Branch Gate and inspect relevant diffs before editing.
- Read repository glossary/context files and relevant ADRs when a finding touches domain language or architecture.
- Read `ENGINEERING_STANDARDS.md` or the repository equivalent and the project
  knowledge/pitfall ledger in `AGENTS.md`; preserve cited rule IDs.
- Read repository environment/configuration docs when a finding touches env vars, provider settings, feature flags, or runtime defaults. Treat local config as secret-bearing and do not quote real values.
- Do not weaken tests, loosen assertions, or delete coverage to make a finding pass.
- Add or strengthen a regression test for every behavioral finding whenever practical.
- If the finding contradicts an approved plan or newer user decision, stop and ask before coding.
- If a finding is invalid after inspection, document why with file and line evidence instead of forcing a change.
- Do not mark a finding `CLOSED`. Report `READY_FOR_REVIEW`, `BLOCKED`, or
  `INVALID`; only a subsequent `$cross-review` may evaluate Closure Criteria and
  close it.
- Keep implementation documents accurate; do not mark manual E2E complete unless it was actually run.
- Do not commit a repair before independent re-review closes its findings. The
  accepting `$cross-review` performs any repository-required automatic phase
  checkpoint. Never push or open a PR unless the user explicitly asks.
- Keep fixes simple and proportionate. Do not introduce avoidable nesting,
  speculative abstractions, pass-through wrappers, or broad refactors to close
  a narrow finding. Add no variable/parameter, gate/threshold, retry, fallback,
  or compatibility branch unless the Finding requires it and identifies its
  current need, real consumer or trigger, and verification.
- Keep code style consistent with the touched area. Do not mix conventions or reformat unrelated files to close a narrow finding.
- If fixing a review finding reveals unresolved `Open Questions`, `Open Decisions`, `Options`, `Alternatives`, `TBD`, or equivalent blocking clarification items in the plan, implementation document, review result, or current phase, stop and ask the user. Do not start or continue implementation until those questions are clarified.

## Task Branch Gate

At the start of every review-fix task:

1. Run `git status --short --branch` and `git branch --show-current`.
2. Use the same task branch as the reviewed plan/implementation and original
   Finding IDs. Do not create a separate repair branch for the same phase unless
   the user or repository policy explicitly requires it.
3. If the current branch is wrong and the worktree is clean, switch to the task
   branch automatically. If the branch does not exist, create it from the
   approved base using the repository convention or `feat/<task-slug>`.
4. If unrelated dirty changes would be carried across branches, do not stash,
   reset, discard, or silently transport them. Prefer a separate worktree when
   safe; otherwise stop and ask the user.

Record the branch decision in Closure Evidence.

## Original Intent Guardrail

Fix the finding while preserving the user's original product intent and latest explicit decisions.

- Do not fix by rewriting the plan so the requirement disappears, moves out of phase, becomes optional or warn-only, or is reframed as out of scope unless the user explicitly approves.
- Before changing scope, acceptance gates, phase boundaries, tuning/configuration support, or user-visible behavior, compare against the original request, latest user decisions, plan history, and review finding.
- If the minimally correct fix conflicts with the current plan, ask the user instead of silently choosing a different product direction.
- When the user says a previous fix drifted from intent, audit related fixes for the same drift pattern before continuing.
- Treat "fixing" a finding by weakening the requirement as an invalid fix, even if tests or wording become easier.

## Finding Intake Gate

Before editing, read `Overall Review` and normalize every selected finding into
a repair ledger containing:

```text
Finding ID
Classification
Repair Confidence
Engineering-standard Rule IDs
Required Change
Minimal Fix
Allowed
Not Allowed
Deferred
Acceptance
Validation
Cleanup
Architecture / consistency invariant to preserve or restore
Closure Criteria
Status: PENDING
```

Apply these gates:

- `ACCEPT`: there is no required repair. Do not invent work.
- `REJECT`: do not edit production code or plan semantics. Perform only the
  explicitly requested bounded investigation/clarification, then return to
  `$cross-review` or `$feature-planner`.
- `APPLY-REVIEW-FIX`: proceed only for selected `Blocking Fix` or
  `Non-blocking Fix` IDs whose proposal-level Reviewer Checklist is fully green.
- `Repair Confidence=LOW` or any unchecked/unjustified Reviewer Checklist item:
  stop before implementation and obtain the missing evidence or clarification.
- `Repair Confidence=MEDIUM`: verify the stated assumption first; if false,
  stop instead of improvising a different repair.

For legacy findings that predate the structured contract, normalize them only
when evidence makes the required behavior, allowed surfaces, acceptance, tests,
and cleanup unambiguous. State the inferred boundary before editing. If a
material product/architecture/scope choice remains, return for a new
`$cross-review` rather than guessing.

## Workflow

1. Pass the Task Branch Gate, then run the Finding Intake Gate and build the
   repair ledger in review Fix Order.
2. Determine fix mode:
   - Plan Fix: findings came from Plan Review, and implementation has not started.
   - Implementation Fix: findings came from Implementation Review, or code/tests/runtime behavior must change.
3. Read the latest user instruction, plan/implementation document, cited code,
   and nearby tests without changing the finding contract.
4. Verify each finding's root cause and MEDIUM-confidence assumptions.
5. Apply one finding or dependency-coherent group without crossing any boundary.
6. Run the finding's named Validation and complete its Cleanup obligations.
7. Audit the diff against `Allowed`, `Not Allowed`, `Deferred`, cited
   engineering-standard rule IDs, ownership/authority/dependency/failure
   invariants, secrets, debug logs, unrelated changes, and the approved goal.
8. Update project-level `AGENTS.md` when the repair confirms a durable project
   fact or recurring pitfall; record fact, required action, and evidence only.
9. Record Closure Evidence and status for each Finding ID, then hand off to
   `$cross-review`.

## Fix Modes

### Plan Fix

Use Plan Fix when code has not started and the review findings are about plan readiness.

Allowed changes:

- the plan, design, ADR, implementation record, or documentation files cited by the review;
- fallback plan docs such as `docs/plans/<feature-slug>.md`;
- fallback architecture docs such as `docs/architecture/<design-slug>.md`;
- fallback implementation records such as `docs/implementation/<feature-slug>-implementation.md`;
- Repository glossary/context docs
- `docs/adr/`
- Environment/configuration docs only for variable names or configuration coverage, without exposing real values
- Other documentation explicitly named by the user

Do not edit business code, tests, prompts, migrations, UI, or runtime configuration in Plan Fix mode unless the user explicitly asks to start implementation.

Plan Fix should close gaps such as unclear decisions, missing production gates, weak phase boundaries, missing acceptance criteria, incomplete reference adaptation matrix, missing risks, or stale conflicting plan text.

If Plan Fix leaves blocking Open Questions or unresolved Options, make them explicit and ask the user. Do not mark the plan implementation-ready, and do not proceed into Implementation Fix or feature implementation.

If a plan fix introduces or preserves multiple viable options for the current phase, record them as blocking and ask the user to choose. Do not make an implicit product, architecture, provider, data, API, UX, or test-gate decision on the user's behalf.

If a plan review finding is about implementation quality, update the plan to state simplicity constraints: existing patterns to reuse, abstractions/refactors to avoid, complexity risks, and what must be justified in the implementation document.

If a plan review finding is about code style, update the plan to state the local style constraints an implementer must follow: naming, package/module layout, DTO/type/component/test conventions, error/log handling, formatting, and verification commands.

If a plan finding cites architecture or consistency rules, update the phase's
Architecture Contract with the exact ownership, authoritative rule, dependency
direction, public surface, failure/fallback semantics, abstraction boundary,
cleanup, and proof required. Do not solve an unresolved architecture decision by
inventing production classes in the plan.

Verification for Plan Fix:

- Re-read changed sections.
- Check markdown structure and fenced code blocks when relevant.
- Search for old conflicting phrasing.
- Confirm each plan review finding is either fixed, explicitly marked non-blocking/deferred, escalated to the user as a blocking Open Question, or explained as invalid with evidence.
- For every selected Finding ID, map changed sections to Required Change,
  Acceptance, Validation, Cleanup, and the `Allowed` boundary. Report it as
  `READY_FOR_REVIEW`, not closed.

### Implementation Fix

Use Implementation Fix when code, tests, prompts, migrations, UI, runtime config, or behavior must change.

Before editing code, tests, schemas, prompts, runtime config, or project documentation in Implementation Fix, re-check the plan, implementation document, review findings, and latest user decision for unresolved blocking Open Questions or Options. If any remain, ask the user and stop instead of guessing a fix.

Implementation document Open Questions are binding blockers. If the implementation document still contains unresolved blocking questions, do not begin an implementation fix, even when the review finding is concrete. First ask the user to clarify, or update the implementation document with a newer explicit answer from the user.

Workflow:

1. Inspect only the finding's cited/Allowed code and nearby tests before editing.
2. For complex bugs, build a feedback loop before changing behavior.
3. Add or update the regression test named by Validation so it fails without
   the fix when practical.
4. Apply the specified Minimal Fix for one Finding ID or dependency-coherent
   group; do not use the group as permission to widen file scope.
5. Run the finding's targeted Validation first, then broader verification when
   the specified regression risk or shared contract justifies it.
6. Complete the finding's Cleanup list and search for stale references.
7. Update the implementation document with per-ID Closure Evidence, tests,
   commands/results, boundary audit, and remaining risk.

Implementation Fix must remove or avoid unnecessary complexity introduced by the fix. If extra complexity is required, document why and cover the risk with tests.

Implementation Fix must preserve local code style. Fix style findings only in the affected files/lines unless the user explicitly asks for a broader style cleanup.

Implementation Fix must restore the cited architecture/consistency invariant
with the smallest allowed change. Do not leave a second authority, obsolete
fallback, dead abstraction, stale config, or contradictory comment behind when
Cleanup requires its removal. If the proposed minimal fix changes ownership,
dependency direction, public API, transaction/concurrency semantics, or the
approved failure model beyond the finding boundary, stop and return to
`$feature-planner` instead of redesigning during repair.

## Diagnose Mini-Loop

For non-obvious runtime bugs or performance regressions:

1. Reproduce the reported symptom or explain why it cannot be reproduced.
2. Minimize the reproduction to the fastest reliable test, command, HTTP request, or browser flow.
3. State 2-4 falsifiable hypotheses before changing code.
4. Add targeted instrumentation only when it tests a hypothesis.
5. Convert the minimized reproduction into a regression test when a correct seam exists.
6. Remove temporary instrumentation before final reporting.

Tag any temporary debug log with a unique prefix such as `[DEBUG-review-fix-<short-id>]` and search for the prefix before finishing.

## Test Expectations

For each fixed finding, prefer tests that prove the real contract:

- Capture prompts, DTOs, payloads, or events when the bug is about propagation.
- Assert exact ordering when the contract depends on sequence.
- Include negative cases for wrong turn, wrong session, disabled flags, permission boundaries, and empty or malformed inputs.
- Assert boundary values for budgets, limits, truncation, and fallback behavior.
- Verify privacy-sensitive logs by checking both failure paths and success paths when logging behavior is part of the contract.

Avoid tests that only verify a method was called if the bug is inside that method's implementation.

## Dirty Worktree Safety

If the worktree contains unrelated changes, classify them before editing or reporting:

- `fix`: bug, test, type, or build correction
- `feature`: user-visible behavior or new endpoint/page
- `chore`: config, workflow, dependency, or cleanup
- `docs`: documentation or plan updates

Only touch files needed for the reviewed findings. Do not stage, commit, push, stash, or discard unrelated changes unless the user asks.

## Documentation-Only Fixes

For documentation-only review findings:

- Treat the latest user decision as the source of truth.
- Patch the decision-bearing section instead of rewriting the whole document.
- Re-read changed sections.
- Check markdown fence balance when code blocks were touched.
- Search for old conflicting phrases so stale guidance does not remain elsewhere.

## Documentation Update

Update the relevant `docs/implementation/<feature-slug>-implementation.md` file when a fix changes implementation details, acceptance status, tests, or known limitations. If the repository stores implementation records inside a plan document, update that section instead.

For any new or renamed file, follow repository-local standards from `AGENTS.md`, README, contributor docs, and nearby existing files.

Use a short entry with:

- Finding ID and `READY_FOR_REVIEW | BLOCKED | INVALID` status
- Required Change evidence
- Acceptance evidence
- Validation command/result evidence
- Cleanup evidence
- Boundary audit (`Allowed` touched; `Not Allowed`/`Deferred` untouched)
- Task branch decision
- Engineering-standard Rule IDs and architecture/consistency evidence
- Files changed
- Simplicity impact, including removed complexity or justified remaining complexity
- Code style impact, including local convention followed and any style-only churn avoided
- Project knowledge/pitfall ledger entry added, consolidated, or `None`
- Test coverage added or strengthened
- Verification command and result
- Remaining manual checks, if any

## Final Response

Lead with the outcome. Include:

- Finding IDs in Fix Order
- Status for each: `READY_FOR_REVIEW | BLOCKED | INVALID`
- Required Change, Acceptance, Validation, Cleanup, and boundary evidence for
  each selected finding
- Tests/builds/manual checks actually run
- Documentation updated
- Residual risk or evidence still missing

Do not claim `CLOSED`, accepted, or checklist-complete on behalf of the reviewer.

## Skill Handoff

After applying fixes:

- Use `$cross-review` with the original Finding IDs, Fix Specifications,
  Reviewer Checklists, Closure Criteria, and new evidence so it can decide
  `OPEN` versus `CLOSED`.
- Use `$feature-implementer` only if the user asks to continue, no blocking Open
  Questions remain, and the subsequent `$cross-review` reports required
  findings `CLOSED` with recommendation `ACCEPT`.
- Use `$feature-planner` if a finding exposes an unresolved product, architecture, dependency, data, security, or acceptance decision.
- Use `$module-introduction` after accepted implementation when onboarding or architecture documentation is requested.
