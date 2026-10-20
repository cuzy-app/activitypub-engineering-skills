# Discovery: WebFinger, remote follow, NodeInfo

Sources: <https://docs.joinmastodon.org/spec/webfinger/> · <https://fedify.dev/manual/webfinger> ·
<https://github.com/jhass/nodeinfo/blob/main/PROTOCOL.md> · RFC 7033 · RFC 7565 ·
FEP-2c59, FEP-d556, FEP-f1d5, FEP-2677

## WebFinger

```text
GET /.well-known/webfinger?resource=acct:alice@a.example
```

```json
{"subject": "acct:alice@a.example",
 "aliases": ["https://a.example/users/alice", "https://a.example/@alice"],
 "links": [
   {"rel": "self", "type": "application/activity+json",
    "href": "https://a.example/users/alice"},
   {"rel": "http://webfinger.net/rel/profile-page", "type": "text/html",
    "href": "https://a.example/@alice"},
   {"rel": "http://ostatus.org/schema/1.0/subscribe",
    "template": "https://a.example/authorize_interaction?uri={uri}"}]}
```

- Also accept `resource=<actor https URL>`. Tolerate `acct:@alice@a.example`.
- Serve as `application/jrd+json`; add `Access-Control-Allow-Origin: *` (Verify: RFC 7033
  recommends CORS).
- 404 for unknown or non-discoverable accounts; 410 for deleted ones.
- **Mastodon's reverse check**: after fetching an actor it WebFingers
  `acct:<preferredUsername>@<actor host>` and requires the `self` link to point back to the
  same actor. Keep `preferredUsername` unique per domain and equal to the handle's user
  part. If handles use a different domain than actor ids, the actor host must still
  answer that lookup with the canonical subject.
- When resolving a remote handle: follow redirects manually and re-validate each hop
  (apex domains often redirect to the real host), accept a `self` link of type
  `application/activity+json` or the ld+json profile type, and fetch that actor.
- FEP-2c59: put `"webfinger": "alice@a.example"` on the actor; the JRD for it must link
  the actor without redirects.
- FEP-d556: `resource=https://a.example/` returns the instance actor with
  `rel: "https://www.w3.org/ns/activitystreams#Service"`.

## Remote follow and interaction

The `http://ostatus.org/schema/1.0/subscribe` template lets a user on another server
click "Follow" on a profile here and land on their own server's confirm page, and the
reverse. On your side, `/authorize_interaction?uri=<handle or URL>` should require login,
resolve the target, show a confirmation, and act only on POST (a GET must not create
records or send activities). FEP-3b86 (Activity Intents) is a newer alternative.

## NodeInfo

```text
GET /.well-known/nodeinfo
{"links": [{"rel": "http://nodeinfo.diaspora.software/ns/schema/2.1",
            "href": "https://a.example/nodeinfo/2.1"}]}
```

- Also list the 2.0 rel for older crawlers (Verify: common practice) and the FEP-2677
  `Application` link to the instance actor.
- The document: `version: "2.1"`, `software {name, version, repository, homepage}` (name
  matches `^[a-z0-9-]+$`), `protocols: ["activitypub"]`,
  `services {inbound: [], outbound: []}`, `openRegistrations`,
  `usage {users {total, activeHalfyear, activeMonth}, localPosts, localComments}`,
  `metadata {}`.
- Content type `application/json; profile="http://nodeinfo.diaspora.software/ns/schema/2.1#"`.
- Crawlers (FediDB, instance lists) read it; zeros in `usage` are allowed but make the
  instance look dead. Expose only what the operator is comfortable publishing.
