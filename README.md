# activitypub-engineering-skills

Agent-agnostic engineering guidance for implementing ActivityPub federation and the
HumHub (Yii2) modules that carry it, with static validators, regression tests, and CI.
The layout follows the progressive disclosure pattern of
`dbwls99706/ros2-engineering-skills`: a short `SKILL.md` router, detailed references
loaded on demand, and scripts that check structure.

The protocol outline builds on the ActivityPub C2S guide (`activitypub-c2s`: concepts,
messaging and side effects, activity types) and extends it to server-to-server
federation, HTTP Signatures, discovery, Mastodon and Lemmy interop, and FEPs. The HumHub
references cover module structure, Yii2, migrations, content, permissions and events, UI
assets, queue jobs, tests and the conventions of
[`humhub/module-coding-standards`](https://github.com/humhub/module-coding-standards).
See [sources](docs/SOURCES.md) for provenance.

Status: **0.2.0**. Items marked "Verify" are not confirmed by a fetched source or the
installed core; check them before relying on them.

## Layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Operating contract and task router (ActivityPub and HumHub sections) |
| `AGENTS.md` | Pointer for agents that read `AGENTS.md` |
| `references/` | Topic files loaded only when relevant; HumHub ones are prefixed `humhub-` |
| `scripts/validate_activitypub.py` | Static checks for Activity Streams / ActivityPub JSON documents |
| `scripts/validate_module.py` | Static checks for a HumHub module directory |
| `scripts/validate_skill.py` | Checks this bundle: metadata, routing, links, budgets |
| `scripts/install_skill.py` | Copies a knowledge-only bundle into an agent's skills directory |
| `examples/documents/` | Example documents that must always pass the document validator in strict mode |
| `examples/minimal-module/` | Fixture module that must always pass the module validator in strict mode |
| `evals/trigger_cases.json` | Activation cases (no model outputs included) |
| `docs/` | Skill contract, client compatibility, sources |
| `.github/workflows/test.yml` | CI |

## Install

```bash
python3 scripts/install_skill.py --client claude --dry-run
python3 scripts/install_skill.py --client claude
# Alternatives: codex, cursor, gemini, agents. Add --project /path for project scope.
```

The installer copies `SKILL.md`, `references/` and the two validator scripts. It never
edits client settings. See [client compatibility](docs/CLIENT_COMPATIBILITY.md).

For FEP lookups, also add the `fep` MCP server; see [FEPs](references/feps.md).

## Validate

```bash
python3 scripts/validate_skill.py
python3 scripts/validate_activitypub.py examples/documents --strict
python3 scripts/validate_activitypub.py path/to/your/fixtures --json
python3 scripts/validate_module.py examples/minimal-module --strict
python3 scripts/validate_module.py /path/to/your/module
python3 -m pip install -r requirements-dev.txt
python3 -m pytest
```

All checks are static: they do not fetch, verify signatures, expand JSON-LD, run PHP,
boot HumHub, or replace Codeception.

## License

Not yet chosen. Add a `LICENSE` file before others can reuse this. The C2S guide this
builds on had no licence information available; see [sources](docs/SOURCES.md).
