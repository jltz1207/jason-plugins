# Note format

Every note `study-build` asks `note-writer` to produce follows this shape.
`scripts/validate_frontmatter.py` enforces the frontmatter part of this
contract before the file is allowed to land on disk.

## Frontmatter (required)

```yaml
---
title: <sub-topic name, matches PLAN.md exactly>
concept: <concept from PLAN.md>
topic: <major topic name this sub-topic belongs to>
created: <YYYY-MM-DD>
tags: [<lowercase-kebab-case-tags>]
status: draft
---
```

| Field | Rule |
| --- | --- |
| `title` | Non-empty string. |
| `concept` | Non-empty string, matches `PLAN.md`'s `concept`. |
| `topic` | Non-empty string, matches the `## <n>. <name>` heading this sub-topic is under. |
| `created` | `YYYY-MM-DD`. |
| `tags` | YAML array, may be empty (`[]`) but must be a list, not a bare string. |
| `status` | One of `draft`, `reviewed`. `note-writer` always writes `draft`; a human flips it to `reviewed`, never the plugin. |

`PLAN.md` and `.study/STYLE.md` are **not** notes and don't follow this
schema — the validation hook only applies it to files under the concept's
output folders, not to `PLAN.md` or `STYLE.md` itself.

## Body shape

```markdown
# <title>

## Overview
<2-4 sentences: what this is, why it matters for the stated goal>

## Details
<tables where the content is naturally tabular (comparisons, options,
parameters); prose where it isn't. Don't force a table just to have one.>

## Examples
<concrete example(s). Code blocks with language tags where applicable.>

## Related
<wikilinks to other notes in this concept, e.g. [[1.2 sub-topic name]].
Left empty until the cross-linking pass if no obvious links exist yet.>
```

Adjust section names/depth to what `STYLE.md` specifies if it overrides this
default — `STYLE.md` wins when the two disagree.

## Verification

Any claim the writer isn't confident about — version numbers, API behavior,
"current best practice" — gets a web search. If still unverifiable, mark it
inline as `[VERIFY]` rather than stating it as fact.
