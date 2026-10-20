# Widgets, views, assets, translations

## Views and widgets

- Controllers render views; reusable fragments become widgets extending the HumHub
  widget base class.
- Keep logic out of views. Pass prepared data and encode output.

## Assets and JavaScript

- Register styles and scripts through an asset bundle, from the view or widget that
  needs them.
- HumHub provides a JavaScript module system; define front-end behaviour as a named
  module rather than loose globals. Verify the exact API in the installed version.
- Source files live under the module's `resources/` directory.

## Translations

- Use the module translation category convention, for example
  `Yii::t('MyModuleModule.base', 'Text')`, and keep message files per language under
  `messages/`.
- Do not concatenate translated fragments. Use placeholders.

## Theming

Use the platform's CSS variables and components where available so the module follows
the active theme. Do not hard-code colours.
