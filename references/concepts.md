# Concepts: Activity Streams, JSON-LD, ids

The data model shared by client-to-server and server-to-server ActivityPub.

Sources: <https://www.w3.org/TR/activitystreams-core/> ·
<https://www.w3.org/TR/activitystreams-vocabulary/> · <https://www.w3.org/TR/activitypub/>

## Media type and context

- Serialise as `application/activity+json` (UTF-8). Treat
  `application/ld+json; profile="https://www.w3.org/ns/activitystreams"` as equivalent.
- Emitted documents SHOULD carry `"@context": "https://www.w3.org/ns/activitystreams"`.
  Extra contexts MAY follow (as an array) but MUST NOT redefine AS2 terms. A consumer that
  receives no `@context` MUST assume the AS2 one.
- Consumers MUST ignore unknown properties instead of rejecting the document.
- **No JSON-LD processing is needed for interop.** Every major implementation reads the
  compacted keys directly. Do not expand documents and do not depend on remote contexts
  loading. Do write the contexts that define the extension terms you use
  ([actors-and-keys](actors-and-keys.md) has the usual block).

## Value shapes: the main source of parser bugs

Documents are JSON-LD compacted, so any property can be:

- a single value **or** an array (order not significant, except `orderedItems`);
- an IRI string, an embedded object, or a `Link` object.

Read every property through two helpers:

```text
asList(v)  -> []            if v is null or absent
           -> v             if v is a list
           -> [v]           otherwise
idOf(v)    -> v             if v is a string
           -> v["id"]       if v is an object with an id (or v["href"] for a Link)
           -> null          otherwise
```

Never index `actor`, `object`, `to`, `cc`, `tag`, `attachment`, `url`, `icon` or `image`
without them. Absent, `null` and `[]` mean the same thing; emit absent rather than `[]`.

## Ids

- Every object and activity MUST have a globally unique id, except transient activities
  that are never stored (rare; do not rely on it). Ids SHOULD be HTTPS URLs.
- An id SHOULD be dereferenceable: a GET with an ActivityPub `Accept` header returns the
  document. Remotes fetch ids to resolve replies, search by URL, and verify origin.
- Ids are opaque and permanent. Do not encode mutable data (usernames that can change)
  unless you also serve redirects or `alsoKnownAs`; a stable internal id (GUID) is safer.
- **Never reuse an activity id.** Follow → Undo → Follow must yield three distinct ids,
  so do not derive activity ids from (actor, object) alone.
- `url` is the human-facing HTML link; `id` is the machine identity. They may differ.

## Public addressing

- The Public collection is `https://www.w3.org/ns/activitystreams#Public`. Compare
  `as:Public` and `Public` as the same value when reading. Verify: universal practice,
  not stated in the AS2 Core text.
- Public is an audience marker, not an inbox: never deliver to it.
- Addressing patterns (Mastodon visibility, see [mastodon-interop](mastodon-interop.md)):

| Visibility | `to` | `cc` |
| --- | --- | --- |
| public | Public | author's followers |
| unlisted | author's followers | Public |
| followers-only | author's followers | - |
| direct | mentioned actors | - |

## Vocabulary that matters

- Actor types: `Person`, `Group`, `Application`, `Service`, `Organization`.
- Object types: `Note` (short post), `Article` (long-form), `Page` (Lemmy posts),
  `Image`, `Video`, `Document`, `Question` (poll), `Event`, `Tombstone` (`formerType`,
  `deleted`).
- Link types: `Link`, `Mention`. `Hashtag` is not AS2 vocabulary; it is an `as:`
  extension used by Mastodon.
- Collections: `Collection`, `OrderedCollection` (reverse chronological for inbox and
  outbox), and their `*Page` types with `first`, `next`, `prev`, `last`, `partOf`.
- Natural language: `content` is a string; `contentMap`, `nameMap`, `summaryMap` are
  keyed by BCP 47 tag (`und` when unknown). State the language when you know it.
- Dates: RFC 3339 with an uppercase `T` and a `Z` or offset, e.g. `2026-10-20T12:00:00Z`.
- Functional (single-valued) properties include `replies`, `mediaType`, `published`,
  `updated`. `inReplyTo`, `audience` and `context` may be multi-valued.
