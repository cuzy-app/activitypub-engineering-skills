# Activity types

What each activity carries, what it must do, and the shapes implementations expect.
`object` MUST be present on Create, Update, Delete, Follow, Add, Remove, Like, Block and
Undo; `target` on Add and Remove (ActivityPub §7).

Sources: <https://www.w3.org/TR/activitypub/> · <https://www.w3.org/TR/activitystreams-vocabulary/> ·
<https://docs.joinmastodon.org/spec/activitypub/>

## Create

```json
{"@context": "https://www.w3.org/ns/activitystreams",
 "id": "https://a.example/users/alice/notes/1/activity", "type": "Create",
 "actor": "https://a.example/users/alice",
 "to": ["https://www.w3.org/ns/activitystreams#Public"],
 "cc": ["https://a.example/users/alice/followers"],
 "object": {"id": "https://a.example/users/alice/notes/1", "type": "Note",
            "attributedTo": "https://a.example/users/alice",
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": ["https://a.example/users/alice/followers"],
            "content": "<p>Hello</p>", "published": "2026-10-20T12:00:00Z"}}
```

- The activity and object addressing should agree. `attributedTo` = `actor`.
- The object's `id` must share the actor's origin.
- Replies set `inReplyTo` to the parent object's id.

## Update

- Carries the **full** object (S2S replaces, it does not merge).
- Mastodon applies a Note edit only when `updated` is set. Always set it.
- `Update{actor}` refreshes a profile; the object id must equal the signing actor.
- Only the owner may update. Same origin is the minimum check.

## Delete

- `object` is the id string or a `Tombstone {id, formerType}`.
- After a Delete, the object URL should answer 410 Gone.
- An actor deleting itself sends `Delete {object: <actor id>}`.
- Only the owner may delete. A Delete for an object you never stored is a no-op.

## Follow, Accept, Reject

```json
{"id": "https://a.example/users/alice/follows/6f1c", "type": "Follow",
 "actor": "https://a.example/users/alice", "object": "https://b.example/users/bob"}
```

- Answer with `Accept {object: <the Follow>}` (embedded, or its id) sent to the follower's
  personal inbox, signed by the followed actor.
- **Store the Follow id you send.** Mastodon's `Accept.object` may be the Follow id string
  or the embedded Follow; match on it rather than accepting every pending follow to that
  actor.
- `Reject` means the follow must not take effect; also used to remove an existing follower.
- Following a `Group` works the same way (see [groups-and-communities](groups-and-communities.md)).

## Undo

- `object` is the original activity, embedded with at least `id`, `type`, `actor`,
  `object`. Its `actor` MUST equal the Undo's actor.
- Common: `Undo{Follow}` (unfollow), `Undo{Like}`, `Undo{Announce}` (unboost),
  `Undo{Block}`, `Undo{Accept}` (remove a follower, Mastodon).

## Like and Dislike

- `Like {object: <object id>}`, sent to the object author's inbox.
- In Lemmy a `Like` is an upvote and `Dislike` a downvote, with `audience` = community.
- Record idempotently by Like id; remove on `Undo{Like}`.

## Announce

- A boost: `Announce {actor, object: <object id>, to: Public, cc: [author, followers]}`.
- A group relay (FEP-1b12): `Announce {actor: group, object: <whole original activity>}`.
  The inner activity is not authenticated by the outer signature; see
  [security-and-validation](security-and-validation.md).
- Distinguish the two by the `object` shape: an object/id (boost) or an activity (relay).

## Add, Remove, Block, Flag, Move

- `Add`/`Remove` with `target` a collection: pinned posts (`featured`), Lemmy moderators.
- `Block` from a local user to a remote actor; Lemmy also uses it for community bans.
- `Flag` reports content to the remote server, sent from the instance actor, `object`
  listing the reported actor and objects.
- `Move` for account migration (see [actors-and-keys](actors-and-keys.md)).

## Ignore safely

Any type you do not implement is accepted (202) and ignored. Log it at info level so
gaps are visible, but never fail the request.
