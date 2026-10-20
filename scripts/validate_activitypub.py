#!/usr/bin/env python3
"""Static checks for Activity Streams 2.0 / ActivityPub JSON documents.

Accepts files or directories (``*.json``, recursively). Checks required properties,
ids, same-origin rules, addressing, actor documents, and interop rules that Mastodon
and Lemmy rely on. It does not fetch anything, verify signatures, or expand JSON-LD.
A clean result means these rules hold for the documents given, not that a remote
server will accept them.

Exit status is 1 when any error is found (or any warning with --strict).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlsplit

AS_CONTEXT = "https://www.w3.org/ns/activitystreams"
PUBLIC = "https://www.w3.org/ns/activitystreams#Public"
PUBLIC_SHORT = {"as:Public", "Public"}
ACTOR_TYPES = {"Person", "Group", "Application", "Service", "Organization"}
ACTIVITY_TYPES = {
    "Accept", "Add", "Announce", "Arrive", "Block", "Create", "Delete", "Dislike",
    "Flag", "Follow", "Ignore", "Invite", "Join", "Leave", "Like", "Listen", "Move",
    "Offer", "Question", "Read", "Reject", "Remove", "TentativeAccept",
    "TentativeReject", "Travel", "Undo", "Update", "View", "EmojiReact",
}  # fmt: skip
OBJECT_REQUIRED = {
    "Create", "Update", "Delete", "Follow", "Add", "Remove", "Like", "Block", "Undo",
    "Accept", "Reject", "Announce", "Dislike", "Flag", "Move",
}  # fmt: skip
TARGET_REQUIRED = {"Add", "Remove"}
EDITABLE_TYPES = {"Note", "Article", "Page", "Question"}
ADDRESS_KEYS = ("to", "cc", "bto", "bcc", "audience")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
SKIP_DIRS = {".git", "node_modules", "vendor"}


@dataclass
class Finding:
    level: str
    code: str
    path: str
    message: str


def as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def id_of(value) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        found = value.get("id", value.get("href"))
        return found if isinstance(found, str) else None
    return None


def origin(url: str | None) -> str | None:
    if not url:
        return None
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return None
    default = {"http": 80, "https": 443}[parts.scheme]
    port = parts.port or default
    return f"{parts.scheme}://{parts.hostname.lower()}:{port}"


def json_files(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            for child in sorted(path.rglob("*.json")):
                if not any(part in SKIP_DIRS for part in child.relative_to(path).parts):
                    found.append(child)
        else:
            found.append(path)
    return found


class Checker:
    def __init__(self, label: str) -> None:
        self.label = label
        self.findings: list[Finding] = []

    def add(self, level: str, code: str, where: str, message: str) -> None:
        path = f"{self.label}#{where}" if where else self.label
        self.findings.append(Finding(level, code, path, message))

    # Entry point -----------------------------------------------------------
    def document(self, doc: dict) -> None:
        context = doc.get("@context")
        if context is None:
            self.add("warning", "W001", "", "no @context; emitted documents should declare AS2")
        elif AS_CONTEXT not in as_list(context):
            self.add("warning", "W002", "", f"@context does not include {AS_CONTEXT}")
        self.node(doc, "", top=True)

    # Any node ------------------------------------------------------------------
    def node(self, doc: dict, where: str, *, top: bool) -> None:
        kind = doc.get("type")
        if not kind:
            self.add("error", "E003", where, "'type' is missing")
            return
        types = set(as_list(kind))
        doc_id = doc.get("id")
        if doc_id is None:
            if top:
                self.add("error", "E004", where, "'id' is missing")
        elif not isinstance(doc_id, str) or origin(doc_id) is None:
            self.add("error", "E005", where, f"id {doc_id!r} is not an absolute http(s) URL")
        elif urlsplit(doc_id).scheme != "https":
            self.add("warning", "W003", where, "id is not https")

        for key in ("published", "updated", "deleted"):
            value = doc.get(key)
            if value is not None and (not isinstance(value, str) or not DATE_RE.match(value)):
                self.add("error", "E040", where, f"{key} {value!r} is not RFC 3339")
        for key, value in doc.items():
            if isinstance(value, list) and not value and key != "orderedItems":
                self.add("warning", "W023", where, f"empty array {key!r}; omit it instead")
        for key in ADDRESS_KEYS:
            for value in as_list(doc.get(key)):
                if value in PUBLIC_SHORT:
                    self.add("warning", "W017", where, f"{key} uses {value!r}; emit {PUBLIC}")

        if types & ACTOR_TYPES:
            self.actor(doc, where)
        if types & ACTIVITY_TYPES:
            self.activity(doc, where, types, top=top)
        else:
            self.object(doc, where, types)

    # Actors --------------------------------------------------------------------
    def actor(self, doc: dict, where: str) -> None:
        actor_id = doc.get("id") if isinstance(doc.get("id"), str) else None
        for key in ("inbox", "outbox"):
            value = id_of(doc.get(key))
            if not value:
                self.add("error", "E030", where, f"actor has no {key}")
            elif actor_id and origin(value) != origin(actor_id):
                self.add("error", "E037", where, f"{key} is not on the actor's origin")
        if not isinstance(doc.get("preferredUsername"), str):
            self.add("error", "E031", where, "actor has no preferredUsername (Mastodon needs it)")
        key = doc.get("publicKey")
        keys = [k for k in as_list(key) if isinstance(k, dict)]
        if not keys:
            self.add("error", "E032", where, "actor has no publicKey {id, owner, publicKeyPem}")
        for item in keys:
            missing = [k for k in ("id", "owner", "publicKeyPem") if not item.get(k)]
            if missing:
                self.add("error", "E032", where, f"publicKey lacks {', '.join(missing)}")
                continue
            if actor_id and item["owner"] != actor_id:
                self.add("error", "E033", where, "publicKey.owner differs from the actor id")
            if actor_id and not str(item["id"]).startswith(actor_id):
                self.add("warning", "W034", where, "publicKey.id is not under the actor id")
        for coll in ("followers", "following"):
            if not doc.get(coll):
                self.add("warning", "W035", where, f"actor has no {coll} collection")

    # Activities ----------------------------------------------------------------
    def activity(self, doc: dict, where: str, types: set[str], *, top: bool) -> None:
        actor = doc.get("actor")
        actor_id = id_of(actor)
        if actor is None:
            self.add("error", "E010", where, "activity has no actor")
        elif isinstance(actor, dict):
            self.add("warning", "W011", where, "actor is embedded; send the actor id string")
        doc_id = doc.get("id") if isinstance(doc.get("id"), str) else None
        if doc_id and actor_id and origin(doc_id) != origin(actor_id):
            self.add("error", "E014", where, "activity id and actor have different origins")
        if types & OBJECT_REQUIRED and doc.get("object") is None:
            self.add("error", "E012", where, f"{'/'.join(sorted(types))} requires 'object'")
        if types & TARGET_REQUIRED and doc.get("target") is None:
            self.add("error", "E013", where, f"{'/'.join(sorted(types))} requires 'target'")
        if top:
            for key in ("bto", "bcc"):
                if doc.get(key) is not None:
                    self.add("warning", "W016", where, f"{key} present; strip before delivery")

        for index, obj in enumerate(as_list(doc.get("object"))):
            if not isinstance(obj, dict):
                continue
            sub = f"{where}/object" + (f"[{index}]" if isinstance(doc["object"], list) else "")
            self.embedded(doc, obj, sub, types, actor_id)

    def embedded(self, parent: dict, obj: dict, where: str, types: set[str], actor_id) -> None:
        obj_types = set(as_list(obj.get("type")))
        obj_id = id_of(obj)
        if types & {"Create", "Update"}:
            if obj_id and actor_id and origin(obj_id) != origin(actor_id):
                self.add("error", "E015", where, "embedded object is not on the actor's origin")
            owner = id_of(obj.get("attributedTo"))
            if owner and actor_id and owner != actor_id and not (obj_types & ACTOR_TYPES):
                self.add("error", "E016", where, "object attributedTo differs from the actor")
        if "Update" in types:
            if obj_types & ACTOR_TYPES and obj_id and actor_id and obj_id != actor_id:
                self.add("error", "E017", where, "Update of an actor must come from that actor")
            if obj_types & EDITABLE_TYPES and not obj.get("updated"):
                self.add("warning", "W020", where, "Update without 'updated'; Mastodon ignores it")
        if "Undo" in types and id_of(obj.get("actor")) not in (None, actor_id):
            self.add("error", "E018", where, "undone activity has a different actor")
        if types & {"Accept", "Reject"} and not obj_id:
            self.add("error", "E019", where, "accepted/rejected activity has no id to match")
        if "Note" in obj_types or "Page" in obj_types:
            self.mentions(obj, parent, where)
        self.node(obj, where, top=False)

    # Objects ---------------------------------------------------------------------
    def object(self, doc: dict, where: str, types: set[str]) -> None:
        if "Page" in types and not doc.get("name"):
            self.add("error", "E021", where, "Page has no 'name' (Lemmy requires a title)")

    def mentions(self, obj: dict, parent: dict, where: str) -> None:
        addressed = {
            id_of(v) for k in ("to", "cc") for v in as_list(obj.get(k)) + as_list(parent.get(k))
        }
        for tag in as_list(obj.get("tag")):
            if isinstance(tag, dict) and tag.get("type") == "Mention":
                href = id_of(tag)
                if href and href not in addressed:
                    self.add("warning", "W022", where, f"mentioned {href} is not in to/cc")


def validate_file(path: Path, label: str | None = None) -> list[Finding]:
    checker = Checker(label or path.as_posix())
    if not path.is_file():
        checker.add("error", "E000", "", "file does not exist")
        return checker.findings
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        checker.add("error", "E001", "", f"invalid JSON: {exc}")
        return checker.findings
    if not isinstance(doc, dict):
        checker.add("error", "E002", "", "document must be a JSON object")
        return checker.findings
    checker.document(doc)
    return checker.findings


def validate(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        if not path.exists():
            findings.append(Finding("error", "E000", path.as_posix(), "path does not exist"))
    for path in json_files([p for p in paths if p.exists()]):
        findings.extend(validate_file(path))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", type=Path, nargs="+", help="JSON files or directories")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args(argv)

    findings = validate(args.paths)
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
