# study-notes

A Claude Code plugin that turns a learning topic into a structured plan, then
batch-generates Obsidian-flavored markdown notes — one topic, one plan file,
one note at a time, each written from a clean context.

## Install

```bash
claude --plugin-dir /path/to/study-notes
```

or add it to a marketplace and `claude plugin install study-notes@<marketplace>`.

This plugin ships without a `version` field in `plugin.json` on purpose: it's
under active development, so it uses Claude Code's commit-SHA versioning
strategy — every push is a new resolvable version, and `/plugin update`
always picks it up. `claude plugin validate --strict` reports one warning
("No version specified") as a result; that's expected, not a defect. See
the "known issues" section below.

## Set up your vault's style guide

Notes are written to match a style guide that lives in **your vault**, not in
the plugin — the plugin is written once, but every vault's conventions
differ.

Create `<vault>/.study/STYLE.md` describing how you want notes written:
depth, table-vs-prose balance, how to handle bilingual technical terms,
frontmatter fields beyond the required minimum, etc. If it doesn't exist,
`study-plan` falls back to a built-in default and tells you it did.

## Usage

### 1. `study-plan` — build a plan

> "幫我規劃學習 Rust 的 ownership 系統，目標是能在 production code review 時看得懂"

You'll be asked for a `goal` if you don't give one — it changes the shape of
the resulting plan. This writes `PLAN.md` to your target folder and stops.
**Edit `PLAN.md` directly** to add, remove, or reorder topics; you don't need
to re-run this skill for that.

### 2. `study-build` — generate notes

> "開始寫筆記" / "continue building the ownership notes"

First run produces a single **pilot note** and stops, asking specific
questions about table/prose balance, depth, term handling, and frontmatter.
Approve it (or iterate) before batch mode starts — this is deliberate, so a
style mismatch costs one note, not eight.

After pilot approval, it batches through remaining sub-topics, skipping any
note file that already exists (idempotent — safe to re-run). After each
major topic finishes, it runs a cross-linking pass to backfill `[[wikilinks]]`
between that topic's notes.

### 3. `study-status` — check progress

> "study 進度如何"

Read-only: completion count, per-topic breakdown, next sub-topic, and
whether the pilot has been reviewed yet.

## How it works

- **State lives on disk**, in `PLAN.md`'s checkboxes and frontmatter — not in
  conversation context, so an interrupted or compacted session resumes
  cleanly.
- **Each note is written by an isolated subagent** (`note-writer`) so note 20
  reads the same quality as note 1.
- **A `PreToolUse` hook validates frontmatter** before any note file lands on
  disk — required fields, `YYYY-MM-DD` dates, `tags` as an array — and blocks
  the write with a specific error if something's missing. It only applies to
  `.md` files inside a folder that has `PLAN.md` as an ancestor, so it never
  interferes with unrelated markdown writes elsewhere in your project.

## Known issues / limitations

- `claude plugin validate ./study-notes --strict` reports one warning: no
  `version` in `plugin.json`. This is intentional (see Install above), not a
  bug — the acceptance bar of "zero warnings" and the "omit version"
  instruction directly conflict for this plugin, and this repo picks
  "omit version" since it's the officially documented strategy for actively
  developed plugins.
- The frontmatter validation hook can't detect a note that omits its
  frontmatter block entirely (as opposed to omitting individual required
  fields) unless the write happens under a folder with a `PLAN.md` ancestor,
  which is the only case it inspects at all — see
  `scripts/validate_frontmatter.py`.
