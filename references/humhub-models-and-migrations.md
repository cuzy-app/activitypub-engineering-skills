# Models and migrations

## Migrations

- File name: `mYYMMDD_HHMMSS_description.php`. The class name must equal the file name.
- Extend HumHub's migration base class so module migrations behave like core ones.
  Verify: whether the installed version offers `safe*` helper methods (for example for
  creating tables and columns idempotently) and prefer them when present.
- Provide `down()` when the change is reversible. If it is not, say so in a comment.
- Never edit a migration that has shipped in a release. Add a new one.
- Keep data migrations separate from schema migrations.
- Name tables with the module id as a prefix to avoid collisions.

## Models

- Extend the ActiveRecord class that matches the data: plain `ActiveRecord` for
  module-private tables, a content record class when the data is user content
  (see [content-and-containers](humhub-content-and-containers.md)).
- Define `tableName()` explicitly, `rules()` for every writable attribute, and
  `attributeLabels()` using the module's translation category.
- Relations are methods (`getAuthor()`); callers use the property (`$model->author`).

## Review checklist

1. Does every migration have a matching, correct `down()` or an explicit comment?
2. Are foreign keys and indexes defined for lookup columns?
3. Are defaults and nullability consistent between migration and `rules()`?
4. Can the migration run twice or on a partially migrated database without damage?
