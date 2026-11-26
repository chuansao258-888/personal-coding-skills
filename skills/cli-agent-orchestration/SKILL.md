---
name: cli-agent-orchestration
description: Orchestrate CLI coding agents while retaining ownership of user discussions, research, architecture, plans, direction, and final code acceptance. Use when delegating plan or code review, implementation, or bug fixes to external agents.
---

# CLI Agent Orchestration

Use this skill when work will be delegated to another agent. The current agent is the orchestrator. Follow the user's instructions, the target repository's guidance, and the current task contract. Project-specific model preferences, build locks, and checkpoint rules belong in that repository.

## Role ownership

The orchestrator must actively perform its own duties. Delegation does not transfer responsibility for the project's direction or final result.

| Role | Owns |
|---|---|
| Orchestrator | Discuss requirements, priorities, trade-offs, architecture, and plans with the user; research and inspect evidence; write and revise the plan, architecture, and interface decisions; set task boundaries and acceptance criteria; choose and supervise executors; resolve review findings and design gaps; inspect and verify code against the agreed design; decide whether the result is accepted. |
| Executor | Give read-only reviews of the orchestrator's plan or of code; write code within the assigned boundary; run verification; fix bugs and review findings; report evidence, deviations, and blockers. |

The orchestrator writes or revises plans and architecture itself. It may ask an executor to critique them, but must evaluate that critique, decide changes, and discuss consequential decisions with the user. An executor does not set product scope, make architecture rulings, approve its own work, or declare final acceptance. When a plan or code review is needed, assign it as a bounded read-only executor task; the orchestrator still checks the evidence and owns the verdict. Never treat an executor's review or test summary as a substitute for the orchestrator's own inspection.

## Choose an executor

1. Check the user's current choice of executor, model, and effort, including choices already made in this conversation. Keep those choices for related dispatches until changed. Never ask again merely because a fix round starts.
2. If a choice is missing, ask once before the first dispatch when an interactive question is available. Offer the usable local CLIs and a recommended default. Ask about model or effort only when the answer affects cost, speed, capability, or the user's stated preference. If the user delegates the choice or does not answer an optional question, choose and report the result.
3. Discover installed CLIs and their current help/model lists. Check the exact syntax and selected model with a cheap smoke run when uncertain. Do not hard-code a particular vendor, model ranking, quota snapshot, executable path, or highest effort level.
4. If the chosen CLI fails or runs out of quota, classify the failure, preserve its work, and switch to another suitable available CLI when the user has not forbidden failover. Report the switch. Do not silently replace a user-selected model with a different one if that choice was a hard constraint.

## Prepare the dispatch

- Discuss unclear requirements and material trade-offs with the user. Inspect the repository state, task branch, relevant instructions, and existing edits. Research the problem, write or update the plan and architecture when needed, and define one bounded outcome, allowed paths, acceptance evidence, and verification commands. Resolve open design decisions before assigning implementation; require executors to report later design gaps for the orchestrator to resolve.
- Use one writer per worktree. Separate concurrent writers into independent worktrees or tasks whose writes cannot overlap. Preserve unrelated changes. Keep logs and prompts in a private scratch location outside tracked files.
- Give the executor a self-contained prompt using [the dispatch contract](references/dispatch-contract.md). Include repository rules by path and quote critical restrictions. Do not assume the executor sees this conversation.
- Select permissions based on the task and the user's authorization. A skill is not permission to bypass approvals, alter live data, push, publish, or use unrestricted execution. Use a read-only contract for reviews.

## Run and monitor

- Use the installed CLI's supported noninteractive syntax. See [CLI notes](references/cli-notes.md) for examples; verify them against local help because flags change.
- Give every run an explicit output location and record its process/session ID, worktree, role, model, start time, and result. Resume only a session created for the same task and role; never attach to the user's unspecified latest interactive session.
- Monitor each dispatched run through completion or a clear terminal failure. A result file alone is insufficient if the process is still writing. Put time limits on waits and recheck long runs. If the orchestrator cannot keep a watch active, report that limitation instead of describing the run as monitored.
- **Progress check cadence (user, 2026-11-27, supersedes same-day "no polling" wording):** while an executor or background verification runs, check its progress **once every 5 minutes** (output file tail / worktree diff / process liveness), not turn after turn. Rely on completion notifications for results between checks. While waiting, do other substantive work or end the turn — repeated status peeks waste turns and disturb the user.
- **Hang prevention and recovery (user, 2026-11-27):** every dispatch must have a hard wall-clock limit and a stuck-detection path:
  1. Record the start time and give the background run an explicit timeout (e.g. the Bash tool timeout; for compile commands also set the repository watchdog such as `MYPIKPAK_HEAVY_TIMEOUT_MIN`). Never launch an executor without a limit.
  2. At a justified interval (not frequent polling), detect a stuck run by combining signals: process alive but its session/state file mtime stale (≈10 min), near-zero CPU delta, and zero worktree writes; or a compile output line unchanged for ≈10 min. Any one strong signal plus a second corroborating signal means stuck.
  3. Recover: kill the whole process tree (`taskkill /PID <pid> /T /F` on Windows), preserve any artifacts already written, and fail over to another available CLI with the same contract plus a note on the previous attempt. Report the switch to the user.
  4. Contract requirement: the executor must run its verification synchronously and include the results in its final report — it must NOT spawn verification in its own background and exit early (this leaves orphan processes and unverified code).
- Respect machine resource limits and any repository-specific build locks. Run tests headlessly when automation could disturb the user's desktop. Never clean another agent's active worktree or outputs.

## Review and close

- Treat executor reports as leads. Personally inspect the actual diff, status, tests, and task-specific evidence against the plan and architecture. Check both design conformance and bugs. Obtain a separate read-only plan or code review when the task calls for one, then adjudicate its findings yourself. An executor's review never replaces final acceptance by the orchestrator.
- For a fix round, send exact findings and current state to the same task session when appropriate. For failover, give the next executor the diff, previous report, and remaining work so it continues from the existing state.
- Apply the target repository's review, commit, and publication policy. Do not impose a universal plan cadence, checkpoint commit, push, or PR. The orchestrator decides and reports acceptance only after its own checks pass. Tell the user what ran, what was verified, what remains, and which claims are still unverified.
- **Delete merged task branches (user, 2026-11-27):** once a task branch is merged into the mainline and the merge is verified, delete the old branch (`git branch -d`; `-D` only when the content is confirmed incorporated) and remove its task worktree to free disk. Keep intentionally-retained reference branches (e.g. golden/demo lines) and never delete branches with unmerged work without user confirmation.
