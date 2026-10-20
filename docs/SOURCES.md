# Sources and provenance

Read on 2026-10-20 unless noted. References cite these inline.

## Base skill

- **ActivityPub C2S guide** (`activitypub-c2s`) by UtakataKyosui, listed at
  <https://mcpmarket.com/tools/skills/activitypub-c2s-guide>. Its original repository
  (`UtakataKyosui/C2Lab`) returns 404. Only the 49-line `SKILL.md` survives, mirrored in
  `diegosouzapw/awesome-omni-skill` (`skills/tools/activitypub-c2s/SKILL.md`); its three
  sub-guides (concepts, messaging, activities) and its licence could not be retrieved.
  This skill reuses its **outline** (concepts → messaging and side effects → activity
  types) and its resource list; the text is written independently.

## HumHub material

- The `humhub-*` references, `validate_module.py` and the example module come from a
  HumHub engineering skill skeleton (0.1.0) prepared alongside this skill and merged in
  0.2.0. Several items still carry "Verify" notes and must be checked against the
  installed HumHub core.
- HumHub module coding standards: <https://github.com/humhub/module-coding-standards>
- HumHub core source of the targeted version (`protected/humhub/`) is the authority for
  class names, events and base classes.

## Specifications

- ActivityPub W3C Recommendation: <https://www.w3.org/TR/activitypub/>
- Activity Streams 2.0 Core: <https://www.w3.org/TR/activitystreams-core/>
- Activity Streams Vocabulary: <https://www.w3.org/TR/activitystreams-vocabulary/>
- Hub: <https://activitypub.rocks/>
- NodeInfo protocol: <https://github.com/jhass/nodeinfo/blob/main/PROTOCOL.md>
- WebFinger: RFC 7033; `acct:` URI: RFC 7565; HTTP Message Signatures: RFC 9421;
  Digest fields: RFC 9530
- FEPs: <https://codeberg.org/fediverse/fep>

## Implementation documentation

- Mastodon: <https://docs.joinmastodon.org/spec/activitypub/>,
  <https://docs.joinmastodon.org/spec/security/>, <https://docs.joinmastodon.org/spec/webfinger/>
- Lemmy federation: <https://join-lemmy.org/docs/contributors/05-federation.html>
- Fedify manual: <https://fedify.dev/manual/send>, <https://fedify.dev/manual/inbox>,
  <https://fedify.dev/manual/actor>, <https://fedify.dev/manual/webfinger>,
  <https://fedify.dev/manual/access-control>, <https://fedify.dev/manual/nodeinfo>

## Tools

- fep-mcp: <https://github.com/dahlia/fep-mcp>
- Testing: <https://activitypub-testing.socialweb.coop/implementation-guide/>,
  <https://feditest.org>, <https://browser.pub>
- Guides: <https://socialhub.activitypub.rocks/t/guide-for-new-activitypub-implementers/479>,
  <https://fedidevs.org/>

## Not verified

- Mastodon's future clock-skew allowance, inbox size limit, retry schedule.
- Whether Lemmy rejects documents without `audience`.
- The NodeInfo 2.1 JSON schema's required-field list (from recollection).
- FEP-8fcf reconciliation details (the fetched summary was garbled).
