# activitypub-engineering-skills

Agent-agnostic engineering guidance for implementing ActivityPub federation, with a
static document validator, regression tests, and CI. The layout follows the progressive
disclosure pattern of `dbwls99706/ros2-engineering-skills`: a short `SKILL.md` router,
detailed references loaded on demand, and scripts that check structure.

The outline builds on the ActivityPub C2S guide (`activitypub-c2s`: concepts, messaging
and side effects, activity types) and extends it to server-to-server federation,
HTTP Signatures, discovery, Mastodon and Lemmy interop, and FEPs. See
[sources](docs/SOURCES.md) for provenance.

Status: **0.1.0**. Items marked "Verify" are practice that no fetched source stated;
check them before relying on them.

## Layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Operating contract and task router |
| `AGENTS.md` | Pointer for agents that read `AGENTS.md` |
| `references/` | Topic files loaded only when relevant |
| `scripts/validate_activitypub.py` | Static checks for Activity Streams / ActivityPub JSON documents |
| `scripts/validate_skill.py` | Checks this bundle: metadata, routing, links, budgets |
| `scripts/install_skill.py` | Copies a knowledge-only bundle into an agent's skills directory |
| `examples/documents/` | Example documents that must always pass the validator in strict mode |
| `evals/trigger_cases.json` | Activation and hand-off cases (no model outputs included) |
| `docs/` | Skill contract, companion-skill rules, client compatibility, sources |
| `.github/workflows/test.yml` | CI |

## Install

```bash
python3 scripts/install_skill.py --client claude --dry-run
python3 scripts/install_skill.py --client claude
# Alternatives: codex, cursor, gemini, agents. Add --project /path for project scope.
```

The installer copies `SKILL.md`, `references/` and `scripts/validate_activitypub.py`. It
never edits client settings. See [client compatibility](docs/CLIENT_COMPATIBILITY.md).

For FEP lookups, also add the `fep` MCP server; see [FEPs](references/feps.md).

## Validate

```bash
python3 scripts/validate_skill.py
python3 scripts/validate_activitypub.py examples/documents --strict
python3 scripts/validate_activitypub.py path/to/your/fixtures --json
python3 -m pip install -r requirements-dev.txt
python3 -m pytest
```

Document checks are static: they do not fetch, verify signatures, or expand JSON-LD.

## Running with the HumHub skill

The `humhub-engineering` skill is developed separately and installed alongside this one.
The two have disjoint triggers and a documented hand-off; see
[companion skills](docs/COMPANION_SKILLS.md).

## License

Not yet chosen. Add a `LICENSE` file before publishing. The C2S guide this builds on had
no licence information available; see [sources](docs/SOURCES.md).
