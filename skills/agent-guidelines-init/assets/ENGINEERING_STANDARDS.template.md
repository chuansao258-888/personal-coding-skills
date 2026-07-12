# <PROJECT_NAME> Engineering Standards

This document is the canonical code-quality, architecture, consistency, and
verification standard for <PROJECT_NAME>. Plans, implementations, reviews, and
review fixes cite its stable rule IDs instead of copying or paraphrasing the
rules into multiple documents.

## Contents

- [Project Profile](#project-profile)
- [Precedence And Compliance](#precedence-and-compliance)
- [Clean Code And Readability](#clean-code-and-readability)
- [Logic And State](#logic-and-state)
- [Simplicity And Abstraction](#simplicity-and-abstraction)
- [Architecture And Boundaries](#architecture-and-boundaries)
- [Consistency](#consistency)
- [Errors And Resilience](#errors-and-resilience)
- [Testing And Verification](#testing-and-verification)
- [Security, Privacy, And Observability](#security-privacy-and-observability)
- [Documentation And Change Hygiene](#documentation-and-change-hygiene)
- [Evidence](#evidence)
- [Language-Specific Profile](#language-specific-profile)
- [Mandatory Decision Gates](#mandatory-decision-gates)

## Project Profile

- Purpose: <PROJECT_PURPOSE>
- Primary languages and formats: <LANGUAGES_AND_FORMATS>
- Required validation commands: <VALIDATION_COMMANDS>
- Shared or local policy: <TRACKING_POLICY>

Replace every placeholder with repository evidence. Remove language-specific
sections that do not apply and add concrete rules for the detected stack. Do not
leave template instructions in a finalized project standard.

## Precedence And Compliance

When instructions conflict, use this order:

1. Latest explicit user decision
2. Accepted plan and phase contract
3. Accepted architecture decision record
4. This standard
5. Existing local convention
6. General preference

Every non-trivial plan must cite applicable rule IDs in an Architecture
Contract. Implementations must provide Architecture Conformance Evidence.
Reviews must cite the violated rule IDs. A justified exception must state its
scope, reason, risk, and verification; never silently weaken a rule.

## Clean Code And Readability

### CLEAN-01 Readable Control Flow

- Prefer guard clauses and early returns when they make the main path easier to
  read.
- Keep the happy path visible and keep failure or rejection branches explicit.
- Avoid unnecessary `else` blocks after an unconditional return, throw, break,
  or continue.
- Do not hide business flow in nested callbacks, nested ternaries, reflection,
  metaprogramming, or generic pipelines without a demonstrated need.
- Treat nesting deeper than three logical levels as a review signal, not an
  automatic failure. Simplify it or explain why the nested structure represents
  the domain more clearly.

Evidence: changed control-flow paths, complexity reduction, and tests for the
important branches.

### CLEAN-02 Cohesive Functions, Classes, And Modules

- Give each function, class, and module one coherent responsibility and one
  primary reason to change.
- Keep related state, invariants, and rules close enough to understand locally.
- Split code by behavior or boundary, not by arbitrary line-count targets.
- Do not extract a helper that merely renames one expression or forwards every
  argument unchanged.
- A local requirement should change the smallest coherent set of files.

Evidence: responsibility statement, callers, owned state, and why each changed
unit belongs in the same capability.

### CLEAN-03 Meaningful Naming And Domain Vocabulary

- Use names that describe business meaning, outcome, or role rather than
  implementation trivia.
- Avoid context-free names such as `data`, `info`, `temp`, `item`, `manager`,
  `handler`, `helper`, `process`, or `doWork` unless the surrounding scope makes
  the meaning unambiguous.
- Name booleans as questions or predicates, such as `isReady`, `hasAccess`,
  `canRetry`, or `shouldPersist`.
- Use one canonical term for the same concept across code, API, persistence,
  events, tests, logs, and documentation.
- Do not encode temporary sequence numbers, author names, or `final`/`new`/`old`
  suffixes into durable names.

Evidence: nearby naming conventions and terminology sources followed.

### CLEAN-04 Comments Explain Why

- Use comments for intent, invariants, constraints, non-obvious trade-offs,
  protocol quirks, and safety reasoning.
- Do not restate what readable code already says.
- Prefer a better name or a smaller coherent function over a comment that
  compensates for unclear code.
- Update or remove comments when behavior changes.
- Do not keep commented-out code, temporary debug notes, or ownerless TODOs.
- Public documentation comments must describe observable contracts, not private
  implementation steps that can drift.

Evidence: comments remain necessary after the code is read without them.

### CLEAN-05 Explicit Data Transformations

- Make validation, normalization, mapping, unit conversion, and defaulting
  visible at the boundary where they occur.
- Avoid chains of nearly identical DTOs or maps when no boundary semantics are
  added.
- Preserve field meaning, units, nullability, versioning, and error semantics
  across transformations.
- Name lossy conversion, truncation, clamping, fallback, and redaction directly.

Evidence: input-to-output mapping and round-trip or boundary tests.

### CLEAN-06 Complexity Signals Are Not Mechanical Quotas

- Treat long functions, high nesting, many parameters, large constructors, and
  high dependency counts as prompts to inspect responsibility.
- Do not fail code only because it crosses an arbitrary size threshold unless
  the repository has an approved, measured limit.
- Prefer a readable cohesive unit over mechanical fragmentation into tiny
  pass-through methods.
- Record why unavoidable complexity exists and protect it with focused tests.

Evidence: complexity delta and the simpler alternatives considered.

## Logic And State

### LOGIC-01 One Authoritative Rule And State Owner

- Every important business rule has one authoritative implementation.
- Every mutable state and transition has one explicit owner.
- Other modules call behavior-oriented contracts instead of reproducing rules
  or mutating internal state directly.
- A replacement removes or delegates the superseded path so two authorities
  cannot drift.

Evidence: owner, authoritative method or policy, callers, and stale-rule search.

### LOGIC-02 Distinguish Outcomes

Keep these outcomes distinguishable when relevant:

- legal empty result
- business rejection
- malformed or invalid input
- internal failure
- external dependency failure
- timeout or cancellation
- concurrency conflict
- deliberate degradation

Do not collapse different meanings into `null`, `false`, an empty collection,
or a generic success response.

Evidence: types or contracts representing each outcome and tests for boundary
cases.

### LOGIC-03 Preserve Ordering, Invariants, And Atomicity

- State required operation order and invariants close to the authoritative code.
- Identify which operations are atomic and which external effects occur outside
  the transaction.
- Do not rely on UI duplicate prevention or "normally once" execution when
  duplicate or concurrent work has real impact.
- Use the simplest mechanism that satisfies the risk: constraint, version,
  idempotency key, state transition, lock, compare-and-set, outbox, or
  compensation.

Evidence: transaction or concurrency boundary, failure window, and tests.

## Simplicity And Abstraction

### SIMP-01 Minimal Correct Change

- Make the smallest complete change inside the accepted boundary.
- Prefer direct, linear, named control flow.
- Do not broaden a feature into a refactor, framework, migration, or future
  roadmap item.
- Small local duplication is preferable to a false shared abstraction.
- Remove obsolete branches, configuration, tests, and comments replaced by the
  change.

Evidence: allowed diff, non-goals, cleanup, and avoided adjacent changes.

### SIMP-02 New Abstractions Must Earn Their Keep

Before adding an interface, factory, strategy, adapter, bridge, registry,
pipeline, context, base class, generic helper, cache, retry, fallback, or
compatibility layer, record:

1. the current problem it solves;
2. the real variation or boundary;
3. current implementations and callers;
4. the concrete cost of a direct implementation;
5. why the abstraction is easier to understand and verify now.

"It may be useful later" is not sufficient.

### SIMP-03 Avoid Hidden Coupling And Generic Containers

- Do not create God services, global mutable contexts, generic business
  managers, or dumping-ground utility modules.
- Prefer composition over inheritance.
- Put code in shared/common/core only when its contract is stable and genuinely
  cross-capability.
- Make dependencies explicit rather than retrieving them through globals or
  unrelated service locators.

Evidence: responsibility, dependency direction, and actual consumers.

## Architecture And Boundaries

### ARC-01 Capability Cohesion And Change Locality

- Organize code around a clear capability and change reason.
- Keep a change within the smallest coherent module set.
- Do not scatter one behavior across generic controller/service/repository/helper
  folders without a real boundary.

### ARC-02 Dependency Direction And Acyclicity

- Follow the repository's established dependency direction.
- Domain behavior must not depend on HTTP, database, MQ, provider SDK, UI, or
  framework implementation details.
- Do not access another capability's internal repository or storage model.
- Do not introduce module, service, or package cycles.

### ARC-03 Stable Boundaries And Information Hiding

- Collaborate through the smallest stable contract that expresses intent.
- Use the narrowest practical visibility.
- Do not leak persistence entities, provider SDK models, internal prompts, or
  transport details across capability boundaries.
- Every layer and conversion must add protocol translation, orchestration,
  rules, permission, transaction ownership, or infrastructure isolation.

Evidence: public surface and the value of every added hop.

## Consistency

### CONS-01 Follow Local Conventions

- Match naming, layout, construction, dependency injection, DTO/type, exception,
  logging, null handling, import, formatting, and test conventions in the
  touched area.
- Do not mix a style migration or unrelated formatting into feature work.
- When local conventions conflict, use the closest maintained code and document
  the choice.

### CONS-02 Keep Contracts Consistent Across Surfaces

- Keep API, DTO, event, SSE, database, prompt/tool, configuration, tests, and
  documentation consistent end to end.
- When configuration changes, update defaults, environment documentation,
  validation, and tests together without exposing secret values.
- Preserve one term and one semantic meaning across producer and consumer.

## Errors And Resilience

### ERR-01 Validate At Boundaries

- Validate untrusted or external input before domain, provider, model, tool, or
  persistence calls.
- Return or raise an outcome that preserves the cause category.
- Include actionable context without exposing secrets or sensitive payloads.

### ERR-02 Do Not Hide Failures

- Do not catch broad exceptions and silently convert them to empty success,
  `null`, or a default value.
- Log at the boundary that can add meaningful context; avoid duplicate stack
  traces at every layer.
- Preserve cancellation and interruption semantics.

### ERR-03 Resilience Must Be Deliberate

- Every fallback, retry, cache, default, circuit breaker, and degradation path
  needs an explicit trigger, limit, outcome, observability signal, and test.
- Do not add resilience behavior merely because a failure can be imagined.
- State whether retries are safe and how duplicate effects are prevented.

## Testing And Verification

### TEST-01 Test Observable Behavior

- Prefer public interfaces, user-visible behavior, and stable contracts.
- Verify payloads, ordering, state transitions, and failure semantics, not only
  that a mock was called.
- Keep tests deterministic and independent from real secrets or uncontrolled
  external systems.

### TEST-02 Cover Boundaries And Regressions

- Cover success, legal empty, invalid, boundary, disabled, unavailable,
  timeout, cancellation, concurrency, and failure cases when relevant.
- A behavioral bug fix should include a regression test that fails without the
  fix whenever a stable seam exists.
- Test defaults, missing values, invalid values, and overrides when
  configuration changes.

### TEST-03 Verify From Narrow To Broad

Run, in order where applicable:

1. targeted tests for changed behavior;
2. relevant module or integration suites;
3. lint, format, typecheck, and build;
4. manual UI or runtime checks;
5. final diff, secret, debug, and stale-reference inspection.

Record checks actually run. Never claim a manual or live check that was not
performed.

## Security, Privacy, And Observability

### SEC-01 Protect Secrets And Sensitive Data

- Never commit or log API keys, tokens, credentials, private connection values,
  raw user data, prompts, tool arguments, or provider payloads.
- Use environment variable names and redacted examples in documentation.
- Enforce authentication, authorization, tenant, and resource boundaries at
  every externally reachable path.
- Review both success and failure logs for accidental data exposure.

### OBS-01 Make Important Outcomes Observable

- Log or measure decisions that operators need to diagnose without exposing
  sensitive content.
- Use stable event names and useful identifiers.
- Distinguish rejection, timeout, retry, degradation, and internal failure.
- Remove temporary diagnostics before handoff.

## Documentation And Change Hygiene

### DOC-01 Keep Documentation Paired With Behavior

- Update architecture, schema, configuration, workflow, and module documents in
  the same change as behavior.
- Keep every required language version synchronized.
- Mark planned, historical, cancelled, diagnostic, and unverified work
  honestly.

### CHANGE-01 Cleanup Is Part Of The Change

- Remove superseded code, duplicate rules, dead branches, stale configuration,
  obsolete tests, comments, and TODOs.
- Search for stale names and references before handoff.
- Preserve unrelated user changes and avoid unrelated formatting churn.

### CHANGE-02 Keep Git Changes Reviewable

- Inspect branch and worktree status before editing.
- Stage only explicit reviewed paths in a mixed worktree.
- Use one focused commit for an accepted phase when repository policy requires
  it.
- Do not stash, reset, discard, force-push, or bundle unrelated work to satisfy
  a workflow gate.

## Evidence

### EVID-01 Evidence Is Required At Every Gate

Plans record applicable rule IDs and required proof. Implementations record
actual ownership, dependency, public/data, transaction, error, complexity,
cleanup, and verification evidence. Reviews check those claims against the
diff, code, tests, and runtime results.

A checkbox without a file, diff, command, test, or runtime artifact is not
proof.

## Language-Specific Profile

Replace this section with rules supported by the detected repository. Keep only
applicable languages and formats. Examples of useful topics include:

- Java/Kotlin: exceptions, nullability, streams, dependency injection,
  transactions, records/data classes, and test conventions.
- TypeScript/JavaScript: strict types, `unknown` vs `any`, async errors,
  component/hook boundaries, effects, and runtime validation.
- Python: type hints, context managers, exception scope, mutable defaults,
  pathlib, dependency boundaries, and test fixtures.
- PowerShell: `$ErrorActionPreference`, `-LiteralPath`, exit codes, pipeline
  behavior, and safe filesystem operations.
- Markdown/YAML/JSON: stable headings, relative links, schema/manifest authority,
  formatting, and paired-language rules.

Do not invent framework rules that the repository does not use.

## Mandatory Decision Gates

Before editing, answer:

1. Where does this behavior belong and who owns its state?
2. Does an authoritative rule or real abstraction already exist?
3. What branches, dependencies, states, transactions, fallbacks, and public
   surfaces will the change add?
4. What can be removed or implemented more directly?
5. Which rule IDs and tests prove the change is readable, correct, and scoped?

Before handoff, verify:

- the main path is readable and avoidable nesting is gone;
- names, comments, errors, data models, and tests follow local conventions;
- ownership, dependency direction, and public surfaces remain clear;
- failure and fallback semantics are explicit;
- superseded code and temporary diagnostics are removed;
- targeted and broader verification evidence is recorded.
