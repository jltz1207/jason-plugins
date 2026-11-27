# wsl-sync

Keep Claude Code sessions in WSL2 and Windows in step, so `/resume` on either side lists every session.

WSL stores transcripts in `~/.claude/projects/-mnt-c-Users-me/`, Windows in `%USERPROFILE%\.claude\projects\C--Users-me\`.
The skill copies each session to the other side, rewrites its `cwd` field (`/mnt/c/...` <-> `C:\...`), and keeps the longer copy when both sides have the same session.

## Install

```
/plugin install wsl-sync --marketplace jltz1207/jason-plugins
```

Install it on both the WSL and the Windows Claude Code if you want to run it from either side.

## Skills

| Skill | Command | Output |
|---|---|---|
| sync-sessions | `/wsl-sync:sync-sessions [--apply] [--include-active]` | Dry-run plan, then (after confirmation) copies sessions both ways and reports copied / updated / conflict counts |

## What it syncs

- `projects/<dir>/<id>.jsonl` and its `<id>/` folder (subagent transcripts, tool results).
- Not synced: `memory/`, `file-history/`, `history.jsonl`, settings.
- Sessions whose `cwd` is WSL-native (`/`, `/home/...`) cannot be opened from Windows and are skipped.
- Sessions modified in the last 5 minutes are treated as active and skipped.
- Overwritten files are backed up to `<target>/.claude/backups/session-sync/<timestamp>/`.

The script is `skills/sync-sessions/scripts/sync_sessions.py` (Python 3, stdlib only) and can be run directly: `python3 sync_sessions.py --help`.
