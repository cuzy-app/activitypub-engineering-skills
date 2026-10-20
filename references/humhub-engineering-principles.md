# Engineering principles and recurring pitfalls

Cross-cutting rules for any HumHub task. Verify version-specific details against the
installed core.

## Principles

1. **Version before advice.** HumHub core APIs, minimum PHP version and UI components
   change between releases. Identify the target from `module.json` and `composer.json`.
2. **Read the installed core.** The authoritative API is the code under
   `protected/humhub/` and `protected/vendor/` of the instance, not memory.
3. **Stay inside the module.** Behaviour changes go through events, behaviors,
   widgets, and configuration.
4. **Prefer existing base classes.** HumHub provides base classes for modules,
   migrations, widgets, jobs, permissions and content models. Use them.
5. **Test the unhappy path.** Permission denied, missing container, empty input,
   and a second run of the same job.

## Recurring pitfalls

1. Editing core or `vendor/` files instead of using an extension point.
2. Changing a released migration. Add a new migration instead.
3. Building SQL by string concatenation. Use parameter binding or the query builder.
4. Reading content or container data without checking the viewer's permission.
5. Assuming a logged-in web user inside a console command or queue job.
6. Hard-coding table names or ids that differ per installation.
7. Using a translation category that does not follow the module's convention,
   so messages are never extracted.
8. Registering assets globally when only one view needs them.
9. Forgetting to guard an event handler against objects of an unexpected type.
10. Declaring support for a core version the module has never been tested against.
11. Echoing user input without encoding it.
12. Starting long-running work inside a web request instead of the queue.
