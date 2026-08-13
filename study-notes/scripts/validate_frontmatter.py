#!/usr/bin/env python3
"""PreToolUse hook: block Write calls that produce a study-notes note with
malformed frontmatter. Deterministic, no model involved — see
skills/study-build/reference/note-template.md for the schema this enforces.

Scope: only applies to .md writes whose path has an ancestor directory
containing PLAN.md (i.e. it's inside a concept folder this plugin manages).
PLAN.md and STYLE.md themselves are exempt since they follow a different
schema. Any other markdown write in the session is left untouched.
"""
import json
import os
import re
import sys

REQUIRED_FIELDS = ["title", "concept", "topic", "created", "tags"]


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def has_plan_md_ancestor(file_path, max_levels=3):
    d = os.path.dirname(os.path.abspath(file_path))
    for _ in range(max_levels):
        if not d:
            break
        if os.path.isfile(os.path.join(d, "PLAN.md")):
            return True
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return False


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1]


def parse_simple_yaml(block):
    data = {}
    lines = block.splitlines()
    i = 0
    kv_re = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$')
    item_re = re.compile(r'^\s*-\s*(.*)$')
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        m = kv_re.match(line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "":
            items = []
            j = i + 1
            while j < len(lines) and item_re.match(lines[j]):
                items.append(item_re.match(lines[j]).group(1).strip().strip('"\''))
                j += 1
            if items:
                data[key] = items
                i = j
                continue
            data[key] = None
            i += 1
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [] if inner == "" else [x.strip().strip('"\'') for x in inner.split(",")]
            i += 1
        else:
            data[key] = val.strip('"\'')
            i += 1
    return data


def main():
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or ""
    file_text = tool_input.get("file_text")
    if file_text is None:
        file_text = tool_input.get("content", "")

    if not file_path.lower().endswith(".md"):
        sys.exit(0)

    basename = os.path.basename(file_path)
    if basename in ("PLAN.md", "STYLE.md"):
        sys.exit(0)

    if not has_plan_md_ancestor(file_path):
        sys.exit(0)

    fm_block = parse_frontmatter(file_text or "")
    if fm_block is None:
        fail(
            f"study-notes: {file_path} is missing YAML frontmatter. "
            f"Notes require --- frontmatter with {', '.join(REQUIRED_FIELDS)}."
        )

    fm = parse_simple_yaml(fm_block)

    missing = [f for f in REQUIRED_FIELDS if f not in fm or fm[f] in (None, "")]
    if missing:
        fail(
            f"study-notes: {file_path} frontmatter missing required field(s): "
            f"{', '.join(missing)}"
        )

    created = fm.get("created")
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(created)):
        fail(
            f"study-notes: {file_path} frontmatter 'created' must be YYYY-MM-DD, "
            f"got: {created!r}"
        )

    tags = fm.get("tags")
    if not isinstance(tags, list):
        fail(
            f"study-notes: {file_path} frontmatter 'tags' must be a YAML array "
            f"(e.g. [a, b] or a '- item' list), got: {tags!r}"
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
