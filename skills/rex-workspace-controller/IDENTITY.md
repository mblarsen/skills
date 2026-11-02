# Bounded Identity Discovery

Use after approval to create a manifest, or to resolve a specific gap in an existing manifest. Stop when the required fields are verified or the bounded sources below are exhausted. Unknown is a valid result.

## Keep The IDs Separate

| Value | Source | Use |
| --- | --- | --- |
| Full Rex session ID (`session:...`) | `rex ls --json`, confirmed by session inspect | Scope all Rex commands |
| Full window ID / block ID | Target session inspect and block listing | Locate tabs/panes; transient, not conversation identity |
| PID / cwd / script | Target block's `process` method | Process evidence; PID is transient |
| Intercom name / short ID | Fresh intercom listing | Contact a peer, not a durable resume target |
| Full conversation UUID | Peer self-report plus its own session header, or explicit live resume UUID | Manifest `session` and restore `--session` |
| Exact session-file path | Peer's own session metadata or user-supplied path | Targeted persistence check |

Verification requires a full conversation UUID bound to a specific live Rex session/block: a peer confirms both from its own metadata/location, or the exact block's live process explicitly selects that UUID. A matching file header verifies persistence, not pane ownership. A tab label, process title, matching cwd, model, filename timestamp, or quoted UUID does not establish the binding. Never choose the newest file or expand a short UUID by searching archives.

Stable names are optional. An unnamed agent can be verified by UUID plus block binding. Use a descriptive manifest alias if needed, mark it as a controller-assigned label in the evidence, and leave `intercom_id` absent unless known. Do not claim a title/alias is an intercom identity or rename the agent automatically. If it cannot be contacted by a fresh short ID, use exact block process evidence or ask the user.

## 1. Inventory The Target's Terminals

After resolving the requested workspace, substitute its full ID and the returned full block IDs:

```sh
rex session inspect "$workspace_id" --json
rex block ls -s "$workspace_id" --json
rex block call -s "$workspace_id" -b "$block_id" process
```

Use `session inspect` for layout and `block call ... process` for `.foreground` process metadata. `block inspect` describes the block and methods; it is not the process-info endpoint. An empty or missing field is unknown, not proof that Rex lacks process support.

For launch evidence, query only the returned PID if needed:

```sh
ps -ww -o command= -p "$pid"
```

Process titles can hide arguments; rendered command strings are not safely reversible argv. Keep them diagnostic. If a wrapper hides a child, prefer peer confirmation; do not enumerate all system processes or open files.

## 2. Ask Each Relevant Peer Once

Refresh `intercom` with `action: "list"`. Use it only to find candidates for the inventoried panes, not to inventory other workspaces. Names/cwds narrow candidates but do not prove a mapping. Re-list before targeting; skip requests that resolve to yourself.

Send one consolidated identity request to each candidate, using its fresh short ID. This is an operational identity check, not a task assignment; keep project/PM routing boundaries intact.

> I am preparing/checking the <workspace> Rex manifest. Please report ONLY your own full conversation UUID, exact active session-file path, intercom name, cwd, REX_SESSION and REX_BLOCK, launcher (pi/pig/pi-switch), and known resume arguments/provider/model. Use your own session metadata; if session_lineage is available, call it without sessionPath to find your current file, then read that file's first session record. Read only your two Rex location env vars, not the full environment. Unknown values should be marked unknown. Do not scan directories, inspect peers, change files, or start/stop anything. This is not a work assignment.

For yourself, use the same own-session metadata and Rex env vars. If the session-path tool is unavailable, use an already-known exact path or ask the user; do not guess env variable names for the conversation UUID.

Require the peer's full Rex session/block IDs to match the target inventory. If inherited IDs are stale, have the peer verify its own location with `rex whoami --json`. If the peer is elsewhere or two candidates conflict, ask for clarification. A peer's UUID without a pane binding does not authorize stopping that pane.

A live, explicit `--session FULL_UUID` or `--session-id FULL_UUID` in launch evidence can corroborate identity. `--resume` alone cannot. Distinguish conversation selection flags from opaque wrapper arguments; preserve the confirmed launcher on restoration.

## 3. Verify Only Exact Session Files

Read only the exact file named by the peer, current-session metadata, or user. Use a file reader/Python with an absolute path; relative Pi directory names often start with `--` and are misread as shell options.

- Parse top-level JSONL records, not substring matches across conversation content.
- Confirm the first record has `type = "session"` and its `id` equals the reported full UUID.
- `session_info` gives a display name; `model_change` gives recorded provider/model. Neither identifies the terminal pane. Read further records in that same file only if these values are actually missing and needed.
- Record session-header cwd and live peer/Rex cwd as separate evidence fields. A header cwd may predate a directory change. When they differ, ask the agent or user to confirm the intended restore cwd; record the answer and its source. Leave restore intent unresolved until confirmed, rather than silently choosing either cwd or substituting a different session file.
- Check existence/readability without dumping conversation bodies, environment variables, or secrets.

No exact file path, no responding peer, or conflicting evidence: mark the entry unknown, keep it protected, and ask the user for the missing mapping/path. One targeted request per candidate and one follow-up for a concrete conflict is the discovery budget. An unavailable peer is not permission to broaden the search.

## 4. Record Evidence And Restore Intent

Every new manifest requires a private evidence sidecar at `~/.local/state/rex/sessions/<workspace>/evidence.toml` (under `REX_SESSIONS_DIR` when configured). This separate directory keeps it out of the helper's manifest listing; the helper-generated `<workspace>.runtime.toml` is disposable and is not the evidence record.

For each pane record full Rex session/block IDs, peer or controller-assigned label, full conversation UUID, exact session-file path, binding source, verification time, session-header cwd, live cwd, confirmed restore cwd and confirmation source, provider/model evidence, and unresolved fields. Record unknown values explicitly. Durable manifest entries retain UUID, confirmed restore cwd, alias, and authoritative restore argv; runtime IDs remain transient. Recheck the live binding before lifecycle actions rather than treating old evidence as current truth.

Keep unresolved entries at `stop = "keep"`. Block both shutdown and restoration of those entries until identity and restore intent are confirmed; the keep flag alone does not prevent restoration. Report "Manifest saved; lifecycle not ready" while any required mapping or restore field is unresolved.

Launch-time provider/model flags can be stale after an in-session switch. When argv, screen, session metadata, or manifest disagree, ask the agent to confirm its current provider/model and intended resume configuration. Record launch-time and confirmed current values separately, with their sources. An unresolved conflict blocks finalizing restore intent; do not silently force the launch-time model or choose from the screen alone.

Preserve original conversation UUIDs for every role, including the controller. For an existing entry, preserve its confirmed `restore` array. For a new entry, confirm the launcher's resume syntax with its help and retain applicable known arguments. Remove one-shot initial prompts from resume commands. Never reconstruct exact argv with whitespace splitting or replace pig/pi-switch with pi by guesswork. If restore intent remains uncertain, save the gap and ask; do not claim resumability.

## Search Boundary

Allowed: target Rex metadata, fresh intercom discovery, exact returned PIDs, and exact session files supplied by their owners or the user.

Outside this workflow: recursive home/project searches, grepping all JSONL files, directory-wide session-content scans, system-wide `ps`/`lsof` sweeps, or reading helper source to invent a new discovery strategy. The current helper's snapshot/session discovery is not a substitute for this procedure.

If these sources are insufficient, report the specific missing field and request the smallest additional source. Broader search requires separate user approval of its path and purpose.
