# Finding Contract Reference

## Contents

- Finding template
- Checklist and closure behavior
- Repair confidence
- Severity and classification

## Finding Template

Every actionable finding must be repair-ready when evidence supports it, or
explicitly investigation-ready when confidence is `LOW`, while remaining inside
the approved scope.

```text
[P1][Spec|Standards/Architecture|Standards/Consistency|Standards/Simplicity] Short title
Classification: Blocking Fix | Non-blocking Fix
Evidence: path:line and the requirement/criterion it violates
Rule IDs: repository engineering-standard IDs, or `None` for a pure Spec finding

Issue
Observable behavior or concrete plan gap.

Impact
Why it matters to the approved goal, runtime, user, data, or acceptance gate.

Root Cause
Confirmed cause, or `Inferred` with the evidence still needed.

Fix Specification
Required Change
- Exact behavior/document change required to close the finding.

Minimal Fix
- Smallest sufficient implementation and why broader redesign is unnecessary.

Files / Surfaces
- Exact likely files, plan sections, contracts, tests, or prompts.

Implementation Boundary
- Allowed: surfaces that may change.
- Not Allowed: adjacent behavior/modules/contracts that must remain unchanged.
- Deferred: related work for another phase or feature.

Acceptance
- Observable conditions that close the finding.

Validation
- Tests to add/update and commands or manual checks to run.

Cleanup
- Obsolete code, prompt text, config, tests, comments, or TODOs to remove.

Regression Risk
- Likely regression and the test/guard that contains it.

Future Enhancement
- Optional only; never part of the required fix or verdict unless approved.

Repair Confidence
HIGH | MEDIUM | LOW, with one-sentence evidence.

Reviewer Checklist
Root Cause
- [x] Actual root cause is confirmed by evidence.

Minimal Fix
- [x] Proposal is the smallest sufficient repair.
- [x] No redesign or speculative abstraction is introduced.

Boundary
- [x] Allowed surfaces are explicit.
- [x] Prohibited surfaces are explicit.
- [x] Related future work is explicitly deferred.

Architecture / Consistency
- [x] Applicable repository rule IDs and local conventions are identified, or
  `N/A` is justified.
- [x] Proposal preserves ownership, authority, dependency direction, public
  surface, and failure semantics, or explicitly restores the violated item.

Validation
- [x] Required regression tests are named.
- [x] Verification commands or manual checks are named.

Cleanup
- [x] Obsolete code/tests/config/prompts/comments are identified, or `None` is
  justified.

Drift
- [x] Fix does not expand the current phase or user goal.
- [x] Fix adds no unapproved feature, provider, or LLM call.
- [x] Fix does not modify unrelated modules.

Plan
- [x] Fix matches the approved plan and latest user decision.
- [x] Fix does not weaken or rewrite acceptance criteria.

Confidence
- [x] Repair confidence and remaining assumptions are explicit.

Closure Criteria
This finding can close only when:
- [ ] Required Change is fully implemented.
- [ ] Every Acceptance item is satisfied.
- [ ] Every Validation item passes and evidence is recorded.
- [ ] Cleanup is complete.
- [ ] Re-review confirms every Reviewer Checklist item remains green.
```

For a simple P3 documentation/style finding, keep fields compact. Never omit
`Minimal Fix`, `Implementation Boundary`, `Acceptance`, `Validation`,
`Reviewer Checklist`, or `Closure Criteria`. Use `Cleanup: None` or
`Future Enhancement: None` when applicable.

## Checklist And Closure Behavior

Complete the Reviewer Checklist independently for every finding. Each check is
an evidence-backed claim, not boilerplate. Use `N/A - reason` only when it does
not apply. If a proposal-quality item cannot be checked, continue root-cause
analysis; when missing evidence requires user/external input, recommend
`REJECT` instead of handing an immature repair to `$apply-review-fix`.

Leave Closure Criteria unchecked on initial review. On re-review, update each
item from actual diff, test, cleanup, and documentation evidence. Never close a
finding because only the main code change landed.

## Repair Confidence

- `HIGH`: evidence and root cause are confirmed; no extra product decision is
  needed.
- `MEDIUM`: the repair is bounded, but the fixer must verify one stated
  assumption before editing.
- `LOW`: root cause or safe repair is unresolved. Require bounded investigation
  or clarification, leave the unresolved checklist visible, and recommend
  `REJECT` until the specification is mature.

Do not over-specify a class, algorithm, or file when evidence does not support
it. Concrete means executable and bounded, not falsely certain.

## Severity And Classification

- `P1`: blocks acceptance; likely runtime bug, data/privacy issue, broken
  contract, or plan-critical behavior missing.
- `P2`: should fix before merge; important test gap, edge-case bug, or meaningful
  plan drift.
- `P3`: cleanup, documentation accuracy, minor hardening, or non-blocking
  coverage improvement.

Severity measures impact on the approved target, not enhancement value.

- `Blocking Fix`: required for the reviewed acceptance contract.
- `Non-blocking Fix`: real in-scope defect or cleanup that does not block the
  current acceptance decision.
- `Future Enhancement`: outside the approved target; not a finding or repair
  order item.
