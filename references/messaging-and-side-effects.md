# Messaging and side effects: inbox, outbox, delivery

Sources: <https://www.w3.org/TR/activitypub/> §5-7 · <https://fedify.dev/manual/send> ·
<https://fedify.dev/manual/inbox> · <https://docs.joinmastodon.org/spec/activitypub/>

## Two directions

| | Client-to-server (C2S) | Server-to-server (S2S) |
| --- | --- | --- |
| Who posts | An authenticated client | A remote server, signed with an actor key |
| Where | The actor's own **outbox** | The recipient's **inbox** or shared inbox |
| Auth | The server's own (OAuth etc.) | HTTP Signatures ([http-signatures](http-signatures.md)) |
| Deployed | Rarely; most servers expose a proprietary client API instead | Everywhere; this is federation |

### C2S outbox POST (§6)

- The client POSTs an activity, or a bare object which the server MUST wrap in a `Create`
  (copying addressing from the object).
- The server assigns ids (it MUST ignore or replace client-supplied ids for new objects),
  sets `attributedTo`/`actor` to the authenticated actor, strips `bto`/`bcc` before
  delivery, answers **201 Created** with `Location: <activity id>`, and then performs the
  side effects below and S2S delivery.
- C2S `Update` is a partial update (only listed properties change); S2S `Update` replaces
  the object. Do not confuse the two.

### S2S inbox POST (§7)

1. Read the raw body; cap its size (Verify: about 1 MB is common).
2. Verify the request ([http-signatures](http-signatures.md)) and origin rules
   ([security-and-validation](security-and-validation.md)).
3. **De-duplicate on activity `id`.** The inbox MUST NOT process the same activity twice;
   a unique key in the database beats a time-limited cache.
4. Answer **202 Accepted** quickly and process asynchronously (a queue job).
5. Unknown types: accept with 202 and ignore. Bad signature: 401. Malformed JSON: 400.
   Blocked actor or domain: 403 or a silent 202.

## Side effects of received activities (S2S)

| Activity | Required effect |
| --- | --- |
| `Create` | Store the object. |
| `Update` | Replace the stored copy completely (not a merge). Only the owner may update. |
| `Delete` | Remove the object or replace it with a `Tombstone`. Only the owner may delete. |
| `Follow` | Answer `Accept` or `Reject`, automatically or after user approval. |
| `Accept` (of our Follow) | Add the actor to our `following`. Match it to the Follow id we sent. |
| `Reject` (of our Follow) | MUST NOT add to `following`; mark the follow rejected. |
| `Like`, `Announce` | Record on the object's `likes` / `shares`. |
| `Undo` | Reverse the undone activity's effect. Its actor MUST equal the undone activity's actor. |
| `Add` / `Remove` | Change the `target` collection, if the actor may. |
| `Block` | Do not forward to the blocked actor (Mastodon also sends it so they stop interacting). |

## Delivery (outbound)

- Recipients: `to`, `bto`, `cc`, `bcc`, `audience`. Dereference collections one level
  (your followers), de-duplicate, drop the activity's own actor and your local users, and
  never deliver to Public.
- Prefer each recipient's `endpoints.sharedInbox`, de-duplicated. A server MUST still
  deliver directly to recipients without one.
- **Directed activities go to the personal inbox** (`Accept`, `Reject`, `Follow`, `Undo`,
  a `Like` or reply to one author). Verify per implementation: some shared inboxes drop a
  directed `Accept`.
- Strip `bto` and `bcc` before delivery and display.
- Send `actor` as an id string, never embedded (Threads rejects embedded actors).
- Keep order per destination server: a `Delete` must not overtake its `Create`.
- Deliver asynchronously with retries and exponential backoff (Fedify: up to 10 tries).

| Response | Treatment |
| --- | --- |
| 2xx | Delivered |
| 404, 410 | Permanent. On 410 from an actor or inbox, mark it gone, drop its follows, stop delivering |
| Other 4xx | Permanent, except 429: retry after `Retry-After` |
| 5xx, timeouts, DNS or TLS errors | Transient: retry with backoff |

Verify: Mastodon retries for about a week, then marks the domain unavailable until it
hears from it again. Doing the same avoids queues filling up with dead servers.

## Inbox forwarding (§7.1.2)

A reply sent to you about your object must reach your followers too. Forward a received
activity **only** when all hold:

1. it is the first time you see it;
2. its `to`, `cc` or `audience` contains a collection you own (e.g. your followers);
3. its `inReplyTo`, `object`, `target` or `tag` references an object you own.

Forward the original body unchanged (its signature is the sender's; the HTTP signature
on your forward is yours, see LD signatures in [http-signatures](http-signatures.md)).
Never add addressees; limit recursion.

## Outbox and collections

- The outbox is an `OrderedCollection` of the actor's public activities, newest first,
  paged (`first`, `next`, `prev`, `totalItems`). Remotes read it to backfill.
- `followers` and `following` expose `totalItems`; listing members is optional and may be
  restricted. Mastodon reads `totalItems` for the counts it shows.
- Serve collections with the same content negotiation as objects.
