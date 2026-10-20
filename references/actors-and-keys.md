# Actors and keys

Sources: <https://www.w3.org/TR/activitypub/> §4 ·
<https://docs.joinmastodon.org/spec/activitypub/> · <https://fedify.dev/manual/actor> ·
FEP-521a, FEP-2677, FEP-d556, FEP-7628 (check with `get_fep`)

## Required and expected properties

ActivityPub requires `inbox` and `outbox`, and recommends `followers` and `following`.
Mastodon cannot verify or display an actor without more:

| Property | Status for interop |
| --- | --- |
| `id`, `type`, `inbox`, `outbox` | Required |
| `preferredUsername` | Required by Mastodon; must match the WebFinger handle |
| `publicKey {id, owner, publicKeyPem}` | Required to verify signatures; `owner` = actor `id` |
| `followers`, `following` | Expected; serve them as paged `OrderedCollection` |
| `endpoints.sharedInbox` | Expected; cuts delivery cost for large fan-outs |
| `name`, `summary` (HTML), `url` (HTML profile) | Expected |
| `icon` (avatar), `image` (header) as `Image {url, mediaType}` | Expected; omit `image` if the user set none |
| `published` | Expected |
| `manuallyApprovesFollowers` | Locked accounts |
| `discoverable`, `indexable` | Directory and search consent (FEP-5feb: missing `indexable` SHOULD be treated as false) |
| `attachment[]` of `PropertyValue {name, value}` | Profile fields (FEP-fb2a proposes Note/Link items; keep `PropertyValue` for Mastodon) |
| `alsoKnownAs`, `movedTo` | Account migration (FEP-7628) |
| `featured`, `featuredTags` | Pinned posts and tags |
| `webfinger` | FEP-2c59, Mastodon 4.6+: canonical `user@domain`, takes priority over `preferredUsername` |
| `attributionDomains` | Domains allowed to name this actor via `<meta name="fediverse:creator">` |

`Application` and `Service` actors display as bots. `Group` is a community (see
[groups-and-communities](groups-and-communities.md)).

## Context block

```json
["https://www.w3.org/ns/activitystreams", "https://w3id.org/security/v1",
 {"toot": "http://joinmastodon.org/ns#",
  "discoverable": "toot:discoverable", "indexable": "toot:indexable",
  "featured": {"@id": "toot:featured", "@type": "@id"}, "Emoji": "toot:Emoji",
  "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
  "sensitive": "as:sensitive", "Hashtag": "as:Hashtag",
  "schema": "http://schema.org#", "PropertyValue": "schema:PropertyValue",
  "value": "schema:value"}]
```

Mastodon's `http://schema.org#` is technically wrong. Copy it verbatim for compatibility.

## Keys

- One RSA key (2048 bits or more) in `publicKey`, id `<actor id>#main-key`. Many
  implementations handle several keys in `publicKey` badly.
- Additional keys (for example Ed25519 for Object Integrity Proofs) go in
  `assertionMethod[]` as `Multikey {id, controller, publicKeyMultibase}` (FEP-521a). Key
  ids are absolute and SHOULD be `actorId#fragment`.
- Generate keys lazily if you must, but rate-limit generation on unauthenticated requests.
- Store private keys encrypted at rest where the platform allows it.
- **Rotation** (Verify: no source documents a standard procedure): replace the key, then
  send `Update{actor}` to followers signed with the new key. Receivers re-fetch the actor
  when verification with a cached key fails, so as a receiver: cache keys, and on failure
  refetch once before rejecting.

## Instance (server) actor

A server-level `Application` actor signs fetches that have no user context and represents
the server for relays and reports.

- It MUST be fetchable **without** a signature, as must its key. Two authorized-fetch
  servers that both require signatures to read each other's instance actor deadlock.
- Advertise it in NodeInfo with a link `rel: "https://www.w3.org/ns/activitystreams#Application"`
  (FEP-2677, draft).
- Answer WebFinger `resource=https://host/` with a link
  `rel: "https://www.w3.org/ns/activitystreams#Service"` to it (FEP-d556, final).
- Mastodon serves its instance actor at `/actor` with `preferredUsername` = the domain.
  Verify before copying.

## Deleted, suspended and moved actors

- A deleted actor's URL and WebFinger answer **410 Gone**, optionally with a `Tombstone`
  `formerType: Person`. Send `Delete {object: <actor id>}` to every known inbox, signed
  with the actor's key (keep the key until delivery finishes).
- `Move {actor: old, object: old, target: new}` is valid only if the new actor lists the
  old one in `alsoKnownAs`. Receivers re-follow the target or notify the user (FEP-7628).
- Handle `Update{actor}` by replacing the cached profile, but only if the embedded
  object's `id` equals the authenticated actor.
