# Agent instructions

This repository is an agent-agnostic skill for ActivityPub engineering (client-to-server
and server-to-server federation) and for the HumHub (Yii2) modules that implement it.
Any coding agent that reads `AGENTS.md` or the Agent Skills layout can use it.

- Entry point: [SKILL.md](SKILL.md). It holds the operating contract and a task router.
- Detailed topics: [references/](references/). Load only the file the router names.
- Static validators: `python3 scripts/validate_activitypub.py <file-or-dir>`,
  `python3 scripts/validate_module.py <module-dir>` and `python3 scripts/validate_skill.py`.

## Working on this repository

- Keep `SKILL.md` short (the validator enforces a line budget) and route every file in
  `references/` from it. HumHub references are named `humhub-*.md`.
- Never state protocol behaviour or a HumHub API as fact unless it comes from a
  specification, a FEP, the installed core, or the documentation of a named
  implementation. Link the source. Mark everything else "Verify".
- Record new sources in [docs/SOURCES.md](docs/SOURCES.md).
- Everything under `examples/` must pass the validators in strict mode.
- Run before committing:

```bash
python3 scripts/validate_skill.py
python3 scripts/validate_activitypub.py examples/documents --strict
python3 scripts/validate_module.py examples/minimal-module --strict
python3 -m pytest
ruff check .
```
