# Permissions and events

## Permissions

- Define module permissions as classes extending HumHub's base permission class, with
  an id, title, description and default group states.
- Check permissions through the permission manager of the relevant container, or the
  global permission manager for system-wide permissions.
- Deny by default. A new permission should not grant access to existing users unless
  a migration or default explicitly says so.
- Guard controller actions with access rules; view-only hiding is not protection.

## Events

Register handlers in `config.php`:

```php
'events' => [
    [
        'class' => SomeEmitter::class,
        'event' => SomeEmitter::EVENT_NAME,
        'callback' => [Events::class, 'onEventName'],
    ],
],
```

- Handlers live as static methods on `Events.php` and delegate to services.
- Type-check `$event->sender` and exit early on unexpected types.
- Do not throw from a handler for core events unless you intend to abort the action.
- Verify the event constant exists in the installed core before referencing it.

## Module configuration

Module settings belong in the module's settings component, not in constants. Provide
a configuration form with validation and sensible defaults.
