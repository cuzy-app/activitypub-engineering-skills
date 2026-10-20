# Fediverse Enhancement Proposals

FEPs document conventions beyond the W3C specs. Statuses below were read from
<https://codeberg.org/fediverse/fep> on 2026-10-20. **Re-check before implementing**: call
`get_fep <slug>` on the `fep` MCP server, or read
`https://codeberg.org/fediverse/fep/src/branch/main/fep/<slug>/fep-<slug>.md`.

## Setting up the fep MCP server

`dahlia/fep-mcp` (by the Fedify author) caches the FEP repository and exposes
`list_feps`, `get_fep`, `search_feps` and `refresh_repository`, plus `fep://index` and
`fep://{slug}` resources. It needs Deno. For Claude Code (from its README):

```bash
claude mcp add fep -- deno run --no-config --node-modules-dir=auto --allow-ffi \
  --allow-read --allow-write --allow-net --allow-env --allow-sys jsr:@hongminhee/fep-mcp
```

Other MCP clients take the same command and arguments in their server configuration
(`{"command": "deno", "args": ["run", "--no-config", ...]}`). `FEP_MCP_REPOSITORY_DIR`
sets the cache location. Prebuilt binaries are on the project's releases page.

## FEPs that matter for a federating platform

| FEP | Title (status) | Use |
| --- | --- | --- |
| f1d5 | NodeInfo in Fediverse Software (FINAL) | Implement NodeInfo 2.1 ([discovery](discovery.md)) |
| 67ff | FEDERATION.md (FINAL) | Ship a `FEDERATION.md` listing supported protocols, FEPs and quirks |
| fe34 | Origin-based security model (DRAFT) | Basis of received-content validation |
| 1b12 | Group federation (FINAL) | Communities, Announce wrapping, `audience`, moderators |
| 2677 | Identifying the Application Actor (DRAFT) | NodeInfo link to the instance actor |
| d556 | Server-Level Actor Discovery Using WebFinger (FINAL) | `resource=https://host/` → instance actor |
| 2c59 | Discovery of a Webfinger address from an ActivityPub actor (DRAFT) | `webfinger` actor property; Mastodon 4.6+ |
| 5feb | Search indexing consent for actors (DRAFT) | Emit `indexable`; honour it for remote content |
| 521a | Representing actor's public keys (FINAL) | `assertionMethod` Multikeys |
| 8b32 | Object Integrity Proofs (DRAFT) | Verify forwarded and announced content |
| 8fcf | Followers collection synchronization across servers (FINAL) | Keep follower state consistent with Mastodon |
| 7628 | Move actor (FINAL) | Handle account migration |
| 044f | Consent-respecting quote posts (DRAFT) | Quotes; Mastodon 4.5+ |
| e232 | Object Links (FINAL) | `tag` Link entries for objects linked in content |
| fb2a | Actor metadata (DRAFT) | Profile fields as Note/Link attachments |
| 400e | Publicly-appendable ActivityPub collections (FINAL) | Group walls (Smithereen model) |
| 7458 | Using the replies collection (DRAFT) | Publish and verify `replies` |
| f228 | Backfilling conversations (DRAFT) | `context` collection for whole threads |
| 844e | Capability discovery (DRAFT) | `implements` on the Application actor |
| c648 | Blocked Collection (DRAFT) | Low priority |

Titles only verified (summaries from recollection, Verify): c0e0 Emoji reactions, 9967
Polls, b2b8 Long-form Text, 4ccd Pending Followers / Pending Following Collections, 3b86
Activity Intents, 7888 Demystifying the context property, 171b Conversation Containers.

## When to reach for a FEP

- Before inventing an extension property: search the FEPs first.
- When a remote implementation behaves unexpectedly: its `FEDERATION.md` usually names
  the FEPs it follows.
- When adding a feature others already federate (quotes, reactions, polls, moves).
