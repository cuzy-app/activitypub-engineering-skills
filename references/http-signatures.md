# HTTP Signatures and proofs

Sources: <https://docs.joinmastodon.org/spec/security/> · <https://fedify.dev/manual/send> ·
<https://fedify.dev/manual/inbox> · <https://fedify.dev/manual/access-control> · FEP-8b32

## draft-cavage (required for interop today)

```text
Signature: keyId="https://a.example/users/alice#main-key",algorithm="rsa-sha256",
           headers="(request-target) host date digest",signature="<base64>"
```

- Algorithm: RSA-SHA256 (RSASSA-PKCS1-v1_5). The signing string is each listed header as
  lowercase `name: value`, joined by `\n`. `(request-target)` is `post /inbox` (method
  lowercase, path plus query).
- POST signs `(request-target) host date digest`; GET signs `(request-target) host date`.
- `Digest: SHA-256=<base64(sha256(raw body))>`. `digest` MUST be in `headers`. Verify it
  against the raw bytes before parsing JSON.
- `Date` in IMF-fixdate (`Tue, 20 Oct 2026 12:00:00 GMT`). Mastodon rejects dates older
  than 12 hours. Verify: it also allows about 1 hour of future skew. A stricter window
  (1 hour past, a few minutes future) is reasonable for receivers.

## Verifying a request

1. Parse `Signature`; require `keyId`, `headers`, `signature`.
2. Require `digest` (POST) and `date` among the signed headers; check the Digest and the
   Date window.
3. Fetch `keyId` (strip the fragment for the actor document), find the `publicKey` whose
   `id` equals `keyId`. If the key lives in a separate document, its `owner` must be an
   actor that lists the same key (a reciprocal claim).
4. Rebuild the signing string from the received request and verify.
5. **The key owner MUST equal the activity's `actor`.** Otherwise reject with 401.
6. Cache keys; when verification with a cached key fails, refetch once and retry.

### Behind proxies

The signature covers `host` and the request path as the sender addressed them. A reverse
proxy that rewrites `Host` or the path breaks verification. Rebuild the signing string
from the server's own canonical public host and path (from configuration) as well as the
received values. Never trust client-controlled `X-Forwarded-*` headers for this.

## RFC 9421 HTTP Message Signatures

- Mastodon verifies them from 4.5: `Signature-Input` + `Signature`, a single signature,
  `created` required, `@method` and `@target-uri` covered, `Content-Digest` (RFC 9530)
  required and covered, RSA-PKCS1-v1_5-SHA256; Ed25519 from 4.7.
- Mastodon still requires cavage. Fedify "double-knocks": sign with RFC 9421 first,
  retry with cavage on a 4xx, remember per server what worked, and answer
  `401 + Accept-Signature` challenges (at most 3 attempts).
- Order of adoption: accept both inbound → keep sending cavage → add RFC 9421 with
  double-knocking.

## Authorized fetch (secure mode)

- Servers in authorized-fetch mode answer 401 to unsigned GETs of actors, objects and
  collections. **Sign every outgoing GET**: as the user when there is a user context,
  otherwise as the instance actor.
- Never require a signature to fetch your instance actor or its key (deadlock between
  two authorized-fetch servers).
- Making your own server require signed fetches is optional and not part of the spec.

## LD Signatures and Object Integrity Proofs

- Mastodon still emits `RsaSignature2017` Linked Data Signatures on account-deletion
  `Delete`s and relayed activities, but advises new implementations not to adopt them.
- FEP-8b32 Object Integrity Proofs (`DataIntegrityProof`, cryptosuite `eddsa-jcs-2022`,
  `proofPurpose: assertionMethod`, key from the actor's `assertionMethod`) are the
  successor. Mastodon 4.7 checks them when no LD signature verifies.
- **Without either, forwarded or `Announce`-wrapped content is not authenticated by the
  HTTP signature**, which belongs to the forwarder. Re-fetch the inner object from its
  origin before trusting it.

## Deleted actors

When a `Delete` arrives from an actor whose key fetch returns 410, it cannot be verified.
Answer 202 and drop it, then, if you cache that actor, fetch its URL yourself: 410 or 404
confirms the deletion and lets you clean up. This stops endless redelivery.
