---
name: sync-sessions
description: Two-way sync of Claude Code session transcripts between WSL2 and Windows (~/.claude/projects and %USERPROFILE%\.claude\projects), rewriting cwd so /resume on either side lists every session. Use when the user runs /wsl-sync:sync-sessions or asks to sync / copy / move Claude sessions between WSL and Windows, or says a session from the other side is missing in /resume.
argument-hint: "[--apply] [--include-active]"
---

# /wsl-sync:sync-sessions

Copy Claude Code sessions between the WSL and Windows `~/.claude/projects` folders, so `/resume` works from both.

## Script

`scripts/sync_sessions.py` beside this file (Python 3, stdlib only). It finds both roots by itself:

- In WSL: `python3 <skill-dir>/scripts/sync_sessions.py`
- In Windows: `python <skill-dir>\scripts\sync_sessions.py` (reaches WSL through `\\wsl.localhost\<distro>`; WSL must be running)

Options: `--apply` (write; default is dry-run), `--include-active`, `--active-minutes N` (default 5), `-v` (list every session), `--wsl-root` / `--win-root` (override detection).

## Steps

1. Run a dry-run (no `--apply`). If the user's arguments include `--include-active`, pass it too.
2. Summarise the plan for the user in Traditional Chinese: how many sessions go each way, which projects, and any conflicts or unmappable sessions.
3. Ask before writing, unless the user already passed `--apply`. Then run again with `--apply` (and the same flags).
4. Report the result: counts, conflicts, and the backup folder if any file was overwritten. Tell the user they can now `/resume` (or `claude --resume`) from the project folder on the other side.

## Rules

- Never delete session files. The script only adds or replaces with a longer copy, and backs up what it replaces.
- The current session is written to as you work, so it is skipped as active. Say so; do not force it with `--include-active` unless the user asks.
- Conflicts mean both copies of the same session grew separately after an earlier sync. The script leaves both untouched; list the session ids and let the user decide (e.g. keep one by deleting the other side's file themselves).
- Unmappable sessions have a WSL-native cwd (`/`, `/home/...`) with no Windows path; they stay WSL-only.
- Only transcripts are synced: not `memory/`, `file-history/`, or settings.

## Example

```
> /wsl-sync:sync-sessions

Dry-run：
- WSL -> Windows：109 個 session（C--Users-jthlee 41、C--Repos-mbx 14 ...）
- Windows -> WSL：9 個（-mnt-c-Users-jthlee）
- 略過：2 個進行中、3 個 cwd=/ 無法對應
要執行 --apply 嗎？
```
