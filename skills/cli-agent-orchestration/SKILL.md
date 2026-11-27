---
name: cli-agent-orchestration
description: Orchestrate CLI coding agents (Codex, Claude Code, Qwen Code, Qoder, Antigravity, and similar) while keeping ownership of user discussion, research, architecture, plans, direction, and final code acceptance. Use whenever work is delegated to an external agent — implementation, bug fixes, plan or code review, audits, or parallel executors across worktrees — even if the user only names the executor or model.
---

# CLI Agent Orchestration

Use this skill when work will be delegated to another agent. The current agent is the orchestrator. Follow the user's instructions, the target repository's guidance, and the current task contract. Project-specific model preferences, build locks, and checkpoint rules belong in that repository.

## Role ownership

Delegation does not transfer responsibility for the project's direction or final result.

| Role | Owns |
|---|---|
| Orchestrator | Discuss requirements, priorities, trade-offs, architecture, and plans with the user; research and inspect evidence; write and revise the plan, architecture, and interface decisions; set task boundaries and acceptance criteria; choose and supervise executors; resolve review findings and design gaps; inspect and verify code against the agreed design; decide whether the result is accepted. |
| Executor | Give read-only reviews of plans or code; write code within the assigned boundary; run verification; fix bugs and review findings; report evidence, deviations, and blockers. |

The orchestrator writes plans and architecture itself. It may ask an executor to critique them, but it evaluates the critique, decides, and discusses consequential decisions with the user. An executor never sets scope, makes architecture rulings, approves its own work, or declares acceptance. Reviews and audits are bounded read-only executor tasks; the orchestrator checks the evidence and owns the verdict.

When the user delegates decisions ("decide yourself, report afterwards"), make the call, record it as a ruling in the repository's plan or spec, and report it. Still ask before irreversible actions on real data, publishing, or anything that contradicts an earlier explicit user decision.

## Choose an executor

1. Use the user's current choice of executor, model, and effort, including choices made earlier in the conversation, for related dispatches until changed. Do not re-ask because a fix round starts. Honour stated routing preferences (e.g. "use X more").
2. If a choice is missing, ask once before the first dispatch, offering the usable local CLIs and a recommended default. If the user delegates or does not answer, choose and report.
3. Discover installed CLIs and their current help and model lists. Smoke-test exact syntax and the model name with a one-line prompt when uncertain — names that look alike (built-in vs. custom models, effort spellings) often differ.
4. Learn each executor's limits and route around them: context size (long tasks end early), per-command time caps (some runners stop synchronous commands after tens of seconds, so full test suites never finish inside them), quota. Give such executors bounded slices and run the full suites yourself or on an executor without the cap.
5. On failure, quota exhaustion, or a stalled session, classify the cause, preserve the work, and fail over to another suitable CLI with the same contract plus a handoff. Report the switch. Do not silently replace a user-mandated model.

## Prepare the dispatch

- Settle open design decisions before assigning implementation. Inspect the repository state, branch, instructions, and existing edits. Define one bounded outcome, allowed paths, acceptance evidence, and verification commands.
- One writer per worktree. Give concurrent writers separate worktrees on separate branches whose files do not overlap; sequence tasks that touch the same files. Share heavy dependency folders by link rather than reinstalling, and remove worktrees only with a method that cannot follow such links into the main checkout.
- Write a self-contained prompt with [the dispatch contract](references/dispatch-contract.md). Cite repository rules by path, quote critical restrictions, and list every test the executor must write — executors under-deliver tests that are not enumerated.
- Size the task to the executor: one round = implement OR tests-plus-verification for executors with small context or command caps; a fresh session per slice beats resuming an exhausted one.
- Select permissions from the task and the user's authorization. A skill is never permission to bypass approvals, alter live data, push, or publish. Use a read-only contract for reviews and audits.

## Run and monitor

- Use the CLI's supported noninteractive syntax (see [CLI notes](references/cli-notes.md); verify flags locally). Close stdin. Give every run an explicit output file and record session ID, process ID, worktree, role, model, start time, and result. Resume only sessions created for the same task and role, by explicit ID.
- **Hard limits:** every run gets a wall-clock timeout, and compile-heavy commands also get the repository's watchdog. Executors must run verification synchronously and report results; spawning verification in their own background and exiting leaves orphans and unverified code.
- **Progress cadence: check once every 10 minutes** (output tail, worktree diff, process liveness), not turn after turn. Completion notifications carry results between checks. While waiting, do other substantive work or end the turn. A run launched detached from your session will not notify you — prefer the tool's background mode, or rely on the 10-minute check for detached runs.
- **Stuck detection and recovery:** treat a run as stuck when a strong signal (output and state files unchanged ≈10 min while the process lives) is corroborated by a second (near-zero CPU delta, no worktree writes, a compile line unchanged ≈10 min). Kill the whole process tree, keep written artifacts, fail over with a handoff, and report.
- **Resources:** check free memory before launching parallel runs; heavy compiles plus browser tests plus several agents can exhaust RAM and the host may reap background jobs. Respect build locks, serialize compiles when memory is tight, and after a reap inspect each worktree — executors often finished their edits before being killed. Clean up orphaned dev servers and agent processes you started.
- Run UI tests headlessly. Never clean another agent's active worktree or outputs.

## Review and close

- Treat executor reports as leads. Inspect the actual diff, tests, screenshots, and runtime behaviour against the plan and architecture yourself, for design conformance and bugs. Re-run the full verification yourself before accepting; executor summaries are not evidence.
- Check test strength, not just colour: a geometry or alignment test that compares containers which are equal by construction passes vacuously. Prefer measurements of the rendered content.
- Verify across every stack a change touches. A backend change that regenerates shared types or IPC bindings must also pass the frontend's type check and tests before merge.
- Check boundaries an executor tends to cross: OS/FFI code in non-platform layers, shell edits that rewrite line endings, machine-specific absolute paths in tracked files, dead code left behind.
- After a read-only audit, confirm no writes occurred (clean `git status`).
- For a fix round, send exact findings and the current state; for failover, include the diff summary, the previous report, and remaining work.
- Rebase task branches onto the current mainline and re-verify before fast-forward merging. Apply the repository's commit and publication policy; do not impose universal cadences, pushes, or PRs.
- After a verified merge, delete the task branch (`git branch -d`; `-D` only when the content is confirmed incorporated) and remove its worktree. Keep intentional reference branches; never delete unmerged work without the user's confirmation (an archive tag is a cheap safety net).
- Tell the user what ran, what you verified, what remains, and which claims are still unverified.
