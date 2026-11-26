---
name: cli-agent-orchestration
description: Coordinate work across available CLI coding agents. Use when the user asks an orchestrator to delegate implementation, fixes, or independent review to one or more external agents; covers executor selection, bounded dispatch, monitoring, handoff, and independent verification.
---

# CLI Agent Orchestration

Use this skill only when work will actually be delegated to another agent. The current agent is the orchestrator; the selected CLI agent is an executor or an independent reviewer. Follow the user's instructions, the target repository's guidance, and the current task contract. Project-specific roles, model preferences, build locks, acceptance gates, and checkpoint rules belong there, not here.

## Choose an executor

1. Check the user's current choice of executor, model, and effort, including choices already made in this conversation. Keep those choices for related dispatches until changed. Never ask again merely because a fix round starts.
2. If a choice is missing, ask once before the first dispatch when an interactive question is available. Offer the usable local CLIs and a recommended default. Ask about model or effort only when the answer affects cost, speed, capability, or the user's stated preference. If the user delegates the choice or does not answer an optional question, choose and report the result.
3. Discover installed CLIs and their current help/model lists. Check the exact syntax and selected model with a cheap smoke run when uncertain. Do not hard-code a particular vendor, model ranking, quota snapshot, executable path, or highest effort level.
4. If the chosen CLI fails or runs out of quota, classify the failure, preserve its work, and switch to another suitable available CLI when the user has not forbidden failover. Report the switch. Do not silently replace a user-selected model with a different one if that choice was a hard constraint.

## Prepare the dispatch

- Inspect the repository state, task branch, relevant instructions, and existing edits. Define one bounded outcome, allowed paths, acceptance evidence, and verification commands. Record open design decisions before assigning implementation. The orchestrator owns any decisions the user or repository reserves for it.
- Use one writer per worktree. Separate concurrent writers into independent worktrees or tasks whose writes cannot overlap. Preserve unrelated changes. Keep logs and prompts in a private scratch location outside tracked files.
- Give the executor a self-contained prompt using [the dispatch contract](references/dispatch-contract.md). Include repository rules by path and quote critical restrictions. Do not assume the executor sees this conversation.
- Select permissions based on the task and the user's authorization. A skill is not permission to bypass approvals, alter live data, push, publish, or use unrestricted execution. Use a read-only contract for reviews.

## Run and monitor

- Use the installed CLI's supported noninteractive syntax. See [CLI notes](references/cli-notes.md) for examples; verify them against local help because flags change.
- Give every run an explicit output location and record its process/session ID, worktree, role, model, start time, and result. Resume only a session created for the same task and role; never attach to the user's unspecified latest interactive session.
- Monitor each dispatched run through completion or a clear terminal failure. A result file alone is insufficient if the process is still writing. Put time limits on waits and recheck long runs. If the orchestrator cannot keep a watch active, report that limitation instead of describing the run as monitored.
- Respect machine resource limits and any repository-specific build locks. Run tests headlessly when automation could disturb the user's desktop. Never clean another agent's active worktree or outputs.

## Review and close

- Treat executor reports as leads. Inspect the actual diff, status, tests, and task-specific evidence independently. A read-only reviewer must not accept its own implementation, and an implementer must not self-accept when the repository requires independent review.
- For a fix round, send exact findings and current state to the same task session when appropriate. For failover, give the next executor the diff, previous report, and remaining work so it continues from the existing state.
- Apply the target repository's review, commit, and publication policy. Do not impose a universal plan cadence, checkpoint commit, push, or PR. Tell the user what ran, what was verified, what remains, and which claims are still unverified.
