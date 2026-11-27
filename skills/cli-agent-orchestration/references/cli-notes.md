# CLI invocation notes

These are examples, not fixed model or permission policy. Run each installed CLI's `--help` and model listing before relying on flags. Quote paths and prompts for the active shell; redirect output to a private scratch directory. Never print credentials into logs.

| CLI | Noninteractive entry | Resume by explicit ID |
|---|---|---|
| Codex | `codex exec -C <worktree> -m <model> -c model_reasoning_effort=<level> - < prompt.md` | `codex exec resume <session-id> -` |
| Claude Code | `claude -p <prompt> ...` | Check current `claude --help`; use an explicit session ID |
| Qwen Code | `qwen -p <prompt> -m <model> -w <worktree> ...` | `-r <session-id>` |
| Qoder | `qoderclicn -p <prompt> -m <model> -w <worktree> ...` | `-r <session-id>` |
| Antigravity | `agy --model <model> -p=<prompt> --output-format json ...` | `--conversation <id>` |

Choose model and effort flags from current help. Some CLIs encode effort in model names, accept only certain effort spellings, or list built-in and custom models with near-identical names — smoke-test the exact string. Confirm the selected model from the run output (session header or JSON). Do not use `--last`, `--continue`, or similar implicit resume options; they can attach to a user-owned conversation. Close stdin (`< /dev/null`, or feed the prompt file) so the CLI never waits for input.

## Known pitfalls

- **Misreported tool limits.** An executor may claim its commands are cut off after a fixed time (e.g. "30 s execution boundary") when the raw log shows the command finished and printed its result; a yield/poll window in the CLI's exec tool can be misread as a kill. Check the raw log (`succeeded/exited in N ms`, raw test summary, or `--json` event stream with the tool's timeout argument) before routing around a supposed cap, and never repeat an unverified limit in later prompts — the executor will obey it.
- **Context exhaustion.** Long sessions end early with partial edits. Resuming an exhausted session tends to stop again quickly; start a fresh session with a handoff instead, and check for half-applied edits first.
- **Shell path rewriting.** Git Bash / MSYS rewrites arguments that look like POSIX paths (e.g. `cmd /c` becomes `cmd C:/`). Set `MSYS_NO_PATHCONV=1` or double the slash when passing Windows switches through it, and confirm the command actually ran.
- **Line-ending rewrites.** Bulk edits through shell cmdlets (e.g. PowerShell `Set-Content`) can convert a whole file's line endings and inject literal escape sequences. Tell executors to edit with their patch tool.
- **Detached processes.** A run started with `&` from a short-lived shell may outlive the shell but will not produce a completion notification; record its PID and output file and check it on the regular cadence.

Keep the run record in a private, ignored registry or scratchpad. Useful fields: CLI, version, task, role, model, effort, worktree, session ID, process ID, start and end times, exit code, result path, verification, and failure category. Never store tokens or full private transcripts in the registry.
