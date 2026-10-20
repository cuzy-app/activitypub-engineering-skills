# Content and content containers

In HumHub, user-generated content belongs to a **content container**: a Space or a
User profile. Visibility and permissions are evaluated against the container.

## Concepts

- **Content record models** extend a HumHub content ActiveRecord base class and are
  linked to a content entry that stores container, visibility and author.
- **Container models** (Space, User) are the owners. Modules can be enabled per
  container through a container-module base class.
- Queries for content must respect visibility. Prefer HumHub's content query helpers
  over raw joins.

## Rules

- Check `canView`, `canEdit` and similar methods before showing or changing content.
- When creating content, set the container and visibility explicitly; do not rely on
  defaults.
- Do not read content tables directly from another module. Use the public model API.
- Deleting a container must remove or detach module data; handle it through events
  (see [permissions-and-events](humhub-permissions-and-events.md)).

## Verify before use

Exact class names, the required abstract methods on content models, and the
container-module base class differ by version. Open a core module in the installed
instance (for example a small one such as polls or tasks) and mirror it.
