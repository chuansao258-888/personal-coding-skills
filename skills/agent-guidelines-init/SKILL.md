---
name: agent-guidelines-init
description: Initialize repository Git when absent, audit local AI-coding ignore rules, generate or merge an English ENGINEERING_STANDARDS.md with stable Clean Code rule IDs, and create or update repository-level AGENTS.md guidance. Use for repository setup, code readability and cleanliness standards, project knowledge/pitfall ledgers, task-branch gates, accepted-phase commits, review closure, documentation pairing, git hygiene, or skill routing.
---

# Agent Guidelines Init

Use this skill to create or update `ENGINEERING_STANDARDS.md` and `AGENTS.md` in
the current repository. The output should make the repository self-describing
for future coding agents and contributors.

This skill is an initializer, not a daily workflow tool. It keeps detailed,
stable code-quality rules in `ENGINEERING_STANDARDS.md` and operational project
guidance in `AGENTS.md`; later planner, implementer, reviewer, and fixer skills
read both as local sources of truth.

## Core Rules

- Inspect the repository before writing. Do not generate a generic template blindly.
- Preserve existing useful `AGENTS.md` rules and merge changes instead of overwriting them.
- Keep operational project guidance in `AGENTS.md`; keep detailed code-quality,
  readability, logic, architecture, testing, and change rules in one canonical
  `ENGINEERING_STANDARDS.md`.
- When no canonical standard exists and the repository contains code, scripts,
  schemas, automation, or a non-trivial engineering workflow, create one from
  [the English template](assets/ENGINEERING_STANDARDS.template.md).
- Treat a shared, public, or team engineering standard as tracked repository
  policy by default. Ignore it only when the user or repository explicitly
  classifies it as personal local guidance.
- Never duplicate the full standard in `AGENTS.md`, plans, or global skills.
  Those surfaces cite stable rule IDs and record task-specific evidence.
- Do not add local `.agents/skills` unless the user explicitly asks for project-local skills.
- If the repository policy says completed phases must be committed, include that rule in `AGENTS.md`; still do not push or open PRs unless the user explicitly asks.
- Keep secrets, private config values, local tokens, and raw sensitive payloads out of the file.

## Repository Initialization Gate

Run this gate before repository discovery, whether `AGENTS.md` already exists or
not.

1. Resolve the user-selected target directory and run
   `git rev-parse --show-toplevel` from it.
2. If the command succeeds, use the returned repository/worktree root. Do not
   initialize a nested repository merely because the target is a subdirectory.
3. If the command proves that no containing repository exists, run `git init`
   automatically in the target directory, then verify with
   `git rev-parse --show-toplevel` and `git status --short --branch`.
4. Do not set a remote, create an initial commit, change global/local Git config,
   or rewrite the default branch as part of initialization.
5. If Git is unavailable, permissions prevent initialization, or the target
   directory is ambiguous, stop and report the exact blocker instead of
   pretending initialization succeeded.

After this gate, always run the AI Coding Gitignore Gate. Newly initialized and
pre-existing repositories follow the same ignore audit.

## AI Coding Gitignore Gate

Ensure the repository root has a `.gitignore`. Preserve its order and existing
rules; append one labeled block only for missing coverage. Treat an existing
broader pattern as coverage instead of duplicating a narrower pattern.

Default local AI-coding baseline:

```gitignore
# Local AI coding workflow files
.agents/
.claude/
.zcode/
.agent-workflow/
.codex/
AGENTS.md
CLAUDE.md
GEMINI.md
CONTEXT.md
```

Also scan for present local tool-state paths such as `.cursor/`, `.windsurf/`,
`.continue/`, `.aider.conf.yml`, `.aider.chat.history.md`, and
`.aider.input.history`. Add an exact ignore pattern when the path is local and
untracked. Do not blanket-ignore `.github/`, `docs/`, source prompts,
or explicitly shared/tracked AI rules.

Before editing `.gitignore`, compare candidate paths with `git ls-files`:

- Adding an ignore rule does not untrack a file already in the index.
- Never run `git rm --cached`, delete, move, or rewrite a tracked AI instruction
  file unless the user explicitly requests that repository policy change.
- Report tracked exceptions so the user knows which AI files remain shared.

Verify directory rules with probe paths and file rules directly, for example:

```powershell
git check-ignore -v --no-index .agents/__probe__
git check-ignore -v --no-index .codex/__probe__
git check-ignore -v --no-index AGENTS.md
```

The gate passes only when every baseline path is covered by `.gitignore` or is
reported as an intentional tracked exception, and each detected local tool-state
path is either ignored or reported as intentionally shared.

Handle `ENGINEERING_STANDARDS.md` separately: a shared standard must not be
ignored; an explicitly local standard must have a verified ignore rule.

## Engineering Standards Creation Gate

Run this gate after repository discovery and before generating `AGENTS.md`.

1. Search for an existing canonical engineering, coding-style, architecture,
   or contributor standard and identify whether it is tracked, shared, or local.
2. If `ENGINEERING_STANDARDS.md` or an equivalent canonical standard exists,
   preserve its stable IDs and project-specific rules. Merge only evidenced
   missing coverage; never replace the file with the template wholesale.
3. If no canonical standard exists and the repository contains code, scripts,
   schemas, automation, or a non-trivial engineering workflow, copy
   `assets/ENGINEERING_STANDARDS.template.md` to the repository root as
   `ENGINEERING_STANDARDS.md`.
4. Replace every template placeholder from repository evidence. Keep the core
   Clean Code rule IDs stable, remove language sections that do not apply, and
   add concrete language/framework rules for the detected stack.
5. Ensure the standard covers readable control flow, low nesting, cohesive
   responsibilities, meaningful naming, useful comments, explicit logic and
   outcomes, minimal abstractions, errors, tests, security, documentation,
   cleanup, and verification evidence. Require a current need, real consumer or
   trigger, and focused verification for every added variable/parameter,
   gate/threshold, retry, fallback, or compatibility branch.
6. Track the standard when it is intended for contributors, a team, a public
   repository, or CI. Ignore it only when the user explicitly wants personal
   local policy; record that decision in `AGENTS.md`.
7. Make `AGENTS.md` point to the repository-local canonical file and require
   planners, implementers, reviewers, and fixers to cite its stable rule IDs.
8. Verify that no placeholder remains, rule IDs are unique, relative links are
   valid, and the selected language profile matches actual repository files.

Do not make a target repository depend on the installed skill's asset path at
runtime. The asset is a generation source; the repository-local standard is the
authoritative output.

## Discovery

After repository initialization and the AI-coding ignore audit, inspect:

```powershell
git status --short --branch
rg --files
```

Read available project context:

- Existing `AGENTS.md`, `CLAUDE.md`, or equivalent.
- Existing `ENGINEERING_STANDARDS.md`, architecture standards, or contributor
  policies with stable rule IDs.
- `README.md` and localized README files.
- Contributor docs, package manifests, build files, lockfiles, test config, lint config, formatter config, and CI files.
- Existing `docs/`, `schemas/`, `examples/`, `tests/`, `src/`, `app/`, `packages/`, or service directories.
- `.gitignore` and ignored local artifact patterns.
- ADRs or architecture docs when present.

Infer commands only from project files or docs. If a build/test command is uncertain, label it as absent instead of inventing it.

## AGENTS.md Structure

Use this structure unless the repository already has a strong existing pattern:

1. `# Repository Guidelines`
2. `## Project Context`
3. `## Project Structure`
4. `## Project Knowledge & Pitfalls`
5. `## Development Workflow`
6. `## Goal-Oriented Workflow`
7. `## Branch And Phase Checkpoint Policy`
8. `## Build, Test, and Local Checks`
9. `## Skill Routing & Development`
10. `## Coding Style & Naming`
11. `## Testing Guidelines`
12. `## Documentation Rules`
13. `## Repository Standards`
14. `## Gitignore & Local Files`
15. `## Git Hygiene`

Omit or compress sections that do not apply. Keep the file concise but specific enough that another agent can work safely.

## Required Content

Include the repository's actual:

- Main purpose and current status.
- Important docs or ADRs to read before planning or editing.
- Directory map for source, tests, docs, schemas, examples, assets, generated outputs, and local artifacts.
- Build, test, lint, format, schema, or validation commands that exist.
- A pointer to the canonical `ENGINEERING_STANDARDS.md`, its tracking policy,
  and the stable rule IDs that later workflow skills must cite.
- A concise operational summary of coding style, naming, framework, testing,
  and file-placement rules; keep the full rule text in the canonical standard.
- Testing conventions and minimum verification before handoff.
- Documentation localization or pairing rules when the repo has them.
- A rule that project documents must be updated in every required language when the repository has bilingual or localized documentation.
- A rule that architecture, schema, pipeline, agent behavior, evaluation, or workflow changes must update the corresponding Markdown documentation in the same phase.
- Rules for generated outputs, scratch files, caches, private notes, and `.gitignore`.
- Repository-initialization and AI-coding-ignore status: whether `git init` was
  required, which baseline patterns are covered, and which tracked AI files are
  intentional shared exceptions.
- Git behavior: inspect status first, preserve unrelated user changes, commit after completed phases when the repository policy requires it, and no push/PR unless asked.
- Task-branch behavior: at every distinct task start, verify the expected branch;
  automatically create/switch when safe; keep review/fix on the same task branch;
  never stash, reset, discard, or carry unrelated dirty changes silently.
- Automatic phase checkpoints: after implementation cross-review returns
  `ACCEPT`, stage only explicitly reviewed phase paths, inspect the staged diff,
  create one focused commit, report its hash, and leave unrelated changes
  untouched. Never auto-commit before acceptance or auto-push.
- A project knowledge/pitfall ledger in project-level `AGENTS.md`: future tasks
  read it at startup; phases update only durable verified facts, recurring
  traps, required actions, and evidence locations; exclude secrets, raw logs,
  speculation, transient failures, and feature history.
- Open-question policy: do not start implementation while the plan or implementation document contains unresolved blocking Open Questions, Options, TBDs, or unconfirmed decisions.
- Review-closure policy: preserve Finding IDs and boundaries; run
  `$apply-review-fix` only for repair-ready findings; rerun `$cross-review` until
  Closure Criteria are green and the recommendation is `ACCEPT`.
- Phase-entry policy: do not start a planned phase while review recommends
  `APPLY-REVIEW-FIX`/`REJECT`, a blocking Finding is OPEN, or a required prior
  phase checkpoint is missing.
- Skill routing: explain which reusable skills to call for initialization, planning, review, review-fix, implementation, module documentation, and skill development.
- Skill development policy: global skills live under `$CODEX_HOME/skills` or `~/.codex/skills`; project-local skills are created only when explicitly requested.

## Embedded Workflow Rules

If the repository has no stronger workflow rule, include this loop:

```text
Plan -> Cross Review -> Apply Review Fix -> Cross Review/ACCEPT
     -> Implement -> Cross Review -> Apply Review Fix -> Cross Review/ACCEPT
     -> Knowledge/Docs -> Automatic Checkpoint Commit -> Next Phase
```

Explain that each loop should produce one reviewable unit, such as a plan update, schema contract, implementation phase, evaluation report, review fix, or module document.

State these handoff invariants:

- Each review Finding keeps a stable ID, Fix Specification, boundary, Reviewer
  Checklist, and Closure Criteria.
- `$apply-review-fix` may report `READY_FOR_REVIEW` but cannot self-close a
  Finding; only the next `$cross-review` may report `CLOSED`.
- `$feature-implementer` records `IMPLEMENTED_PENDING_REVIEW` and cannot
  self-accept a phase.
- The next phase waits for `ACCEPT`, all blocking Findings `CLOSED`, required
  verification/documentation, and any repository-required checkpoint commit.
- Every workflow stage enforces the canonical simplicity rule: add no
  behavior-affecting variable/parameter, gate/threshold, retry, fallback, or
  compatibility branch without a current need, real consumer or trigger, and
  focused verification.
- Every distinct task begins with a branch gate. A task's planning,
  implementation, review-fix, and re-review stay on one branch; phases do not
  create nested branches.
- Durable project facts and recurring pitfalls discovered during a phase are
  recorded in project-level `AGENTS.md` before final review/checkpoint.

If the repository wants commit-per-phase discipline, state that each accepted
phase is committed automatically after required verification, documentation,
accepted cross-review, and blocking Finding closure. Stage explicit reviewed
paths only, inspect the staged diff, use a focused message describing the phase
outcome, report the hash, and do not bundle unrelated work. If a mixed worktree
cannot be isolated safely, report `CHECKPOINT_BLOCKED` instead of stashing,
resetting, discarding, or broad-staging files.

Say that goal-tracking tools should be used only when the user explicitly asks to create, continue, or manage a goal.

## Embedded Skill Routing Rules

Add a repository-specific skill routing section when the environment uses Codex skills. Keep it short and operational:

- `$agent-guidelines-init`: initialize Git when absent, audit local AI-coding
  ignore rules, and create or refresh repository `AGENTS.md`.
- `$skill-creator`: create or update global Codex skills.
- `$feature-planner`: plan unclear, risky, cross-module, or product-facing work before coding.
- `$cross-review`: review plans before implementation and completed work before acceptance.
- `$apply-review-fix`: consume repair-ready Finding IDs and boundaries, apply
  minimal fixes, and return closure evidence for re-review.
- `$feature-implementer`: implement only an accepted phase after review,
  finding, Open Question, prerequisite, and checkpoint gates are clear.
- `$module-introduction`: create module onboarding, architecture walkthrough, or interview docs after implementation.

State the default sequence for substantial work:

```text
$feature-planner -> $cross-review -> $apply-review-fix -> $cross-review
  -> $feature-implementer -> $cross-review -> $apply-review-fix -> $cross-review
  -> $module-introduction
```

Tell agents to skip non-applicable steps, use the smallest matching skill, and never start implementation while the plan or implementation document has unresolved blocking Open Questions.
Do not skip the second `$cross-review` after a fix when acceptance or Finding
closure matters.

## Embedded Skill Development Rules

When a repository wants local instructions for developing reusable skills, write these rules into `AGENTS.md`:

- Use `$skill-creator` before creating or updating a skill.
- Prefer global skills under `$CODEX_HOME/skills` or `~/.codex/skills`.
- Do not create project-local `.agents/skills` unless the user explicitly requests project-local behavior.
- Keep each skill single-purpose with clear frontmatter trigger text.
- Keep `SKILL.md` concise; use references only when details are too large for the core workflow.
- Do not add extra README, changelog, installation, or quick-reference files inside a skill.
- Validate every changed skill with `quick_validate.py`.
- Regenerate or update `agents/openai.yaml` when display metadata or the default prompt becomes stale.

## Embedded Repo Standards

Write a concise pointer and operational summary into `AGENTS.md`; keep detailed
rules in `ENGINEERING_STANDARDS.md`:

- Read the canonical engineering standard before non-trivial planning,
  implementation, review, or repair. Plans provide an Architecture Contract;
  implementations provide Architecture Conformance Evidence; reviews cite
  stable rule IDs.
- Apply the standard's Clean Code rules for readable control flow, low nesting,
  cohesive responsibilities, meaningful naming, useful comments, explicit
  outcomes, minimal abstractions, behavior-focused tests, and cleanup.
- Keep business capabilities cohesive, dependency direction acyclic, important
  state and business-rule authority explicit, public surfaces minimal, failure
  semantics distinguishable, and changes local. Require present-value
  justification for new abstractions, behavior-affecting variables/parameters,
  gates/thresholds, fallbacks, retries, caches, compatibility layers, or shared
  code; hypothetical future use is not sufficient.
- Follow existing repository layout before creating new directories.
- Use stable, descriptive names; avoid `data.json`, `final`, `copy`, `draft`, and version-number suffixes.
- Use repository-local naming conventions for docs, tests, fixtures, schemas, and generated outputs.
- Keep committed fixtures small, durable, and replayable.
- Put generated run outputs, scratch files, local caches, private notes, and tool state under ignored folders such as `.local/`, `tmp/`, `scratch/`, `artifacts/`, or `outputs/`.
- Add `.gitignore` patterns immediately when creating project-unrelated local files.
- Keep the AI Coding Gitignore Gate baseline covered even when the corresponding
  paths do not yet exist. If a baseline file is already tracked, keep it tracked
  and report the exception; never run `git rm --cached` without an explicit user
  request.

Use a compact knowledge ledger format such as:

```text
| ID | Area | Verified knowledge or pitfall | Required action | Evidence |
```

Give entries stable IDs, update an existing entry when facts change, and keep
task-specific decisions in plans/implementation records instead of turning
`AGENTS.md` into a chronological diary.

## Documentation Pairing

If the repository uses bilingual or localized docs, state the exact pairing convention. Examples:

- `README.md` and `README.zh-CN.md`
- `docs/product/01-prd.md` and `docs/product/01-prd.zh-CN.md`

Also state which operational docs are exempt, such as `AGENTS.md` or global skill files, when that is the repository's policy.

For repositories that require bilingual project documentation, write the rule explicitly:

- Every project-level document must have an English and Chinese version unless exempted.
- `AGENTS.md` may be single-language/local-only when the repository treats it as coding-agent configuration.
- Every project-document update must update the paired language version in the same phase.
- If a paired update is deliberately skipped, the handoff must state why.

## Validation

After editing:

```powershell
git rev-parse --show-toplevel
git diff --check -- AGENTS.md
git check-ignore -v --no-index .agents/__probe__
git check-ignore -v --no-index .codex/__probe__
git check-ignore -v --no-index AGENTS.md
Test-Path .\ENGINEERING_STANDARDS.md
Select-String -Path .\ENGINEERING_STANDARDS.md -Pattern '<[A-Z0-9_]+>'
```

For a shared standard, verify `git check-ignore --no-index
ENGINEERING_STANDARDS.md` returns no ignore match. For an explicitly local
standard, require and report the matching ignore rule instead.

Also check:

- Markdown fence balance if code blocks were changed.
- Local links when docs were linked.
- Stable engineering rule IDs are unique and no template placeholder remains.
- The selected language profile matches detected source, scripts, and config.
- `.gitignore` baseline coverage even when no new local directory was created.
- detected local AI tool-state paths and tracked exceptions.
- `git status --short --branch` to report remaining state.

## Handoff

Report:

- Whether the target was already a repository or `git init` was run, and the
  verified repository root.
- AI-coding `.gitignore` coverage added/preserved and any tracked exceptions.
- Whether `ENGINEERING_STANDARDS.md` was created or merged, which language
  profile was selected, and whether the file is tracked or local.
- Whether `AGENTS.md` was created or updated and points to the canonical
  standard.
- Key rules added or preserved.
- Any commands or conventions that could not be discovered.
- Validation run.
- Uncommitted state.
