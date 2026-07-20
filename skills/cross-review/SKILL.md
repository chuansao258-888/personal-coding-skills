---
name: cross-review
description: Use when reviewing a plan before implementation or completed work against an approved plan, engineering standards, implementation document, or acceptance criteria. Check architecture/consistency, bugs, drift, tests, scope, and verification; produce drift-bounded finding contracts and, after accepted implementation, perform any required scoped phase checkpoint commit.
---

# Cross Review

Use this skill when the user asks to review a plan/design before code exists, or to review/accept a completed phase, feature, or review-fix pass.

The goal is to decide whether a plan is safe to implement, or whether completed work is logically correct, follows the plan, and has enough test coverage to protect the intended behavior.

## Review Stance

Start from findings.

For plan review, prioritize unclear decisions, untestable acceptance criteria, unsafe scope, missing production gates, weak phase boundaries, and missing risks.

For implementation review, prioritize bugs, behavioral regressions, missing tests, plan drift, security or privacy issues, unnecessary scope, and avoidable implementation complexity.

Do not lead with praise or a long summary. If there are no findings, say so clearly and mention any remaining manual checks or residual risk.

Review is read-only by default. Do not edit files or apply fixes. The only
repository mutation allowed during review is a post-acceptance phase checkpoint
commit when project policy explicitly requires automatic phase commits and the
Checkpoint Gate below is fully green. Never push or open a PR unless the user
explicitly asks.

## Source Of Truth

When information conflicts, use this order:

1. Latest explicit user instruction
2. Approved plan document
3. Implementation document
4. Current code
5. Existing tests
6. General best practices

Do not treat older design text as binding if the user has made a newer decision.

## Task Branch Gate

At the start of every distinct review task:

1. Run `git status --short --branch` and `git branch --show-current`.
2. Determine the expected task branch from the latest user goal and approved
   plan. A plan review, implementation, review-fix, and re-review for one feature
   stay on the same branch.
3. Continue when it matches. If the worktree is clean and the current branch is
   the default or unrelated, create or switch automatically using the
   repository convention, falling back to `feat/<task-slug>`.
4. If unrelated dirty changes would be carried across branches, do not stash,
   reset, discard, or silently move them. Prefer a separate worktree from the
   intended base when safe; otherwise stop and ask the user.

Record the branch decision in `Reviewed Target`. Do not create a new branch for
the re-review of an existing task.

## Intent Drift Review

Review whether plans, review fixes, and implementation choices preserve the user's stated intent.

- Compare the latest plan or implementation against the original user request, latest explicit instructions, confirmed decisions, and the specific finding being fixed.
- Flag Spec drift when a finding is closed by changing the requirement instead of satisfying it, such as deferring requested RAG tuning support, weakening a hard acceptance gate to warn-only without approval, or removing user-visible scope.
- In Plan Review, do not accept a plan that silently drops, defers, narrows, or weakens user-requested behavior. Return a finding and recommend `REJECT` when clarification is required.
- In Implementation Review, inspect review-fix diffs for scope shrink, phase-boundary changes, and acceptance-gate weakening, not only whether the previous finding text disappeared.
- If the user's original intent and the current plan conflict, ask for clarification instead of choosing the narrower interpretation.

## Fix Proposal Anti-Drift Contract

A reviewer has authority to specify how to close an evidenced finding inside
the approved target. A reviewer does not have authority to redesign the feature,
change product semantics, weaken acceptance, or invent adjacent work.

For every proposed fix:

- Trace it to one finding, one approved goal/criterion, and the smallest affected
  behavior surface.
- Preserve the latest user goal, current phase, public contracts, explicit
  non-goals, and deferred boundaries.
- Prefer the smallest sufficient correction. Do not introduce a framework,
  dependency, provider, schema, endpoint, migration, abstraction, or broad
  refactor unless the approved plan already requires it and the finding cannot
  be closed without it.
- State what may change, what must not change, and what remains deferred. Do not
  leave those boundaries for the fixer to infer.
- Do not "fix" implementation drift by editing the plan after the fact. The code
  must return to the approved plan unless the user explicitly approves a plan
  change.
- When the diff already contains an unapproved adjacent feature, the default
  repair is to remove that out-of-scope change and its tests/config/dependency,
  not to broaden the finding or retroactively add it to the plan. Record the
  idea as a future enhancement only when useful.
- Do not turn a possible enhancement into a blocking defect. Put useful but
  unrequested improvements under `Future Enhancement` and exclude them from the
  verdict and required fix.
- Do not prescribe speculative implementation details as fact. If root cause or
  the safe repair is uncertain, lower repair confidence and require focused
  investigation or user clarification before implementation.
- If the only plausible fix changes scope, architecture, API/data contracts,
  provider/dependency choice, security posture, phase boundaries, or acceptance
  gates, recommend `REJECT`, state `Clarification required`, and route back to
  `$feature-planner`.

Before emitting a finding, answer internally:

1. Which exact requirement or project standard is violated?
2. Is the root cause confirmed by evidence or only inferred?
3. What is the narrowest change that closes the issue?
4. Which tempting adjacent changes are outside this finding?
5. What observable test would fail before and pass after the fix?

## Workflow

1. Determine review mode:
   - Plan Review: code has not started, or the user asks to review a plan/design.
   - Implementation Review: code, tests, docs, prompts, migrations, or UI changes exist and need acceptance.
2. Pass the Task Branch Gate and read the relevant plan and implementation document.
3. In Implementation Review, inspect the diff scope and classify unrelated
   dirty changes before evaluating or staging anything.
4. Read `AGENTS.md`, `ENGINEERING_STANDARDS.md` or its equivalent, the project
   knowledge/pitfall ledger, glossary/context files, relevant ADRs, and
   environment/configuration docs when config is involved.
5. For Plan Review, inspect current code only enough to validate feasibility, existing patterns, and missing decisions.
6. For Implementation Review, inspect changed source files, tests, prompts, migrations, and frontend contracts.
7. Review along two axes: Spec and Standards, with explicit Architecture,
   Consistency, and Simplicity subchecks under Standards.
8. Run targeted verification when useful and affordable. Do not run implementation verification for plan-only review.
9. Confirm each finding's evidence and root cause before prescribing a repair.
10. Write a minimal fix specification with explicit allowed/prohibited/deferred
    boundaries, acceptance, validation, cleanup, and regression risk.
11. Complete the Reviewer Checklist and Closure Criteria for each finding,
    order fixes by dependency and severity, then produce the Overall Review
    summary and recommendation.
12. On an accepted implementation phase, run the Phase Checkpoint Gate when the
    repository requires automatic phase commits.

## Review Modes

### Plan Review

Use Plan Review when implementation has not started or the user asks whether a plan is ready.

The review outcome should answer: can another agent safely implement this plan without making major unstated product or architecture decisions?

Do not require code diff, tests, or build output for plan-only review. Do not claim implementation acceptance.

A plan with unresolved blocking `Open Questions`, `Open Decisions`, `Options`, `Alternatives`, `TBD`, or equivalent clarification items is not implementation-ready. Return a blocking finding and recommend `REJECT` with `Clarification required`; do not accept the plan until those questions are answered by the user or explicitly marked non-blocking/deferred.

A plan that lists multiple implementation options, recommended-but-unconfirmed choices, or "choose one" alternatives for the current phase is not ready for implementation. Do not let the implementer decide; require user confirmation first.

An implementation document with unresolved blocking `Open Questions`, `Open Decisions`, `Options`, `Alternatives`, `TBD`, `To Clarify`, or equivalent items also blocks starting implementation. Treat those items as P1 Spec findings unless they are explicitly answered by a newer user decision, explicitly marked non-blocking/deferred, or clearly outside the reviewed phase.

For a Plan Review finding, specify the exact plan sections/decisions/acceptance
criteria that must be added or corrected. Do not prescribe production code as
the required fix while product or architecture decisions are still unresolved.
If user confirmation is required, the fix is the clarification and plan update,
not an implementer-selected option.

### Implementation Review

Use Implementation Review when code or docs have changed and the user asks to review, accept, or verify a phase.

The review outcome should answer: does the implementation satisfy the approved plan and project standards with enough verification evidence?

For an Implementation Review finding, keep the required fix inside the approved
phase and existing architecture. Documentation may be corrected to describe the
approved behavior and actual verification, but must not be rewritten to make a
non-conforming implementation appear compliant.

## Two-Axis Review

Run both axes explicitly:

- Spec Review: does the plan or implementation match the latest user instruction, approved plan, implementation document, and acceptance criteria?
- Standards Review: does the plan or implementation match project language,
  ADRs, repository engineering-standard rule IDs, existing architecture, test
  style, privacy rules, git hygiene, and frontend/backend conventions?

Keep the axes distinct in your notes so a correct implementation with poor standards, or clean code that implements the wrong thing, does not hide behind a single mixed verdict.

Within Standards, label concrete findings as
`[Standards/Architecture]`, `[Standards/Consistency]`, or
`[Standards/Simplicity]` when that precision helps. Do not promote a general
architecture preference into a finding unless it violates an approved rule,
local convention, phase contract, or observable maintainability boundary.

## Architecture And Consistency Review

For plans, verify that every non-trivial phase defines an Architecture Contract:

- business capability, behavior owner, state owner, and authoritative rule;
- existing, allowed, and forbidden dependency edges;
- public API/data-model and transaction/concurrency impact;
- distinct empty, rejection, failure, timeout, and fallback semantics;
- existing pattern reuse, justified abstractions, change locality, cleanup, and
  evidence required.

For implementations, verify the corresponding Architecture Conformance
Evidence against the actual diff. Inspect for parallel business-rule authority,
cross-module internal access, cycles or reversed dependencies, leaked provider
models, unnecessary public API, pass-through layers, speculative abstractions,
hidden errors, ambiguous fallback, and incomplete cleanup.

Use architecture metrics and size/dependency counts as investigation signals,
not mechanical defects, unless the repository has an approved measured limit.

## Naming And Layout Review

Review new files, directories, language pairs, fixtures, generated outputs, and naming against repository-local standards from `AGENTS.md`, README, contributor docs, and nearby existing files. Flag local convention violations before generic style preferences.

## Plan Review Checklist

- Does the plan state the user problem, goals, non-goals, user flow, scope, and deferred work clearly?
- Does the plan preserve the user's requested capability instead of resolving risk by silently narrowing, deferring, or weakening it?
- Are blocking product, architecture, API, database, dependency, provider, security, privacy, release, or reference-adaptation decisions resolved or explicitly marked as open?
- If the plan has `Open Questions`, `Options`, `Alternatives`, or recommended-but-unconfirmed choices, are they `None`, already answered by newer user decisions, or explicitly non-blocking/deferred? Treat unresolved blocking choices as a P1 Spec finding.
- If the implementation document has `Open Questions`, `Options`, `Alternatives`, or recommended-but-unconfirmed choices, are they `None`, already answered by newer user decisions, or explicitly non-blocking/deferred? Treat unresolved blocking choices as a P1 Spec finding before telling implementation to start.
- Are acceptance criteria testable, concrete, and tied to success, failure, boundary, permission, privacy, API, UI, SSE, prompt, tool, or agent contracts where relevant?
- Are implementation phases vertical slices with goals, expected files/modules, deliverables, tests, verification commands, and manual checks?
- Are production planning gates covered when relevant: API contract, data/migration, configuration/env vars, security/privacy, release/rollback, observability, and Definition of Done?
- Does the plan constrain implementation simplicity: existing patterns to reuse, abstractions/refactors to avoid, and complexity risks that need justification?
- Does every planned variable/parameter, gate/threshold, retry, fallback, or
  compatibility branch map to a current requirement or evidenced failure mode,
  a real consumer or trigger, and focused verification?
- Does the plan identify code style constraints for touched areas: naming, package/module layout, DTO/type/component/test conventions, error/log handling, formatting, and lint/type/build expectations?
- Does each non-trivial phase provide an Architecture Contract with applicable
  repository rule IDs, ownership, authority, dependency direction, failure
  semantics, abstraction justification, locality, cleanup, and proof?
- Does the plan record the correct task branch and post-acceptance checkpoint
  expectation without requiring a new branch per phase?
- If a reference project is used, does the plan include an adaptation matrix with Adopt / Adapt / Reimplement / Reject / Defer decisions?
- Does the plan use canonical terms from repository glossary/context docs and respect relevant ADRs?
- Are risks, rollback/fallback behavior, and manual E2E limitations stated honestly?
- Does the plan avoid extra endpoints, debug APIs, permissions, migrations, dependencies, or UI scope that the user did not approve?
- Is the plan implementation-ready, or would an implementer still need to invent major requirements?

## Implementation Review Checklist

- Does the implementation match the exact phase scope?
- Does the implementation document still contain unresolved Open Questions that affect the reviewed phase? If yes, do not accept the phase or recommend further implementation until they are clarified.
- Does the implementation preserve the latest user intent and approved capability, including review-fix changes that may have narrowed scope or weakened acceptance gates?
- Did it add extra endpoints, permissions, debug APIs, UI scope, migrations, or abstractions the user did not ask for?
- Is the implementation simple and readable, with avoidable nesting, pass-through wrappers, speculative abstractions, and generic helper layers removed?
- Does each new abstraction, seam, service, helper, or component earn its keep through reuse, testability, isolation, or a clear domain boundary?
- Did the implementation add a behavior-affecting variable/parameter,
  gate/threshold, retry, fallback, or compatibility branch without a current
  need, real consumer or trigger, and focused verification? If so, require the
  simpler direct path.
- Are complex branches, fallback paths, budget checks, and error paths explicit and covered by tests rather than hidden in clever conditionals?
- Does the implementation match local code style for naming, package/module placement, construction patterns, error handling, logging, import ordering, formatting, and tests?
- Does Architecture Conformance Evidence match the actual ownership,
  authoritative rule, dependency edges, public surface, failure semantics,
  abstraction cost, and cleanup in the diff?
- Did the phase preserve one authority per business rule and one owner per
  important state, without cycles, cross-module internal access, or leaked
  infrastructure models?
- Did it avoid unrelated style-only churn and mixed conventions in the same touched area?
- Does the diff include only intended files, with no secrets, temporary logs, debug code, generated private files, or unrelated formatting churn?
- Does the code use canonical terms from repository glossary/context docs when they exist?
- Does the implementation contradict any ADR without explicitly reopening that decision?
- Was the phase implemented as a reviewable vertical slice rather than disconnected horizontal work?
- If config, provider settings, feature flags, or env vars changed, were repository config files and environment docs kept consistent without exposing real secret values?
- Are public API, SSE, DTO, database, and prompt contracts consistent between backend, frontend, tests, and docs?
- Are feature flags, execution modes, budgets, retries, fallback paths, and error paths wired end to end?
- Are internal messages, traces, logs, tool arguments, prompts, and provider responses sanitized according to privacy expectations?
- Are tests strong enough to fail if the reviewed behavior regresses?
- Do tests assert behavior and payloads, not only that mocks were called?
- Are ordering-sensitive flows tested with exact order assertions?
- Are wrong-turn, wrong-session, disabled, unavailable, empty, malformed, and boundary cases covered where relevant?
- For UI changes, was rendered behavior checked locally, including browser console errors, or is the limitation explicitly documented?
- Are implementation docs updated with accurate verification results and remaining manual checks?
- Was durable, verified project knowledge or a recurring pitfall discovered? If
  so, is project-level `AGENTS.md` updated with fact, action, and evidence,
  without secrets or transient history?

## Plan-Gap Closure

When the user asks to verify whether a phase is done, close gaps, or continue from an existing plan:

- Extract each success criterion from the exact plan or implementation document path the user named.
- Check whether the current code already satisfies each criterion before recommending new implementation.
- Treat missing optional/null fields, wrong-turn streaming behavior, missing static tests, and manual-verification blockers as real gaps.
- If every criterion is satisfied, accept the phase with evidence instead of asking for unnecessary code changes.

## Finding Format

Read [references/finding-contract.md](references/finding-contract.md) before
writing any actionable finding or re-reviewing one for closure. Use its exact
required fields, per-finding Reviewer Checklist, Closure Criteria, confidence,
severity, and classification rules. Do not emit a shortened finding contract
from memory.

## Finding Re-review And Closure

When reviewing an `apply-review-fix` pass:

- Reuse the original finding ID and its exact Fix Specification, Reviewer
  Checklist, and Closure Criteria.
- Inspect the new diff for both the required repair and boundary violations.
- Mark each closure item pass/fail with file/test evidence; do not replace the
  original acceptance contract with a looser interpretation.
- Keep the finding open when any required change, acceptance item, validation,
  cleanup, or checklist item remains incomplete.
- Raise a new drift finding when the repair introduces unapproved work outside
  its `Allowed` boundary; do not silently absorb it into the old finding.
- Close the finding only when every Closure Criteria item is green. State
  `CLOSED` or `OPEN` explicitly so partial repairs cannot be mistaken for
  acceptance.

## Overall Review Format

Overall Review does not validate individual findings. Each finding's Reviewer
Checklist and Closure Criteria own that job. Overall Review only summarizes the
reviewed target, groups findings, orders repairs, reports cross-finding drift,
and gives the final recommendation.

```text
Overall Review

Reviewed Target
- Latest user goal, approved plan/phase, task branch, and diff boundary.

Blocking Fixes
- Finding IDs and short titles only, or None.

Non-blocking Fixes
- Finding IDs and short titles only, or None.

Fix Order
1. Finding ID: concrete first repair and why it precedes the next.
2. Finding ID: next repair.

Anti-Drift Summary
- All required fixes remain inside the approved target: Yes/No
- Findings proposing a new feature/provider/LLM/API/schema/dependency: None | IDs
- Findings changing phase boundaries or acceptance: None | IDs
- Cross-finding combination creates broader redesign: No | explanation

Reviewer Recommendation
ACCEPT | APPLY-REVIEW-FIX | REJECT
Reason: one sentence.

Phase Checkpoint
- NOT_APPLICABLE | CHECKPOINT_COMMITTED <hash> | CHECKPOINT_BLOCKED <reason>
```

Use `APPLY-REVIEW-FIX` only when every required finding has a fully green
proposal-level Reviewer Checklist and a bounded repair-ready specification. Use
`REJECT` when clarification, root-cause investigation, or an approved plan
change is required before safe implementation. Explain every drift exception.
Omit `Fix Order` when there are no required fixes. Never place a `Future
Enhancement` in the finding groups, repair order, or verdict.

## Acceptance Language

If accepted, say what was checked and what remains manual.

If not accepted, say which findings block acceptance and what should be fixed next.

Do not use vague repair language such as "improve handling", "add more tests",
or "consider refactoring" without the required behavior, boundary, and proof.
The fix specification is the handoff contract for `$apply-review-fix`.

Do not accept a plan, accept a phase, or tell an implementer to start when unresolved blocking Open Questions remain in either the plan or implementation document.

Do not claim full E2E coverage unless the E2E path was actually executed.

## Phase Checkpoint Gate

Run this gate only after an Implementation Review returns `ACCEPT` and the
repository policy requires an automatic commit for every completed phase. It is
not used for plan review, partial implementation, an `APPLY-REVIEW-FIX` or
`REJECT` verdict, or a user-requested no-commit run.

Before committing, require all of the following:

- every blocking Finding is `CLOSED` and no blocking Open Question remains;
- required tests, builds, manual checks, documentation, cleanup, Architecture
  Conformance Evidence, and project knowledge/pitfall updates are complete;
- current branch is the task branch recorded by the Task Branch Gate;
- the reviewed phase files can be isolated from unrelated dirty changes;
- no secrets, temporary diagnostics, generated private artifacts, or unreviewed
  changes are in the checkpoint set.

Then:

1. Stage only explicit reviewed phase paths; never use `git add -A` or
   `git add .` in a mixed worktree.
2. Inspect `git diff --cached --stat`, `git diff --cached`, and
   `git status --short` to prove the index contains exactly the accepted phase.
3. Create one focused checkpoint commit using the repository convention, or a
   fallback such as `feat(<scope>): complete <phase-id>`.
4. Report the commit hash and leave unrelated changes untouched. Do not push.

If files overlap unrelated work, ownership is ambiguous, validation became
stale, or the index cannot be isolated safely, do not commit. Report
`CHECKPOINT_BLOCKED` with the exact reason; never stash, reset, discard, weaken
the gate, or bundle unrelated changes merely to satisfy automatic commit policy.

## Skill Handoff

- If plan review is accepted and implementation is requested, use `$feature-implementer`.
- If plan review or implementation review has concrete findings, use
  `$apply-review-fix` and hand off the exact finding IDs and drift-bounded fix
  specifications. Do not add new repair scope during handoff.
- If review finds unresolved product, architecture, dependency, data, security, or acceptance decisions, return to `$feature-planner` or ask the user directly before implementation.
- If implementation is accepted, complete the Phase Checkpoint Gate when
  required before starting the next phase.
- If accepted implementation needs a module walkthrough, use `$module-introduction`.
