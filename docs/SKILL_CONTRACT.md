# Skill contract

## Scope

ActivityPub engineering: Activity Streams 2.0 documents, actors and keys, client-to-server
and server-to-server messaging, activity side effects, HTTP Signatures, WebFinger,
NodeInfo, delivery, security of received content, Mastodon and Lemmy interoperability,
FEPs, and mapping a platform's entities to ActivityPub.

## Not in scope

- HumHub and Yii2 module structure, migrations, events, queue wiring and tests
  (companion `humhub-engineering` skill).
- The Mastodon client REST API and OAuth.
- Operating a server (hosting, moderation policy, relays as a service).
- Security certification or penetration testing.

## Permission boundaries

- The skill grants no tool permissions. Bundled scripts only read files.
- `validate_activitypub.py` never makes network requests and never writes files.
- `install_skill.py` writes only to the chosen skills directory and never edits client
  settings.

## Context budget

- `SKILL.md` is held to a line budget enforced by `validate_skill.py`.
- Each reference file has a separate, larger budget and is loaded on demand.

## Evidence rules

A statement about protocol behaviour must be tagged by origin: specification, FEP,
documentation of a named implementation, or recollection. Recollection needs a "Verify"
note. FEP statuses are re-checked with the `fep` MCP server or the FEP repository.
