---
name: cli-agent-orchestration
description: Orchestrate CLI coding agents (Codex, Claude Code, Qwen Code, Qoder, Antigravity, and similar) while keeping ownership of user discussion, research, architecture, plans, direction, and final code acceptance. Use whenever work is delegated to an external agent — implementation, bug fixes, plan or code review, audits, or parallel executors across worktrees — even if the user only names the executor or model.
---

# CLI Agent Orchestration

The current agent is the orchestrator. Follow the user's instructions, the repository's guidance, and the task contract. Project-specific models, build locks, and checkpoint rules belong in the repository.

## Roles

| Role | Owns |
|---|---|
| Orchestrator | User discussion, research, plans, architecture, interface specs, behaviour contracts, design rulings, executor choice and supervision, reading and judging the code, final acceptance. |
| Executor | Bounded coding, bug fixing, verification, and read-only plan or code review. Reports evidence, deviations, and design gaps; never sets scope, rules on design, or accepts its own work. |

Write plans and specs yourself; an executor may only critique them. When the user delegates decisions ("decide, report afterwards"), decide conservatively, record the ruling with its date and evidence in the plan, and report it. Still ask before irreversible actions on real data, installs, publishing or pushing, and anything that reverses an explicit user decision.

## Before dispatch: contract first

Loose rulings produce code that passes tests with the wrong approach. Before any executor touches a module:

1. **Behaviour contract.** Write or update the module's contract in the repository: structure (owners, files), numbered MUST rules with stable IDs, and the acceptance test that proves each rule. A rule without a test, or a test without a rule, is a finding.
2. **Reference comparison.** When the product mirrors a reference implementation (an official client, upstream behaviour), add a rule-by-rule comparison. Resolve divergences to the reference's observed behaviour unless the user decided otherwise. Rank evidence live observation > reference static analysis > third-party code > legacy code. Start caching and performance work from the reference's strategy, measure, then optimize.
3. **Written ruling.** Every design or performance discussion with the user becomes a dated ruling (user's words plus evidence) before dispatch. Diagnose user-reported bugs against the running app (logs, debug port, measurements) and name the faulty code path in the ruling.
4. **Structure.** Plans and dispatches state the module layout and the repository's file-size and layering rules, so god files never form. Schedule splits after the current writer merges.
5. **Docs hygiene.** While researching or writing docs, move outdated documents to an archive folder with an index and repoint links; never silently delete them.

## Choose an executor

- Keep the user's executor, model, and effort choices for related work until changed; fix rounds do not re-ask. If unset, ask once with a recommended default; if the user delegates, choose and report. Honour routing preferences ("use X more").
- Read each CLI's help and model list; smoke-test the exact model string (built-in and custom names look alike). Learn each one's limits: context (long tasks stop early, so slice the work: implement OR tests-plus-verify, fresh session per slice) and quota.
- On failure, quota exhaustion, or a stall: preserve the work, record the quota reset time, and fail over with the same contract plus a handoff. Never silently replace a model the user mandated.
- Never believe an executor's claim about tool limits without reading the raw log.

## Dispatch

- Use [the dispatch contract](references/dispatch-contract.md): cite rule IDs and repository rules by path, quote critical restrictions, and name every test to write — unnamed tests are under-delivered.
- One writer per worktree; parallel writers get separate worktrees and branches with disjoint files. Share heavy dependency folders by link, and remove worktrees only with a method that cannot follow those links.
- Permissions follow the task and the user's authorization; reviews and audits are read-only. A skill never authorizes pushing, publishing, or touching live data.
- Tests are silent: headless browsers, recording ports instead of real shell, picker, or opener calls, no windows on the user's desktop.

## Run and monitor

- Use each CLI's noninteractive syntax ([CLI notes](references/cli-notes.md)); close stdin; record CLI, model, worktree, session and process IDs, start time, output file, and result. Resume only by explicit session ID of the same task.
- Every run has a wall-clock limit; compile-heavy commands also go through the repository's build lock and watchdog, with build parallelism capped through the environment. Executors run verification synchronously — never in their own background before exiting.
- Check progress about every 10 minutes (output tail, worktree diff, liveness), not every turn; rely on completion notifications in between and do useful work meanwhile. Treat a run as stuck when output is unchanged ≈10 min and a second signal agrees (no CPU, no worktree writes); kill the process tree, keep artifacts, fail over.
- Respect the user's cap on parallel executors and check free memory first; after a host reap, inspect each worktree before re-dispatching and kill orphans.
- Unattended goals: keep the dispatch → review → merge loop going at the user's parallelism cap, decide per the delegation rule, and resume after quota refreshes instead of stopping.

## Batch verification

Parallel executors run only targeted checks: lint, tests of every package they touched (all of it, not just the edited files), type check, touched UI specs. The orchestrator merges finished branches into one integration branch as they arrive, pre-compiles it while the last executor works, and runs the full verification once on the combined tree. A change that regenerates shared types or IPC bindings is verified on every stack it touches.

Triage each failure of the full run:

- **Regression** from a merged change → fix the business code (finding to the owner).
- **Outdated test** encoding a superseded design → the orchestrator records a ruling, then the test is updated to it. Executors never loosen a failing test on their own.
- **Flake** → rerun that spec alone; accept only when green, and note it.

## Review and accept

Executor reports and green tests are leads, not evidence. An executor's "fixed / all green" is often a narrower run than asked or a fix of an adjacent symptom — confirm in the raw log that the named failures now pass, and re-run the full verification yourself.

**Read the logic, rule by rule.** For each rule or acceptance ID: open the core changed functions, trace the runtime path (thread, surface, data flow, second page, restart, error, navigation), compare with recorded rulings and gates, and record a verdict (implemented as designed / defect with reason) in the plan. Reject a change that reverses a recorded decision unless the user reopened it. Wrong-approach patterns to look for:

- ordering applied per page (locally sorted, globally wrong); a keyset cursor whose comparator lacks a unique tiebreak;
- a background task disguised as pagination; one bad record failing a whole page;
- cache keys from unnormalised values; state reset on mount that defeats a cache; a loading state shown while local data is ready;
- a fix that changes a mechanism without reproducing the original failure;
- shared fixtures edited outside the task, residue left by a revert, dead code that would reintroduce rejected behaviour;
- platform or FFI code in non-platform layers, whole-file shell rewrites, machine-specific paths.

**Test strength:** a geometry test comparing containers equal by construction passes vacuously; prefer measurements of rendered content.

**UI merges:** take headless screenshots of each affected screen at a wide and a narrow width, review alignment, overlap, and duplicate controls (check visibility — kept-alive hidden views make locators ambiguous), and show the key ones to the user.

**Status:** keep a per-rule status in the plan — planned / implemented / verified-live / defect — with commit and evidence. Merged-and-green is only *implemented*; *verified-live* needs a measurement in the real app, taken against a baseline captured before the change. A user-reported symptom in an *implemented* area is an acceptance defect.

## Close

- Rebase onto the current mainline, re-verify, then fast-forward. Follow the repository's commit and publication policy.
- After a verified merge, delete the task branch and its worktree (keep reference branches; never delete unmerged work without confirmation).
- After a read-only audit, confirm no writes occurred.
- Report what ran, what you verified, the decisions you made, what remains, and which claims are still unverified.
