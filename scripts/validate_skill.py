#!/usr/bin/env python3
"""Validate this skill bundle: metadata, routing, local links, and size budgets.

Static checks only. This does not prove that any agent client activates the skill.
Exit status is 1 when any error is found.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

MAX_SKILL_LINES = 200
MAX_REFERENCE_LINES = 600
MAX_DESCRIPTION_CHARS = 1024
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
REQUIRED_FILES = ("SKILL.md", "README.md", "AGENTS.md", "CHANGELOG.md")
SKIP_DIRS = {".git", "node_modules", "vendor", ".pytest_cache", "__pycache__", ".ruff_cache"}


@dataclass
class Finding:
    level: str  # "error" or "warning"
    code: str
    path: str
    message: str


def parse_frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    """Parse a flat ``key: value`` frontmatter block. Returns (data, error)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "SKILL.md must start with a '---' frontmatter block"
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data, None
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return data, f"unparseable frontmatter line: {line!r}"
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip().strip("'\"")
    return data, "frontmatter block is not closed with '---'"


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return "\n".join(lines[index + 1 :])
    return text


def local_links(text: str) -> list[str]:
    """Return link targets outside fenced code blocks that point at local files."""
    targets: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for target in LINK_RE.findall(line):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            targets.append(target.split("#", 1)[0])
    return [t for t in targets if t]


def markdown_files(root: Path) -> list[Path]:
    found = []
    for path in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        found.append(path)
    return found


def validate(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    def add(level: str, code: str, path: Path | str, message: str) -> None:
        rel = path.relative_to(root).as_posix() if isinstance(path, Path) else path
        findings.append(Finding(level, code, rel, message))

    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            add("error", "S001", name, "required file is missing")

    skill_path = root / "SKILL.md"
    skill_text = ""
    if skill_path.is_file():
        skill_text = skill_path.read_text(encoding="utf-8")
        meta, problem = parse_frontmatter(skill_text)
        if problem:
            add("error", "S002", skill_path, problem)
        name = meta.get("name", "")
        if not name:
            add("error", "S003", skill_path, "frontmatter 'name' is missing")
        elif not NAME_RE.match(name) or len(name) > 64:
            add("error", "S004", skill_path, f"name {name!r} must be lowercase-hyphenated, <= 64")
        description = meta.get("description", "")
        if not description:
            add("error", "S005", skill_path, "frontmatter 'description' is missing")
        elif len(description) > MAX_DESCRIPTION_CHARS:
            add("error", "S006", skill_path, f"description exceeds {MAX_DESCRIPTION_CHARS} chars")
        line_count = len(skill_text.splitlines())
        if line_count > MAX_SKILL_LINES:
            add("error", "S007", skill_path, f"{line_count} lines exceeds budget {MAX_SKILL_LINES}")

    references = (
        sorted((root / "references").glob("*.md")) if (root / "references").is_dir() else []
    )
    if not references:
        add("error", "S010", "references/", "no reference files found")

    routed = {
        (skill_path.parent / target).resolve()
        for target in local_links(strip_frontmatter(skill_text))
    }
    for ref in references:
        if ref.resolve() not in routed:
            add("error", "S011", ref, "reference is not linked from SKILL.md (unrouted)")
        lines = len(ref.read_text(encoding="utf-8").splitlines())
        if lines > MAX_REFERENCE_LINES:
            add("warning", "S012", ref, f"{lines} lines exceeds budget {MAX_REFERENCE_LINES}")

    for md in markdown_files(root):
        text = md.read_text(encoding="utf-8")
        for target in local_links(strip_frontmatter(text)):
            if not (md.parent / target).exists():
                add("error", "S020", md, f"broken local link: {target}")

    evals = root / "evals" / "trigger_cases.json"
    if evals.is_file():
        try:
            cases = json.loads(evals.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            add("error", "S030", evals, f"invalid JSON: {exc}")
        else:
            if not isinstance(cases, list) or not cases:
                add("error", "S031", evals, "expected a non-empty list of cases")
            else:
                for index, case in enumerate(cases):
                    ok = (
                        isinstance(case, dict)
                        and isinstance(case.get("prompt"), str)
                        and case.get("expect") in {"activate", "not_activate", "handoff"}
                    )
                    if not ok:
                        add(
                            "error",
                            "S032",
                            evals,
                            f"case {index} needs 'prompt' and a valid 'expect'",
                        )

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    findings = validate(root)
    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        for f in findings:
            print(f"{f.level.upper():7} {f.code} {f.path}: {f.message}")
        print(f"{len(errors)} error(s), {len(warnings)} warning(s)")

    failed = bool(errors) or (args.strict and bool(warnings))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
