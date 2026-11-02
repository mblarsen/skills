# Manifest And Helper Reference

Read this before saving, pausing, or resuming a workspace, or interpreting helper status.
For first use, follow SKILL.md's missing-manifest approval gate before calling the helper. For identity gaps, use [IDENTITY.md](IDENTITY.md), not helper-source exploration.

## Runtime Requirements

The bundled `rex-sessions` executable requires Python 3.11+, Rex CLI, and `ps`.
Its session discovery supports Pi-compatible JSONL files. Other agent formats need separate identity and persistence checks.
The command guide comes from the installed Rex CLI, not this reference.

Resolve the executable relative to this skill directory, not the current project.
A `rex-sessions` command on PATH is optional. Verify its source before assuming it matches the bundled script.

Defaults:

- Manifests: `~/.local/state/rex/sessions/`. Override with `REX_SESSIONS_DIR`.
- Legacy helper discovery root: `~/.pi/agent/sessions/`. Override with `PI_SESSIONS_DIR`.

This default is not a reason to search either it or `~/.config/pig/agent/sessions/`. Obtain exact active file paths from their owners through IDENTITY.md. The helper does not bootstrap a missing manifest: `show`, `path`, `status`, `snapshot`, `up`, and `down` all require an existing one.

## Manifest Fields

One `<workspace>.toml` file describes a workspace. Keep private inventories outside the skill repository.

- `rex_session`: the enclosing Rex session ID.
- `writer`: the controller responsible for manifest updates.
- `[[panes]]`: one entry per pane. Several entries can share a `window` label.
- `alias`: the intercom name. Record the full agent UUID in `session` separately from short targeting IDs.
- `cwd`: the working directory used on restore.
- `restore`: authoritative argv, with executable first and every argument separate. Execute directly without shell interpolation.
- `observed_argv`: diagnostic process arguments. Process titles can hide launch arguments.
- `stop = "keep"`: protects the controller. Other panes can be `stoppable`.
- `[[layouts]]`: split placement, ratio, and pane order for supported layouts. The split ratio gives the new pane's percentage.

Block IDs and PIDs are transient. Store them in a runtime sidecar, not as durable identity.
For non-resumable and fresh-start entries, record that restoration cannot recover the same conversation.

## Commands

Replace placeholders before execution. Angle brackets below are notation, not shell syntax.

```text
./rex-sessions list
./rex-sessions show <workspace>
./rex-sessions path <workspace>
./rex-sessions status <workspace>
./rex-sessions snapshot <workspace>
./rex-sessions up <workspace> --dry-run
./rex-sessions down <workspace> --dry-run
```

- **Save**: construct a reviewed merge from bounded, verified observations. `snapshot` uses legacy session discovery and positional assumptions; do not use it for bootstrap or identity-gap resolution. Automated replacement is unsafe for paused workspaces.
- **Pause**: run `down` after preflight and dry run.
- **Resume**: run `up` after preflight and dry run.
- **Status**: run `status`, then verify identities independently. Its `ok` means no detected conflict, not a verified UUID; report unknown when identity evidence is missing.

`up` and `down` change processes when `--dry-run` is absent.
`--only <agent-alias>` is repeatable, but partial split operations are unsafe.
`down --force` overrides keep protection. Retain that protection during ordinary pauses.

The current dry-run summary says panes "started" or "closed" even though it only prints commands.
Treat the printed commands as the plan, not evidence of changes.

`status` returns 1 for paused entries or drift, including after a successful pause.
This is distinct from the exit code of `down`.

## Verification Limits

A full workspace pause/resume with original agent identities and a two-pane split has passed a manual test.
That test does not establish safety for every operation.

- Pane matching uses position. After one split pane closes, the script can misidentify the surviving pane.
- Partial split operations, nested splits, and arbitrary layouts are unsafe or unsupported.
- `snapshot --write` can discard paused entries and retain stale identity assumptions. Use a reviewed merge instead.
- Shutdown closes blocks. Graceful exit, child-process cleanup, and final state flushing are not fully verified.
- Non-resumable and explicit fresh-start entries start a different conversation.
- Process arguments and pane counts alone do not prove agent identity.
- `up` requires the enclosing Rex session to exist. It does not recreate that session automatically.

Test unsupported behavior in a disposable workspace before using it on a live team.

## Regression Test

From this skill directory:

```sh
python3 test_rex_sessions.py
```

The test mocks Rex subprocesses and checks session-inspection arguments. It does not validate real agent lifecycle or change live panes.
