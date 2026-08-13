---
name: study-build
description: Use when the user wants to generate notes from an existing PLAN.md (e.g. "开始写笔记", "generate the notes now", "continue building X"). Handles pilot review gating and batch generation.
---

# Study Build — Stage 2

Turn an existing `PLAN.md` into note files, one sub-topic at a time, each
written by an isolated `note-writer` subagent. State lives in `PLAN.md`'s
checkboxes and frontmatter — never track progress only in conversation.

## Procedure

1. Read `PLAN.md` from the target folder. If it doesn't exist, tell the user
   to run `study-plan` first.
2. Read `<vault>/.study/STYLE.md` (or built-in default) and this skill's
   `reference/note-template.md`.
3. **Check `pilot_reviewed` in the frontmatter.**

   - **`false`** → Pilot mode:
     1. Find the first unchecked sub-topic in `PLAN.md`.
     2. Dispatch one `note-writer` subagent for it (see "Dispatching a note"
        below).
     3. Update its checkbox to `[x]` once the file is written.
     4. **Stop.** Do not touch `pilot_reviewed` yet — that happens only after
        the user responds. Ask specific review questions, not "does this
        look ok?":
        - 表格與敘述的比例合適嗎？
        - 深度是太淺還是太深？
        - 技術術語的中英文處理方式對嗎？
        - frontmatter 欄位需要增減嗎？
     5. If the user asks for changes, apply them to the pilot note (or have
        them edit `STYLE.md`) and offer to regenerate the pilot. Once they
        approve, edit `PLAN.md` and set `pilot_reviewed: true`. Do not
        proceed to batch mode in the same turn without this explicit
        approval.

   - **`true`** → Batch mode: continue to step 4.

4. **Batch loop**, for each unchecked sub-topic in `PLAN.md` order:
   1. Compute the target path: `<major-topic-folder>/<sub-topic-name>.md`.
   2. **Idempotency check**: if the file already exists, skip it — leave the
      checkbox as-is if unchecked (inconsistent state worth flagging to the
      user) or move on if already `[x]`. Only overwrite when the user
      explicitly passed `--force` for this run.
   3. Dispatch `note-writer` for this sub-topic.
   4. On success, update the checkbox to `[x]` in `PLAN.md`.
   5. Continue to the next sub-topic.
5. **After all sub-topics under one major topic are checked**, run a
   cross-linking pass: re-read every note written for that major topic and
   add `[[wikilink]]` references between notes that are related but weren't
   linked yet (they couldn't be — earlier notes didn't know later ones would
   exist). Do this pass directly, not via a subagent, since it needs to see
   multiple notes at once.
6. Report the completed major topic to the user and ask if anything needs
   adjustment before continuing to the next major topic. Then repeat step 4
   for the next major topic.

## Dispatching a note

Use the Agent tool with `subagent_type` set to this plugin's `note-writer`
agent. Pass in the prompt:

- Sub-topic name + its major topic name.
- `concept` and `goal` from `PLAN.md`.
- Full `STYLE.md` contents.
- Full `reference/note-template.md` contents.
- The exact target file path.
- Filenames of notes already completed in this concept (for wikilink
  reference).

The subagent runs in an isolated context so note quality doesn't degrade
across a long batch — don't inline note-writing logic into this skill's own
context instead.

## Reference

- `reference/note-template.md` — required frontmatter schema and body shape
  for every note.
