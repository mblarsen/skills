# Skills

Agent skills for my development workflow. Each skill contains its instructions and any supporting scripts or references.

## Install

Install a skill with the [skills CLI](https://skills.sh/):

```sh
npx skills add mblarsen/skills --skill rex-workspace-controller
```

Choose your agent and installation scope when prompted.
The repository must be pushed to GitHub before this command can install its contents.

## Available Skills

| Skill | Use it to |
| --- | --- |
| [rex-workspace-controller](skills/rex-workspace-controller/SKILL.md) | Save, pause, resume, and inspect a Rex workspace without confusing agent sessions with terminal panes. |

### Rex Workspace Controller

Requirements: [Rex](https://www.superlogical.com/rex), Python 3.11+, and `ps`.
The bundled helper supports Pi-compatible session files. Intercom provides agent identity checks when available.

Nominate an agent with:

> You are the Rex workspace controller for the side-projects session.

Nomination resolves the workspace and checks its manifest. If none exists, the controller asks permission to create one and waits before collecting worker identities. It does not stop agents or change files.
After approval, identity discovery uses target Rex metadata and direct peer confirmation, then reads only exact session files. Missing values become explicit questions, not broad filesystem searches.
Then request an operation:

- **Save the workspace**: record agent identities, restart commands, and layout in a TOML manifest.
- **Pause the workspace**: stop its agents while keeping the controller running.
- **Resume the workspace**: restore missing agents and layout from the manifest.
- **Show workspace status**: compare the manifest with live panes.

Manifests stay local under `~/.local/state/rex/sessions/`. They are not part of this repository.

The helper is experimental. Partial split operations can misidentify panes, and automatic snapshots can discard paused entries.
Read the [helper reference](skills/rex-workspace-controller/HELPER.md) before lifecycle operations.

## Local Development

```sh
git clone https://github.com/mblarsen/skills.git
cd skills
python3 skills/rex-workspace-controller/test_rex_sessions.py
```

The regression test mocks Rex calls. It does not stop or start live agents.
Test lifecycle changes in a disposable Rex workspace before using them on a working team.

## License

[MIT](LICENSE).
