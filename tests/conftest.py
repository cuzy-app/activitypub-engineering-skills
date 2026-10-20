import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

ACTOR = "https://a.example/users/alice"
PUBLIC = "https://www.w3.org/ns/activitystreams#Public"


@pytest.fixture
def root() -> Path:
    return ROOT


@pytest.fixture
def write_doc(tmp_path):
    """Write a JSON document into tmp_path and return its path."""

    def factory(doc, name="doc.json"):
        path = tmp_path / name
        path.write_text(doc if isinstance(doc, str) else json.dumps(doc))
        return path

    return factory


@pytest.fixture
def person():
    return {
        "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/security/v1"],
        "id": ACTOR,
        "type": "Person",
        "preferredUsername": "alice",
        "inbox": ACTOR + "/inbox",
        "outbox": ACTOR + "/outbox",
        "followers": ACTOR + "/followers",
        "following": ACTOR + "/following",
        "publicKey": {"id": ACTOR + "#main-key", "owner": ACTOR, "publicKeyPem": "PEM"},
    }


@pytest.fixture
def create_note():
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": ACTOR + "/notes/1/activity",
        "type": "Create",
        "actor": ACTOR,
        "to": [PUBLIC],
        "cc": [ACTOR + "/followers"],
        "object": {
            "id": ACTOR + "/notes/1",
            "type": "Note",
            "attributedTo": ACTOR,
            "to": [PUBLIC],
            "cc": [ACTOR + "/followers"],
            "content": "<p>Hi</p>",
            "published": "2026-10-20T12:00:00Z",
        },
    }


@pytest.fixture
def make_bundle(tmp_path, root):
    """Copy the skill bundle into tmp_path so tests can break it safely."""
    import shutil

    def factory():
        target = tmp_path / "bundle"
        shutil.copytree(
            root,
            target,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".ruff_cache"),
        )
        return target

    return factory
