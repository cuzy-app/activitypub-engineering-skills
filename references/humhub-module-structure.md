# Module structure

A HumHub module is a Yii2 module with a `module.json` manifest and a `config.php`
that registers it. Verify folder names against a current core module.

## Typical layout

```text
mymodule/
  module.json        manifest: id, version, name, description, humhub.minVersion
  composer.json      type "humhub-module", platform PHP version
  config.php         id, class, namespace, events, URL rules
  Module.php         extends the HumHub module base class
  Events.php         static event handlers referenced from config.php
  controllers/
  models/
  migrations/        mYYMMDD_HHMMSS_name.php, class name equals file name
  views/
  widgets/
  resources/         JS, CSS, images served through asset bundles
  messages/          translations per language
  permissions/
  jobs/              queue jobs
  tests/             Codeception tests
```

## module.json

Required by this skill's validator: `id`, `version`, `name`, `description`, and
`humhub.minVersion`. Keep `version` in step with release tags. `humhub.maxVersion`
is optional; the module CI workflows read both bounds when choosing core branches.

## config.php

Returns an array. The keys this skill checks: `id` (must equal `module.json` id),
`class` (the Module class) and `namespace`. Event handlers go in an `events` list,
each entry naming the emitting class, the event constant, and a callback.

## Rules

- The module id is lowercase, stable, and used in translation categories, URLs and
  database table prefixes. Do not rename it after release.
- Use the module's own PHP namespace; keep it identical to the `namespace` entry.
- Do not put business logic in `config.php` or `Events.php`; delegate to services.

Verify: current base-class names and the exact set of recognized `config.php` keys.
