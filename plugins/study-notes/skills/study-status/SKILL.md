---
name: study-status
description: Use when the user asks for progress on a study plan (e.g. "study 進度如何", "how far along is X"). Reads PLAN.md and reports status — no writes.
---

# Study Status

Read-only progress report for an existing `PLAN.md`.

## Procedure

1. Locate `PLAN.md` (ask the user which topic/folder if not obvious from
   context).
2. Read the frontmatter and body.
3. Report:
   - `concept` and `goal`.
   - Overall completion: `<checked> / <total>` sub-topics.
   - Per major-topic breakdown: `<checked>/<total>` for each `## <n>. <name>`.
   - The next unchecked sub-topic (what `study-build` would produce next).
   - Whether `pilot_reviewed` is `true` or `false` — if `false`, note that
     `study-build` will produce a pilot note and stop for review before any
     batch work happens.

Do not modify `PLAN.md` or write any note files — this skill only reads and
reports.
