# Testing and CI

## Tests

- HumHub modules are tested with Codeception, normally from a `tests/` directory in
  the module, against a HumHub core checkout. Verify the config layout in a core
  module before creating new test config.
- Test levels, from cheapest to most expensive:
  1. Static checks (formatting, PHPStan, this skill's validators).
  2. Unit tests of services and models.
  3. Functional tests of controllers and permissions.
  4. Acceptance tests in a browser, only for critical flows.
- Every permission rule needs a "denied" test, not only an "allowed" one.
- Migrations need a test that applies them on a clean database.

## CI

The shared coding-standards repository provides ready-made workflows to copy into
`.github/workflows/`: formatting, weekly Rector pull requests, Codeception against the
`master`, `develop` and `next` core branches and the module's minimum supported version,
and a marketplace upload on release. See
[coding-standards-tooling](humhub-coding-standards-tooling.md).

- Test against the minimum and the newest core version the module claims to support.
- A green run on one core branch is not evidence for the others.
- Some workflows need extra configuration (for example enabling the REST API for
  Codeception); read the workflow header before relying on it.

## Federation tests

For protocol-level fixtures and live interop checks, see
[testing-and-debugging](testing-and-debugging.md).
