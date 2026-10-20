# Mapping a social platform to ActivityPub

Patterns for exposing an existing platform's users, groups, posts, comments and likes,
written with HumHub in mind but platform-neutral. Where the code lives in a HumHub
module (events, jobs, migrations) is covered by the `humhub-*` references; this file
covers the document shapes and the rules that keep federation safe.

## Entities

| Platform concept | ActivityPub | Notes |
| --- | --- | --- |
| User profile | `Person` | Stable id from an internal GUID, not the username |
| The server | `Application` instance actor | Signs fetches, owns no content |
| Group / space | `Group` | Outbound only if the group's content is public |
| Post | `Note` (short) or `Article` (long-form) | `Page` with `name` for Lemmy communities |
| Comment | `Note` with `inReplyTo` | Replies to comments may be flattened onto the post |
| Like / reaction | `Like` (reactions: FEP-c0e0, Verify) | Store the Like id |
| Follow | `Follow` / `Accept` / `Undo{Follow}` | Store the Follow id |
| Topic / tag | `Hashtag` tag | Lowercase name |
| File | `attachment` `Image` / `Document` | `name` = alt text |
| Remote account | A local shadow record | See below |

## Visibility is the first decision

Federation publishes. Only content that is already readable without login on the
platform should leave it, and the rule must be enforced in one place every outbound path
calls. Typical requirements, all at once:

- federation switched on for the site and opted into by the author or container;
- guest (anonymous) access enabled on the site;
- the content is published (not draft, archived or deleted) and public;
- the author's profile is visible to guests (otherwise remotes cannot fetch the key).

Being discoverable (an actor that can be fetched) is a separate, weaker gate than "may
publish content". Outbound follows, likes and replies need only discoverability, since
the remote must be able to verify the signature.

## Remote accounts as local records

To show remote authors, comments and likes, most platforms create a local "shadow" user
per remote actor:

- Create it only after the activity is authenticated **and** when something will be
  stored (an accepted follow, a reply or like on local content, a post from a followed
  account). Never for strangers, boosts, or Undo/Delete/Update/Accept from unknown actors.
- Make it non-loginable, without email, excluded from local defaults (default groups,
  notifications to admins, directories), with the remote handle as its display identity.
- **Loop guard**: never federate an activity whose local author is a shadow user, or
  inbound interactions echo back out.
- Refresh profiles lazily (on view, at most daily) and on `Update{actor}`.
- Provide a cleanup command for shadow users that no longer have any stored interaction.

## Ids and URLs

- Actor: `https://host/<prefix>/actor/<guid>`; objects under the actor:
  `<actor>/notes/<id>`, `<actor>/comments/<id>`; activities with random suffixes.
- Make object ids dereferenceable (serve the Note on GET with content negotiation) and
  answer 410 after deletion. If they are not, remotes cannot resolve replies or searches.
- `url` points to the platform's normal permalink.

## Inbound content

- Respect addressing: only Public-addressed content may become publicly visible.
- Map remote HTML to the platform's text format with block boundaries and entities
  preserved; render custom emoji where possible; map trailing hashtag blocks to topics if
  the platform has them.
- Attach remote images by copying them (size and type limits) rather than hot-linking,
  if the platform's file handling expects local files.
- Idempotency: one mapping table from AP id to local record (unique on the AP id), used
  for every create, like and delete.

## Display names

A remote user shows as their remote display name with `@user@host` beneath it. Platforms
that let operators customise display names (callbacks, formats) must keep that working
for local users and only override rendering for shadow users.
