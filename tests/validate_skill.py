#!/usr/bin/env python3
"""Checks SKILL.md against the Agent Skills authoring rules.

- name: 1-64 chars, lowercase letters, digits and hyphens; no reserved words
- description: 1-1024 chars, no XML tags
- body: under 500 lines
- every relative link in SKILL.md points to a file that exists, one level deep

Run: python3 tests/validate_skill.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "phaselens" / "SKILL.md"
RESERVED = ("anthropic", "claude")


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        raise SystemExit("SKILL.md: missing YAML frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, match.group(2)


def main():
    text = SKILL.read_text(encoding="utf-8")
    fields, body = frontmatter(text)
    errors = []

    name = fields.get("name", "")
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?", name):
        errors.append(f"name {name!r} must be 1-64 lowercase letters, digits or hyphens")
    if any(word in name for word in RESERVED):
        errors.append(f"name {name!r} contains a reserved word")

    description = fields.get("description", "")
    if not 1 <= len(description) <= 1024:
        errors.append(f"description is {len(description)} chars (must be 1-1024)")
    if re.search(r"<[^>]+>", description):
        errors.append("description must not contain XML tags")

    lines = body.count("\n") + 1
    if lines >= 500:
        errors.append(f"SKILL.md body is {lines} lines (keep under 500)")

    for target in re.findall(r"\]\(((?!https?://)[^)#]+)\)", body):
        path = SKILL.parent / target
        if not path.is_file():
            errors.append(f"broken link: {target}")
        elif len(pathlib.PurePosixPath(target).parts) > 2:
            errors.append(f"reference nested too deep: {target}")

    if errors:
        print("\n".join(f"FAIL  {e}" for e in errors))
        sys.exit(1)
    print(f"OK    {SKILL.relative_to(ROOT)}: name={name}, "
          f"description={len(description)} chars, body={lines} lines")


if __name__ == "__main__":
    main()
