---
name: agent-guidelines-init
description: Initialize repository Git when absent, audit local AI-coding ignore rules, and generate or update a repository-level AGENTS.md guide. Use for repository setup, engineering standards, project knowledge/pitfall ledgers, task-branch gates, accepted-phase commits, review closure, documentation pairing, git hygiene, or skill routing.
---

# Agent Guidelines Init

Use this skill to create or update `AGENTS.md` in the current repository. The output should make the repository self-describing for future coding agents and contributors.

This skill is an initializer, not a daily workflow tool. It writes project-level guidance into `AGENTS.md`; later planner, implementer, reviewer, and fixer skills should read that file as the local source of truth.

## Core Rules

- Inspect the repository before writing. Do not generate a generic template blindly.
- Preserve existing useful `AGENTS.md` rules and merge changes instead of overwriting them.
- Keep project-specific rules in `AGENTS.md`; keep reusable execution behavior in global skills only when it cannot be expressed as repository guidance.
- When the repository has a substantial architecture/consistency standard, keep
  one canonical project-level source instead of duplicating the full policy.
  Treat `ENGINEERING_STANDARDS.md` as local AI workflow guidance by default and
  ignore it; an existing intentionally tracked team standard is a reported
  exception, not something this skill untracks automatically.
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
ENGINEERING_STANDARDS.md
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
git check-ignore -v --no-index ENGINEERING_STANDARDS.md
```

The gate passes only when every baseline path is covered by `.gitignore` or is
reported as an intentional tracked exception, and each detected local tool-state
path is either ignored or reported as intentionally shared.

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
- Coding style, naming patterns, framework conventions, and file placement rules.
- The canonical architecture/consistency standard and its stable rule IDs, or a
  concise repository-specific subset when no separate standard is warranted.
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

Write these rules into `AGENTS.md` when applicable:

- Read the canonical engineering standard before non-trivial planning,
  implementation, review, or repair. Plans provide an Architecture Contract;
  implementations provide Architecture Conformance Evidence; reviews cite
  stable rule IDs.
- Keep business capabilities cohesive, dependency direction acyclic, important
  state and business-rule authority explicit, public surfaces minimal, failure
  semantics distinguishable, and changes local. Require present-value
  justification for new abstractions, fallbacks, retries, caches, compatibility
  layers, or shared code.
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
git check-ignore -v --no-index ENGINEERING_STANDARDS.md
```

Also check:

- Markdown fence balance if code blocks were changed.
- Local links when docs were linked.
- `.gitignore` baseline coverage even when no new local directory was created.
- detected local AI tool-state paths and tracked exceptions.
- `git status --short --branch` to report remaining state.

## Handoff

Report:

- Whether the target was already a repository or `git init` was run, and the
  verified repository root.
- AI-coding `.gitignore` coverage added/preserved and any tracked exceptions.
- Whether `AGENTS.md` was created or updated.
- Key rules added or preserved.
- Any commands or conventions that could not be discovered.
- Validation run.
- Uncommitted state.
