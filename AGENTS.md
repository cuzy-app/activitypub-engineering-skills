# Agent instructions

This repository is an agent-agnostic skill for ActivityPub engineering (client-to-server
and server-to-server federation). Any coding agent that reads `AGENTS.md` or the Agent
Skills layout can use it.

- Entry point: [SKILL.md](SKILL.md). It holds the operating contract and a task router.
- Detailed topics: [references/](references/). Load only the file the router names.
- Static validators: `python3 scripts/validate_activitypub.py <file-or-dir>` and
  `python3 scripts/validate_skill.py`.

## Working on this repository

- Keep `SKILL.md` short (the validator enforces a line budget) and route every file in
  `references/` from it.
- Never state protocol behaviour as fact unless it comes from a specification, a FEP, or
  the documentation of a named implementation. Link the source. Mark everything else
  "Verify".
- Record new sources in [docs/SOURCES.md](docs/SOURCES.md).
- Every example document in `examples/documents/` must pass the validator in strict mode.
- Run before committing:

```bash
python3 scripts/validate_skill.py
python3 scripts/validate_activitypub.py examples/documents --strict
python3 -m pytest
ruff check .
```
