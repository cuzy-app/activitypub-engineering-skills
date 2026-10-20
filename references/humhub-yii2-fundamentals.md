# Yii2 fundamentals for HumHub code

HumHub is built on Yii2. These rules come from Yii2 itself and apply unchanged.

## Queries and ActiveRecord

- Bind parameters: `->where(['id' => $id])` or `->andWhere('x = :x', [':x' => $x])`.
  Never interpolate request data into SQL strings.
- Use `->one()` and null checks. A missing row returns null; handle it.
- Wrap multi-step writes in a transaction.

## Validation and input

- Declare `rules()` on every model that accepts input. Use `load()` then `validate()`.
- Treat `Yii::$app->request` values as untrusted.
- Mark attributes safe only through rules, not by assigning arrays blindly.

## Output and security

- Encode output in views (`Html::encode`). Use `Html::*` helpers for attributes.
- Keep CSRF validation on for state-changing requests; use POST for them.
- Check access in controller `behaviors()` (access control filters), not only in views.

## Behaviors, events, dependency injection

- Attach behaviors for reusable model logic; trigger and listen to events for
  loose coupling.
- Use `Yii::$app->get()` components and constructor or property injection rather than
  global state.

## Console and web contexts

Code that runs in console commands and queue jobs has no web session. Do not read
`Yii::$app->user` there; pass identifiers explicitly.
