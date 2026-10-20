# Client compatibility

`scripts/install_skill.py` knows these skill directories. They are defaults, not
guarantees. Confirm each against the client's current documentation before relying on
it, and use `--dest` to override.

| Client | User scope | Project scope | Status |
| --- | --- | --- | --- |
| claude | `~/.claude/skills/` | `.claude/skills/` | Documented layout |
| codex | `~/.codex/skills/` | `.codex/skills/` | Unverified |
| cursor | `~/.cursor/skills/` | `.cursor/skills/` | Unverified |
| gemini | `~/.gemini/skills/` | `.gemini/skills/` | Unverified |
| agents | `~/.agents/skills/` | `.agents/skills/` | Generic convention, unverified |

A documented discovery path is not proof that a client activated the skill. Use the
cases in `evals/trigger_cases.json` to check activation per client.
