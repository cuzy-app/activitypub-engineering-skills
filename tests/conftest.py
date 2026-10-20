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
def make_module(tmp_path):
    """Build a valid minimal module in tmp_path and return its path."""

    def factory(manifest_overrides=None, config=None, migrations=None, extra_php=None):
        module = tmp_path / "mod"
        module.mkdir()
        manifest = {
            "id": "demo",
            "version": "1.0.0",
            "name": "Demo",
            "description": "Demo module",
            "humhub": {"minVersion": "1.16"},
        }
        manifest.update(manifest_overrides or {})
        manifest = {k: v for k, v in manifest.items() if v is not None}
        (module / "module.json").write_text(json.dumps(manifest))
        (module / "composer.json").write_text(json.dumps({"type": "humhub-module"}))
        (module / "Module.php").write_text("<?php\nnamespace demo;\nclass Module {}\n")
        default_config = (
            "<?php\nreturn ['id' => 'demo', 'class' => 'demo\\\\Module', 'namespace' => 'demo'];\n"
        )
        (module / "config.php").write_text(config if config is not None else default_config)
        (module / "tests").mkdir()
        if migrations:
            (module / "migrations").mkdir()
            for filename, body in migrations.items():
                (module / "migrations" / filename).write_text(body)
        for filename, body in (extra_php or {}).items():
            (module / filename).write_text(body)
        return module

    return factory


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
