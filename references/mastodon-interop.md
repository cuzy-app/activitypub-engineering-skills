# Mastodon interoperability

Mastodon is the reference implementation in practice for `Person` and `Note`.

Source: <https://docs.joinmastodon.org/spec/activitypub/> (and /spec/security/, /spec/webfinger/)

## How objects are read

- `Note` becomes a status, `Question` a poll. `Article`, `Page`, `Image`, `Video`, `Event`
  are converted best-effort (`content`, or `name`, with `url` appended). For short social
  posts, emit `Note`.
- `summary` is the content warning; `sensitive: true` hides media (and collapses the post
  behind `summary` if present).
- `inReplyTo` threads; `attributedTo` is the author; `published` the date.
- Visibility comes from addressing plus mentions (table in [concepts](concepts.md)).
  **Mentioned actors must appear in `to`/`cc` and as `Mention` tags.**
- `replies` collection: on discovering a status Mastodon fetches up to 5 same-server
  replies. `likes` and `shares` collections are read for `totalItems` only.

## Tags and attachments

```json
"tag": [
  {"type": "Mention", "href": "https://b.example/users/bob", "name": "@bob@b.example"},
  {"type": "Hashtag", "href": "https://a.example/tags/humhub", "name": "#humhub"},
  {"type": "Emoji", "name": ":blob:", "icon": {"type": "Image", "url": "https://a.example/e/blob.png"}}]
```

- Hashtags are normalised to lowercase with ASCII folding.
- Attachments: `Document` or `Image` with `url`, `mediaType`, `name` (alt text), and
  optionally `blurhash`, `focalPoint [x, y]` in -1..1.
- Custom emoji (`:shortcode:`) also appear in display names; strip them where images
  cannot render.

## HTML

Mastodon keeps `p br a span`, and from 4.2 also `del pre code em strong b i u ul ol li
blockquote`; headings become `<p><strong>`. Classes kept: microformats (`h-*`, `p-*`,
`u-*`, `dt-*`, `e-*`) and `mention hashtag ellipsis invisible`. Link schemes include
http(s), dat, dweb, ipfs, ipns, ssb, gopher, xmpp, magnet, gemini.

Typical markup (Verify: standard Mastodon output, not normative):

```html
<span class="h-card"><a href="https://b.example/@bob" class="u-url mention">@<span>bob</span></a></span>
<a href="https://a.example/tags/humhub" class="mention hashtag" rel="tag">#<span>humhub</span></a>
```

Convert your rich text (Markdown, editor JSON) to this subset before sending. Sanitise
what you receive; never trust remote HTML.

## Activities Mastodon handles

- Statuses: `Create`, `Update`, `Delete`, `Like`, `Announce`, `Undo` (of Like, Announce),
  `Flag`, `QuoteRequest`.
- Accounts: `Follow`, `Accept`, `Reject`, `Undo` (Follow, Accept, Block), `Update`,
  `Delete`, `Block`, `Add`/`Remove` (featured), `Move`, `Flag`.
- Edits: `Update{Note}` with the full object and `updated` set (ignored otherwise).
- Quote posts (4.5+): FEP-044f (`quote`, `QuoteRequest` → `Accept` with a
  `QuoteAuthorization`); Mastodon also reads `quoteUri`, `quoteUrl`, `_misskey_quote`.

## Practical shapes

Verify each against current Mastodon before relying on it:

- `Accept.object` is the Follow id string or the embedded Follow; Mastodon matches the id
  it sent.
- `Undo` embeds the original activity.
- `Delete{Note}` has a `Tombstone {id}` or the id as object; the object URL then 410s.
- `Update{Person}` must have `object.id == actor`; Mastodon may re-fetch the actor.
- Followers synchronisation (FEP-8fcf): Mastodon sends
  `Collection-Synchronization: collectionId="…", url="…", digest="…"`; the digest is the
  XOR of SHA-256 of follower ids on the receiver's domain. Read the FEP before
  implementing reconciliation.

## Authorized fetch

Instances in secure mode (common on larger servers) answer 401 to unsigned GETs. If
following or resolving accounts on one server fails while others work, check signed
fetch first ([http-signatures](http-signatures.md)).
