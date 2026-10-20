# Groups and communities

Lemmy, Mbin, PieFed and NodeBB federate topic communities as `Group` actors that relay
their members' activities.

Sources: <https://join-lemmy.org/docs/contributors/05-federation.html> · FEP-1b12 (Group
federation, final) · FEP-400e (publicly-appendable collections)

## Group actor

`type: Group`, `preferredUsername`, `name`, `summary`, `icon`, `image`, `inbox`, `outbox`
(about the 20 latest posts), `followers` (`totalItems` only), `featured`,
`endpoints.sharedInbox`, `publicKey`, `sensitive` (whole community is NSFW), and
`attributedTo` = the moderators collection (creator first). `postingRestrictedToMods`
appears in examples but is undocumented.

Handles are written `!community@host`; strip the `!` for the WebFinger lookup.

## Posts, comments, votes

- **Post = `Page`** with a mandatory `name` (title), `attributedTo` (author),
  `to: [community, Public]`, `audience: community`, `content` (HTML) plus `mediaType` and
  `source` (Markdown), `attachment` (a single `Link` for link posts), `image` (thumbnail),
  `sensitive`, `commentsEnabled` (false = locked), `stickied`, `language`, `published`,
  `updated`. Lemmy also accepts `Article`, `Note`, `Video`, `Event` as posts.
- **Comment = `Note`** with `inReplyTo` (the post or the parent comment), `to`/`cc` and
  `audience` = community, `Mention` tags.
- **Votes**: `Like` = upvote, `Dislike` = downvote, both with `audience`; `Undo` cancels.
- Always send `to`, `cc` and `audience` on posts, comments and votes. Verify: Lemmy shows
  `audience` in every example; whether it rejects documents without it is unconfirmed.

## Following

A user (or a local proxy actor) sends `Follow` to the group; the group answers
`Accept{Follow}`. FEP-1b12: groups SHOULD support Follow/Accept and apply block checks,
and MAY Reject.

## Announce wrapping (FEP-1b12)

For each valid incoming activity (Create, Update, Like, Dislike, Delete, Remove, Undo…),
the group MUST send to its followers:

```json
{"type": "Announce", "actor": "https://l.example/c/linux",
 "to": ["https://www.w3.org/ns/activitystreams#Public"],
 "cc": ["https://l.example/c/linux/followers"],
 "object": {"id": "https://m.example/activities/create/42", "type": "Create",
            "actor": "https://m.example/u/alice", "object": {"type": "Page", "...": "..."}}}
```

The inner activity is preserved byte-for-byte so its id and proofs keep working. Private
activities such as Follow may be left out.

## Receiving an Announce from a group

1. Verify the HTTP signature: it authenticates the **group**, not the inner author.
2. Confirm the group is one you follow (or that is relevant to the target).
3. Check the inner activity's `id` and `actor` share an origin.
4. **Re-fetch the inner object (or activity) from its origin** and use the fetched copy,
   unless it carries a verifiable integrity proof.
5. Then apply it as if received directly: Create → store post or comment; Like/Dislike →
   vote; Delete/Remove → remove; Update → replace.

## Moderation

- `Add`/`Remove` with `target` = moderators collection (mod or instance admin), or the
  featured collection (pin a post).
- `Lock{Page}` locks comments. `Delete` with `summary` gives a removal reason.
- `Block` with `target` = community or instance, plus `removeData`, `summary`, `expires`.
- FEP-1b12: moderation actors MUST be listed in the group's `attributedTo`, and followers
  MUST check that moderation activities were announced by the group.

## Mapping onto a platform

A community can be mirrored into a local group or space owned by a system account, with
local members interacting through their own actors (posts become `Page` to the community,
comments `Note`, votes `Like`). Decide early whether local users author posts in the
remote community and how titles are required, because Lemmy rejects a `Page` without
`name`.
