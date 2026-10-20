#!/usr/bin/env python3
"""Install the knowledge-only skill bundle into an agent's skills directory.

Copies SKILL.md, references/ and scripts/validate_activitypub.py. It never edits client
settings and never registers hooks. An existing installation is replaced only with
--force, and the replacement is staged before the old copy is touched.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKILL_NAME = "activitypub-engineering"
BUNDLE_FILES = ("SKILL.md", "scripts/validate_activitypub.py")
BUNDLE_DIRS = ("references",)

# Defaults, not guarantees. See docs/CLIENT_COMPATIBILITY.md.
CLIENT_DIRS = {
    "claude": ".claude/skills",
    "codex": ".codex/skills",
    "cursor": ".cursor/skills",
    "gemini": ".gemini/skills",
    "agents": ".agents/skills",
}


def destination(client: str, project: Path | None, dest: Path | None) -> Path:
    if dest is not None:
        return dest / SKILL_NAME
    base = project if project is not None else Path.home()
    return base / CLIENT_DIRS[client] / SKILL_NAME


def stage_bundle(source: Path, staging: Path) -> None:
    for rel in BUNDLE_FILES:
        src = source / rel
        if not src.is_file():
            raise FileNotFoundError(f"bundle file missing: {rel}")
        target = staging / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    for rel in BUNDLE_DIRS:
        src = source / rel
        if not src.is_dir():
            raise FileNotFoundError(f"bundle directory missing: {rel}")
        shutil.copytree(src, staging / rel)


def install(source: Path, target: Path, *, force: bool, dry_run: bool) -> str:
    exists = target.exists()
    if exists and not force:
        raise FileExistsError(f"{target} already exists; use --force to replace it")
    if dry_run:
        action = "replace" if exists else "create"
        return f"dry run: would {action} {target}"

    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.parent / f".{SKILL_NAME}.staging"
    backup = target.parent / f".{SKILL_NAME}.old"
    for leftover in (staging, backup):
        if leftover.exists():
            shutil.rmtree(leftover)
    try:
        stage_bundle(source, staging)
        if exists:
            target.rename(backup)
        staging.rename(target)
    except Exception:
        if backup.exists() and not target.exists():
            backup.rename(target)
        if staging.exists():
            shutil.rmtree(staging)
        raise
    if backup.exists():
        shutil.rmtree(backup)
    return f"installed {target}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=sorted(CLIENT_DIRS), default="claude")
    parser.add_argument("--project", type=Path, help="install into PROJECT/<client dir>")
    parser.add_argument("--dest", type=Path, help="skills directory override")
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    target = destination(args.client, args.project, args.dest)
    try:
        print(install(args.source.resolve(), target, force=args.force, dry_run=args.dry_run))
    except (FileExistsError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
