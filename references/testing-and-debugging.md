# Testing and debugging federation

## Levels

1. **Document fixtures.** Write the JSON you emit (actor, Create, Follow, Accept, Undo,
   Delete…) as fixture files and run `python3 scripts/validate_activitypub.py <dir>`.
   Pin the shape in unit tests (golden JSON) so refactors cannot change it silently.
2. **Unit tests, network-free.** Feed prebuilt documents and request headers into the
   inbox handler, signature verifier, serializers and resolvers. Use a fixed test key
   pair and a known digest vector.
3. **Contract tests.** Sign a request with your code and verify it with an independent
   implementation (or the reverse) to catch canonicalisation bugs.
4. **Live interop.** Only from a public HTTPS host: follow and be followed by test
   accounts on Mastodon, Lemmy and one other implementation; check posts, replies, likes,
   edits, deletes, and an unfollow in both directions.

Never point automated tests at real servers you do not operate.

## Tools

- <https://browser.pub>: view any actor or object as a remote server fetches it.
- <https://activitypub-testing.socialweb.coop/implementation-guide/> and
  <https://feditest.org>: test suites and an implementation guide.
- JSON-LD Playground (<https://json-ld.org/playground/>) to check what a context
  defines; do not use expansion in production code.
- FediDB (<https://fedidb.org/>) to see what software a remote host runs.
- `curl -H 'Accept: application/activity+json' <id>` to fetch a document (add a
  signature for authorized-fetch hosts).

## Debugging a failing remote

| Symptom | Check first |
| --- | --- |
| Remote cannot find the account | WebFinger answer, `preferredUsername` vs handle, reverse lookup, CORS |
| Follow stays pending | `Accept` sent to the personal inbox, signed by the followed actor, `object` = our Follow |
| All inbound rejected | Proxy rewriting `Host`/path; clock skew; Digest computed on a modified body |
| One server rejects fetches with 401 | Authorized fetch: sign GETs as the instance actor |
| Posts arrive but not on the remote timeline | Addressing (`to` Public, `cc` followers), follow accepted on their side |
| Edits ignored | `updated` missing on `Update{Note}`; object not the full document |
| Replies don't thread | `inReplyTo` id not dereferenceable or different from the stored id |
| Remote shows wrong counts | `followers`/`following` collections missing `totalItems` |

Keep an opt-in activity log (raw inbound and outbound JSON, outcome, capped size) so
problems can be diagnosed from real traffic, and record the received versus canonical
values when a signature fails.

## Before declaring federation "works"

- A second delivery of the same activity is a no-op.
- An Undo, Delete and Update from someone other than the author is rejected.
- Followers-only or direct content from a remote is not exposed publicly.
- A 410 from a remote stops further deliveries to it.
- Nothing is created on GET requests (confirm pages, actor fetches) besides cached keys.
