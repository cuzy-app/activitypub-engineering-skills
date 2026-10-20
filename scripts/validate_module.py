#!/usr/bin/env python3
"""Static checks for a HumHub module directory.

Checks module.json, config.php, Module.php, migration naming, and a few risky SQL
patterns. It does not run PHP, boot HumHub, or replace Codeception. A clean result
means these structural rules hold, not that the module works.

Exit status is 1 when any error is found (or any warning with --strict).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED_KEYS = ("id", "version", "name", "description")
ID_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
VERSION_RE = re.compile(r"^\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?$")
MIGRATION_FILE_RE = re.compile(r"^m\d{6}_\d{6}_[A-Za-z0-9_]+\.php$")
MIGRATION_CLASS_RE = re.compile(r"^\s*(?:final\s+|abstract\s+)?class\s+(m\d{6}_\d{6}_\w+)", re.M)
CONFIG_ID_RE = re.compile(r"""['"]id['"]\s*=>\s*['"]([^'"]+)['"]""")
CONFIG_CLASS_RE = re.compile(r"""['"]class['"]\s*=>""")
CONFIG_NAMESPACE_RE = re.compile(r"""['"]namespace['"]\s*=>\s*['"]([^'"]+)['"]""")
RISKY_SQL_RES = (
    (
        re.compile(r"""createCommand\(\s*(?:"[^"\n]*\$\w|'[^'\n]*'\s*\.)"""),
        "createCommand() receives SQL built by interpolation or concatenation; bind parameters",
    ),
    (
        re.compile(r"""->(?:and|or)?[wW]here\(\s*"[^"\n]*\$\w"""),
        "where() condition interpolates a variable into the string; use array form or bindings",
    ),
)
SKIP_DIRS = {"vendor", "node_modules", ".git", "tests"}


@dataclass
class Finding:
    level: str
    code: str
    path: str
    message: str


def php_files(root: Path) -> list[Path]:
    found = []
    for path in sorted(root.rglob("*.php")):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        found.append(path)
    return found


def validate(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    def add(level: str, code: str, path: Path | str, message: str) -> None:
        rel = path.relative_to(root).as_posix() if isinstance(path, Path) else path
        findings.append(Finding(level, code, rel, message))

    if not root.is_dir():
        add("error", "E000", str(root), "module directory does not exist")
        return findings

    # module.json -----------------------------------------------------------
    manifest_id: str | None = None
    manifest_path = root / "module.json"
    if not manifest_path.is_file():
        add("error", "E001", "module.json", "module.json is missing")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            manifest = None
            add("error", "E002", manifest_path, f"invalid JSON: {exc}")
        if isinstance(manifest, dict):
            for key in REQUIRED_KEYS:
                value = manifest.get(key)
                if not isinstance(value, str) or not value.strip():
                    add("error", "E003", manifest_path, f"required key {key!r} is missing or empty")
            manifest_id = manifest.get("id") if isinstance(manifest.get("id"), str) else None
            if manifest_id and not ID_RE.match(manifest_id):
                add("error", "E004", manifest_path, f"id {manifest_id!r} must be lowercase")
            version = manifest.get("version")
            if isinstance(version, str) and version and not VERSION_RE.match(version):
                add(
                    "error",
                    "E005",
                    manifest_path,
                    f"version {version!r} is not MAJOR.MINOR[.PATCH]",
                )
            humhub = manifest.get("humhub")
            min_version = humhub.get("minVersion") if isinstance(humhub, dict) else None
            if not isinstance(min_version, str) or not min_version.strip():
                add("error", "E006", manifest_path, "humhub.minVersion is missing")
        elif manifest is not None:
            add("error", "E002", manifest_path, "module.json must contain a JSON object")

    # Module.php and config.php ----------------------------------------------
    if not (root / "Module.php").is_file():
        add("error", "E010", "Module.php", "Module.php is missing")
    config_path = root / "config.php"
    if not config_path.is_file():
        add("error", "E011", "config.php", "config.php is missing")
    else:
        config = config_path.read_text(encoding="utf-8")
        id_match = CONFIG_ID_RE.search(config)
        if not id_match:
            add("error", "E012", config_path, "config.php has no 'id' entry")
        elif manifest_id and id_match.group(1) != manifest_id:
            add(
                "error",
                "E013",
                config_path,
                f"id {id_match.group(1)!r} differs from module.json id {manifest_id!r}",
            )
        if not CONFIG_CLASS_RE.search(config):
            add("error", "E014", config_path, "config.php has no 'class' entry")
        if not CONFIG_NAMESPACE_RE.search(config):
            add("error", "E015", config_path, "config.php has no 'namespace' entry")

    # Migrations -------------------------------------------------------------
    migrations = root / "migrations"
    if migrations.is_dir():
        for path in sorted(migrations.glob("*.php")):
            if not MIGRATION_FILE_RE.match(path.name):
                add("error", "E020", path, "name must match mYYMMDD_HHMMSS_description.php")
                continue
            declared = MIGRATION_CLASS_RE.search(path.read_text(encoding="utf-8"))
            if not declared:
                add("error", "E021", path, "no migration class declaration found")
            elif declared.group(1) != path.stem:
                add("error", "E022", path, f"class {declared.group(1)} must equal file name")

    # Risky patterns, tests, composer ---------------------------------------
    for path in php_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern, message in RISKY_SQL_RES:
            if pattern.search(text):
                add("warning", "W010", path, message)

    composer = root / "composer.json"
    if composer.is_file():
        try:
            data = json.loads(composer.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            add("error", "E030", composer, f"invalid JSON: {exc}")
        else:
            if isinstance(data, dict) and data.get("type") != "humhub-module":
                add("warning", "W030", composer, "composer type is not 'humhub-module'")
    else:
        add("warning", "W031", "composer.json", "composer.json not found")

    if not (root / "tests").is_dir():
        add("warning", "W040", "tests/", "no tests directory")

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module_dir", type=Path)
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args(argv)

    root = args.module_dir.resolve()
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
