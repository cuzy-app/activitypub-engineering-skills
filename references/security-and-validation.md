# Security and validation of received content

Sources: FEP-fe34 (origin-based security model) · <https://www.w3.org/TR/activitypub/>
Appendix B · <https://fedify.dev/manual/inbox> · <https://docs.joinmastodon.org/spec/security/>

## Origin rules (FEP-fe34)

- **Origin** = scheme + host + port, lowercased, default ports normalised.
- An object's `id` and its owner (`actor` for activities, `attributedTo` for objects)
  MUST share an origin.
- A signed request authenticates its actor, and objects that share that actor's origin.
- An **embedded object** is trusted only if its wrapper is trusted and it shares the
  wrapper's origin and owner. `Create{Note}` from `a.example` whose Note id is on
  `b.example` must be rejected, or the Note re-fetched from `b.example`.
- When fetching by id without a signature: the final URL after redirects MUST share the
  origin of the requested id, and the response must be an ActivityPub media type.
- Key ids MUST share the actor's origin and be claimed by the actor.

## Authorisation of effects

- `Update` and `Delete`: only the object's owner.
- `Undo`: actor equals the undone activity's actor.
- `Update{actor}`: embedded actor id equals the signer.
- `Accept`/`Reject` of a Follow: the signer is the Follow's `object` (the followed actor),
  and the Follow is one you sent.
- Group moderation activities: the actor is in the group's moderators and the activity was
  announced by the group (FEP-1b12).

## Visibility of received content

Respect the sender's addressing. Content whose `to`/`cc` does not contain Public
(`https://www.w3.org/ns/activitystreams#Public`, `as:Public` or `Public`) is followers-only
or direct and must not become publicly visible on your side. Map it to a restricted
visibility or drop it if the platform has none.

## Inbound processing checklist

1. Body size cap; parse JSON only after Digest verification.
2. Signature, Date window, key owner = `actor` ([http-signatures](http-signatures.md)).
3. Origin rules above, for the activity and every embedded object you use.
4. De-duplicate on activity id and on object id.
5. Persist nothing (no shadow accounts, no follow rows) before steps 1-4 pass, and only
   when the activity will actually be stored.
6. Re-fetch `Announce`d or forwarded inner objects from their origin.
7. Sanitise HTML: allow-list tags and attributes, http(s) links only.
8. Every URL you will render as a link (`url`, `icon.url`, profile links) must be
   `http`/`https`; reject `javascript:` and `data:`.

## SSRF and fetch hygiene

- Allow only `https` (and `http` only behind an explicit dev switch, off by default).
- Resolve the host and reject loopback, private, link-local, CGNAT and reserved ranges.
  Pin the resolved address for the connection to avoid DNS rebinding between check and
  connect.
- Disable automatic redirects; follow at most a few manually, re-validating each target
  (Fedify: 5).
- Set connect and total timeouts; cap response size; for media, allow-list types
  (raster images) and cap bytes.
- Limit recursion: `inReplyTo` chains, collection pages, nested Announces.

## Abuse controls

- Rate-limit the inbox per IP and per remote domain; answer 429 with `Retry-After`.
- Keep a domain and actor blocklist checked before processing and before delivery.
- Rate-limit expensive unauthenticated endpoints (actor key generation, WebFinger).
- Log rejected activities with the reason and the received versus expected values, but
  never log private keys.
