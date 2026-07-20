---
name: feature-planner
description: Use when turning a new, unclear, cross-module, risky, reference-based, or product-facing request into a cross-review-ready implementation plan. Enforce the task-branch gate and define stable acceptance IDs, Architecture Contracts, explicit Allowed/Not Allowed/Deferred boundaries, cleanup, tests, verification, and phase checkpoint gates before coding.
---

# Feature Planner

Use this skill before implementation when a feature request is new, unclear, cross-module, user-facing, risky, or based on another project's design.

The goal is to convert a rough idea into a clear, reviewable plan that another coding agent can implement safely.

This skill is for planning only. Do not implement code unless the user explicitly asks to continue into implementation.

## Core Rule

Do not silently decide unclear product requirements, architecture choices, API contracts, database changes, dependencies, security behavior, privacy behavior, model/provider choices, or reference-project adaptation choices.

If one of those choices is unclear and materially affects the feature, ask the user before finalizing the plan.

## Project Context

This is a generic planning skill. Do not assume a specific repository, framework, domain, documentation layout, language policy, or tech stack.

Before choosing files or naming, read the repository's local instructions and conventions:

- `AGENTS.md`, `CLAUDE.md`, or equivalent agent instructions.
- `ENGINEERING_STANDARDS.md` or the repository's equivalent architecture and
  consistency standard when present.
- README and contributor docs.
- Existing `docs/`, `tests/`, `examples/`, `schemas/`, `src/`, `app/`, `packages/`, or service-specific layouts.
- Existing naming, localization, validation, and gitignore patterns.

Generic fallback locations:

- `docs/plans/<feature-slug>.md` for feature plans.
- `docs/implementation/<feature-slug>-implementation.md` for implementation records.
- `docs/architecture/<design-slug>.md` for architecture designs.
- `docs/adr/ADR-NNN-<decision-slug>.md` for hard-to-reverse decisions.

For file and directory naming, follow repository-local standards from `AGENTS.md`, README, contributor docs, and nearby existing files.

When present and relevant, also read repository-specific context files such as:

- `CONTEXT.md`, glossary files, or domain docs for project language and canonical terms.
- `docs/adr/` for hard-to-reverse architectural decisions.
- `docs/env_variables.txt` for local environment variable names and configuration surface when a feature touches config, providers, credentials, feature flags, or runtime defaults.

Create or update glossary/context documents only when a term or decision has actually been clarified. Keep glossary files as glossaries, not implementation specs.

Treat `docs/env_variables.txt` as secret-bearing local configuration. Use it to understand variable names and config coverage, but do not quote real values in plans, logs, tests, or final responses.

## Task Branch Gate

At the start of every distinct repository task, before editing a plan or project
document:

1. Run `git status --short --branch` and `git branch --show-current`.
2. Identify the expected task branch from the latest user goal, approved plan,
   and repository naming convention. Planning, implementation, review-fix, and
   re-review for one feature stay on the same task branch.
3. Continue when the current branch is the correct task branch.
4. When the worktree is clean and the current branch is the default or an
   unrelated branch, create or switch to the task branch automatically. Use the
   repository convention; fall back to `feat/<task-slug>`.
5. When unrelated dirty changes would be carried across branches, do not stash,
   reset, discard, or silently transport them. Prefer a separate worktree from
   the intended base when safe; otherwise stop and ask the user.

Record the branch decision in the plan or handoff. Do not create a new branch
for a continuation, review, or repair of the task already represented by the
current branch.

## Source Of Truth

When information conflicts, follow this priority:

1. Latest explicit user instruction
2. Existing approved plan document
3. Existing implementation document
4. Current project code
5. Reference project behavior
6. General best practices

Do not let older documents override newer user decisions.

## Original Intent Preservation

Treat the latest explicit user goal, the original problem statement, and confirmed decisions as planning constraints.

- Do not resolve ambiguity, review feedback, or implementation difficulty by dropping, deferring, weakening, or converting a user-requested capability into an observation or warning unless the user explicitly approves that trade-off.
- When revising a plan after review, compare the change against the user's stated goal and latest decisions. If the fix changes scope, acceptance gates, phase boundaries, or user-visible behavior, ask the user before finalizing.
- If a capability is intentionally deferred, record the explicit user decision, the reason, and the phase or follow-up where it will be handled.
- A plan is not implementation-ready if it silently closes a concern by changing what the user asked for.
- After plan review begins, keep phase IDs and acceptance IDs stable. Do not
  renumber or rewrite them to hide a finding; append or explicitly supersede an
  item with the user's approval and preserve traceability.

## Clarification Gate

Ask the user before finalizing the plan if any of these are unclear:

- User problem, target user, or expected user flow
- In scope, out of scope, or deferred work
- Acceptance criteria or manual E2E expectations
- API request/response contract
- Database schema, migration, or data-retention behavior
- Authentication, authorization, privacy, or security behavior
- Async jobs, queues, schedulers, streaming, SSE, or tool-calling contracts
- New dependencies, model/provider choices, or cost-sensitive behavior
- Environment variables, local configuration, feature flags, or runtime defaults
- How closely to follow a reference project
- Rollback or backward-compatibility requirements

When clarification is required, do not produce a final plan. Return blocking questions, options, a recommendation if clear, and why user confirmation is needed.

Do not leave blocking items in `Open Questions` while also presenting the plan as implementation-ready. Any unresolved question that can affect product behavior, architecture, API, data model, permissions, dependencies, provider/model choice, UX, tests, rollout, or implementation scope must be asked to the user and resolved before implementation can start.

Do not present unresolved options as implementation-ready. If the plan includes `Option A / Option B`, alternatives, a recommendation that still needs user confirmation, or any "choose one" decision that affects implementation, ask the user to choose before coding can start. Do not let the implementer pick the option.

## Production Planning Gates

When the feature touches one of these areas, the plan must include the corresponding details instead of leaving them implicit:

- API contract: request schema, response schema, error cases, compatibility impact, and example payloads.
- Configuration and environment: variable names, defaults, required/optional status, secret boundaries, local/dev/prod differences, and `docs/env_variables.txt` update needs.
- Data or migration: schema changes, migration path, backfill needs, rollback path, and old-data compatibility.
- Security or privacy: permission checks, data exposure, logging boundaries, trace/prompt/tool/provider sanitization, and retention behavior.
- Release or rollback: feature flags, staged rollout, fallback behavior, old-client compatibility, and how to disable the feature.
- Observability: logs, metrics, health checks, audit/debug surfaces, and what must not be logged.
- Implementation simplicity: expected seams, reuse of existing patterns,
  complexity risks, and explicit non-goals for abstractions or refactors that
  should not be introduced. Do not plan a new behavior-affecting variable or
  parameter, gate or threshold, retry, fallback, or compatibility branch unless
  a current requirement or evidenced failure mode needs it and the plan names
  its real consumer or trigger and verification.
- Code style consistency: existing naming, package/module layout, DTO/type/component/test conventions, error handling, logging, formatting, and lint/type/build expectations.
- Architecture and consistency: business capability owner, behavior/state
  owner, authoritative rule location, existing and added dependency direction,
  public API impact, transaction/concurrency boundary, failure/fallback
  semantics, change-locality boundary, and cleanup of superseded authority.
- Definition of Done: tests, build/typecheck, documentation updates, review, manual E2E, and known blockers.

If one of these gates applies but cannot be specified safely, ask the user before finalizing the plan.

## Architecture Contract

For every non-trivial phase, add an `Architecture Contract` using stable rule
IDs from the repository engineering standard. If the repository has no IDs,
use descriptive labels without inventing a permanent architecture policy.

```text
Business capability and owning module
Behavior owner and state owner
Authoritative business-rule location
Existing dependency direction
Allowed new dependency edges
Forbidden dependency edges / internal surfaces
Public API and data-model impact
Transaction, concurrency, and idempotency boundary
Empty / rejection / failure / timeout / fallback semantics
Existing patterns to reuse
New abstractions or control surfaces (variables, gates, fallbacks) and
present-value justification
Change-locality boundary
Cleanup of superseded code, rules, config, tests, and docs
Verification evidence required
```

Do not use arbitrary class-size, dependency-count, or constructor-parameter
thresholds as acceptance gates. Treat them as investigation signals unless the
repository has an approved measured limit.

## Planning Workflow

1. Understand the feature goal, user problem, scope, non-goals, success criteria, and failure behavior.
2. Pass the Task Branch Gate and read repository engineering standards,
   glossary/context files, project knowledge/pitfalls in `AGENTS.md`, and
   relevant ADRs when they exist.
3. Inspect the current project before planning implementation details,
   including nearby patterns and the current authoritative implementation.
4. Inspect any reference project separately and identify reusable ideas versus incompatible assumptions.
5. Compare requested behavior with current project support.
6. Define in-scope, out-of-scope, deferred, assumptions, and constraints.
7. Assign stable IDs to testable acceptance criteria for success, failure,
   boundary, permission, privacy, persistence, API, UI, SSE, prompt, tool, or
   agent contracts as relevant.
8. Design the Architecture Contract plus backend, frontend, data, API,
   prompt/tool/SSE, validation, error handling, logging, observability, and test
   strategy.
9. Split implementation into small vertical phases with explicit Allowed, Not
   Allowed, Deferred, Cleanup, prerequisite, and acceptance-ID mappings.
10. Create or update the planning and implementation documents.

## Review Handoff Contract

Before sending a non-trivial plan to `$cross-review`, ensure it exposes:

- latest user goal and confirmed decisions;
- stable phase and acceptance IDs;
- Allowed / Not Allowed / Deferred boundaries for each phase;
- prerequisites and checkpoint expectations;
- files/surfaces, tests, verification, cleanup, risks, and rollback;
- Architecture Contract rule IDs and evidence expectations;
- task branch decision and the required post-acceptance checkpoint commit;
- unresolved questions only when explicitly non-blocking/deferred.

Treat the review recommendation as a gate:

- `ACCEPT`: the approved phase may move to `$feature-implementer` when the user
  asks.
- `APPLY-REVIEW-FIX`: send the exact Finding IDs and Fix Specifications to
  `$apply-review-fix`, then rerun `$cross-review`.
- `REJECT`: resolve clarification/root-cause/plan decisions before any
  implementation.

Do not make a reviewed plan appear accepted by changing its scope, phase
boundary, or acceptance criteria after the review. Material changes require a
new explicit user decision and another cross-review.

## Project Knowledge Handoff

When planning reveals a durable, verified repository fact or recurring pitfall
that future tasks need to know, update the project-level `AGENTS.md` knowledge
ledger in the same planning phase. Record the fact, required action, and
evidence location. Do not record secrets, raw payloads, temporary failures,
speculation, or feature-specific history that belongs in the plan or
implementation document. Consolidate an existing entry instead of duplicating
it, and remove or supersede stale guidance when evidence changes.

## Skill Handoff

After producing an implementation-ready plan, route the next step deliberately:

- Use `$cross-review` for plan review before implementation when the work is non-trivial, risky, cross-module, or user-facing.
- Use `$apply-review-fix` if plan review returns concrete findings.
- Use `$feature-implementer` only after blocking Open Questions are resolved,
  the latest review recommendation is `ACCEPT`, and blocking Finding IDs are
  `CLOSED`.

Do not continue into implementation from this skill unless the user explicitly asks and the Open Questions gate is clear.

## Phase Template

Each implementation phase should include:

- Stable phase ID
- Goal
- Allowed / in-scope files, surfaces, and behavior
- Not Allowed / explicit non-goals for this phase
- Deferred work with owning phase/follow-up
- Prerequisite phases, decisions, reviews, and checkpoint commits
- Task branch and checkpoint commit expectation
- Architecture Contract and applicable engineering-standard rule IDs
- Files or modules likely to change
- Deliverables
- Stable acceptance criteria IDs mapped to deliverables
- Tests to add or update
- Verification commands
- Cleanup obligations and stale-reference checks
- Risks or manual checks

Prefer tracer-bullet vertical slices: each phase should deliver a narrow but complete behavior through the needed layers. Avoid horizontal phases such as "all backend first" or "all frontend later" unless the phase is explicitly infrastructure-only.

Avoid mixing broad refactoring with feature delivery.

Use repository conventions for IDs when they exist; otherwise use stable labels
such as `AC-001` and `PHASE-02`. IDs are references, not priorities, and must not
change merely because criteria are reordered.

## Plan Document Template

The plan document should include:

- Product summary
- Goals and non-goals
- Confirmed decision ledger
- User flow
- Scope and deferred work
- Stable acceptance criteria IDs
- Current project findings
- Domain language or ADR impact
- Reference project findings, if any
- Reference adaptation matrix, if a reference project is provided
- Production planning gates that apply
- Configuration / environment variables, if relevant
- Implementation simplicity constraints
- Code style constraints
- Architecture Contract
- Technical design
- Implementation phases with Allowed / Not Allowed / Deferred boundaries,
  prerequisites, acceptance-ID mappings, and cleanup obligations
- Test strategy
- Definition of Done
- Risks
- Open questions

The implementation document should include:

- Phase checklist
- Review status and accepted plan/phase reference
- Task branch decision
- Architecture Conformance Evidence keyed by repository rule IDs
- Finding ledger with `OPEN | READY_FOR_REVIEW | CLOSED | BLOCKED | INVALID`
- Files changed
- Decisions made
- Tests added or updated
- Verification commands
- Known failures
- Manual checks
- Review history
- Acceptance-ID evidence, boundary audit, cleanup evidence, and Closure Criteria
  status for review-fix passes
- Deferred items

Do not create or leave blocking `Open Questions`, `Open Decisions`, `Options`, `Alternatives`, `TBD`, or `To Clarify` in the implementation document while presenting the feature or phase as ready to implement. Any unresolved item in the implementation document that can affect the current phase must be clarified with the user first, answered by a newer explicit decision, or explicitly marked non-blocking/deferred.

Do not mark manual E2E checks as complete unless they were actually completed.

## Open Questions

Use `Open Questions` only to expose unresolved decisions honestly.

- If an Open Question is blocking, stop and ask the user instead of finalizing the plan.
- If the user answers an Open Question, move the answer into the relevant Decisions or Confirmed Decisions section and remove it from Open Questions.
- If an Open Question is non-blocking or deferred, label it as non-blocking/deferred and explain why implementation can safely proceed without it.
- Treat unresolved `Options`, `Alternatives`, `Decision Needed`, `To Clarify`, `TBD`, or `choose one` sections as blocking Open Questions when they affect the current feature or phase.
- An implementation-ready plan should have `Open Questions: None` or only explicitly non-blocking/deferred items.

## Reference Adaptation Matrix

If a reference project is provided, include a matrix that states which reference decisions should be adopted, adapted, reimplemented, rejected, or deferred.

Use this template:

| Reference Area | Reference Design / Behavior | Current Repository State | Decision | Reason |
|---|---|---|---|---|
| API contract |  |  | Adopt / Adapt / Reimplement / Reject / Defer |  |
| Data model |  |  | Adopt / Adapt / Reimplement / Reject / Defer |  |
| UI behavior |  |  | Adopt / Adapt / Reimplement / Reject / Defer |  |
| Dependency / library |  |  | Adopt / Adapt / Reimplement / Reject / Defer |  |
| Security / permission |  |  | Adopt / Adapt / Reimplement / Reject / Defer |  |

Use `Adopt` only when the reference behavior fits the repository without changing project architecture or user-approved scope. Use `Adapt` when the idea is useful but must follow repository conventions. Use `Reimplement` when the behavior is needed but the reference code or design should not be copied. Use `Reject` when it conflicts with the repository. Use `Defer` when it is useful but outside the current phase.

## Output Format

When no clarification is needed, respond with:

- Product Summary
- Current Understanding
- Confirmed Decision Ledger
- Assumptions
- Scope
- Current Project Findings
- Domain Language / ADR Impact
- Reference Project Findings, if relevant
- Reference Adaptation Matrix, if relevant
- Production Planning Gates
- Configuration / Environment Variables, if relevant
- Implementation Simplicity Constraints
- Code Style Constraints
- Architecture Contract
- Stable Acceptance Criteria
- Technical Design
- Implementation Phases With Boundaries And Prerequisites
- Files / Docs to Create or Update
- Definition of Done
- Risks
- Open Questions, which must be `None` or explicitly non-blocking/deferred for implementation-ready plans
- Recommended Next Step

If unresolved blocking questions remain, do not present the plan as final.
