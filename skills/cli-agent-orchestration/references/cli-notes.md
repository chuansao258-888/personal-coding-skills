# CLI invocation notes

These are examples, not fixed model or permission policy. Run each installed CLI's `--help` and model listing before relying on flags. Quote paths and prompts for the active shell; redirect output to a private scratch directory. Never print credentials into logs.

| CLI | Noninteractive entry | Resume by explicit ID |
|---|---|---|
| Codex | `codex exec -C <worktree> -m <model> ... <prompt>` | `codex exec resume <session-id> <prompt>` |
| Claude Code | `claude -p <prompt> ...` | Check current `claude --help`; use an explicit session ID |
| Qwen Code | `qwen -p <prompt> ...` | Check current `qwen --help`; use an explicit session ID |
| Qoder | `qoderclicn -p ... -w <worktree> <prompt>` | `-r <session-id>` |
| Antigravity | `agy --model <model> -p=<prompt> ...` | `--conversation <id>` |

Choose model and effort flags from current help. Some CLIs encode effort in model names. Confirm the selected model from the run output when available. Do not use `--last`, `--continue`, or equivalent implicit resume options because they can attach to a user-owned conversation. Close stdin for noninteractive runs when the CLI might otherwise wait for more input. Use explicit timeout or process monitoring for long runs.

Keep the run record in a private, ignored registry or scratchpad. Useful fields: CLI, version, task, role, model, effort, worktree, session ID, process ID, start and end times, exit code, result path, verification, and failure category. Never store tokens or full private transcripts in the registry.
