---
name: study-plan
description: Use when the user wants to plan out a new learning topic — creates a structured PLAN.md before any notes are written. Trigger phrases include "帮我规划/规劃 <topic>", "make a study plan for X", "I want to learn X".
---

# Study Plan — Stage 1

Turn a learning topic into a structured `PLAN.md` file. This is the *only*
output of this skill — do not write any note content here.

## Inputs

- `concept`: the topic to study.
- `goal`: what mastery level the user wants (e.g. "能用來寫 production code" vs
  "能教別人"). **If the user did not give a goal, ask for it before doing
  anything else.** Do not guess — the plan structure differs significantly
  by goal depth.
- Target folder: where `PLAN.md` and the note folders will live (ask if not
  obvious from context, e.g. an Obsidian vault path).

## Procedure

1. Confirm `concept` and `goal`. Ask if either is missing or ambiguous.
2. Read `<vault>/.study/STYLE.md` if it exists. If it doesn't, use sensible
   built-in defaults (concise, table-friendly, bilingual technical terms) and
   tell the user they can create `.study/STYLE.md` to customize future notes.
3. **Web search the topic before drafting the plan.** Your training data has
   a cutoff; the topic may have new sub-areas, tools, or best practices since
   then. Do not skip this step even if you feel confident about the topic.
4. Draft the plan: 3–8 major topics, each with 3–8 sub-topics. If you land
   outside that range, the breakdown granularity is wrong — merge or split.
   See `reference/plan-schema.md` for the exact file format.
5. Write `PLAN.md` to the target folder. This is a **file**, not a chat
   message — the user reviews and edits it directly on disk.
6. Stop. Tell the user explicitly:
   - Where `PLAN.md` was written.
   - That they can edit it directly (add/remove/reorder sub-topics) without
     re-running this skill.
   - That running `study-build` next will start with a single pilot note.

## Reference

- `reference/plan-schema.md` — full `PLAN.md` format, frontmatter fields, and
  edge cases (topic count out of range, existing PLAN.md, etc).
