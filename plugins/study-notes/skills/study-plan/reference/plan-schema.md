# `PLAN.md` format

`PLAN.md` is the single source of truth for study progress. It lives in the
target folder (e.g. the Obsidian vault subfolder for this concept) and is
read/written by both `study-plan` and `study-build`.

## Frontmatter

```yaml
---
concept: <topic name>
goal: <what the user wants to be able to do after studying this>
created: <YYYY-MM-DD>
style: ../.study/STYLE.md
pilot_reviewed: false
---
```

| Field | Meaning |
| --- | --- |
| `concept` | The topic being studied. Also used as a label in status reports. |
| `goal` | The target mastery level. Drives note depth — keep it as the user stated it, don't paraphrase away nuance. |
| `created` | ISO date the plan was generated. |
| `style` | Relative path from `PLAN.md` to the vault's style guide. |
| `pilot_reviewed` | Gates Stage 2 batch mode. `false` until the user approves the first (pilot) note. `study-build` flips this to `true` after approval — never set it to `true` in Stage 1. |

## Body

```markdown
## 1. <major topic name>
- [ ] 1.1 <sub-topic>
- [ ] 1.2 <sub-topic>

## 2. <major topic name>
- [ ] 2.1 <sub-topic>
```

Rules:

- Each major topic is a `## <n>. <name>` heading. `<name>` becomes the output
  folder name for that topic's notes (sanitize for filesystem safety: no
  `/ \ : * ? " < > |`).
- Each sub-topic is a markdown checkbox `- [ ] <n>.<m> <name>`. The checkbox
  state *is* the progress tracker — `study-build` reads and writes these
  directly, never a separate progress file.
- 3–8 major topics. 3–8 sub-topics per major topic. Outside this range means
  the granularity is wrong: topics too broad (under 3) will produce shallow
  notes, or too fragmented (over 8) will produce redundant micro-notes.

## Edge cases

- **`PLAN.md` already exists at the target folder**: don't silently
  overwrite. Ask the user whether they want to regenerate it (losing any
  manual edits and progress checkboxes) or pick a different target.
- **User edits `PLAN.md` directly** (adds/removes sub-topics, reorders): this
  is expected and supported. `study-build` always re-reads the file fresh, so
  edits take effect on the next run with no extra step.
- **Sub-topic checked but note file missing**: treat as inconsistent state —
  surface it to the user rather than silently regenerating or silently
  leaving it checked.
